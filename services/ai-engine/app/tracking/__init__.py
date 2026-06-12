"""Code acceptance tracking — measures KPI #3 (code-acceptance rate).

Tracks when a user accepts/rejects AI-generated code suggestions so we
can compute the code-acceptance rate.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

_local = threading.local()


def _get_db() -> sqlite3.Connection:
    """Get thread-local SQLite connection."""
    if not hasattr(_local, "conn") or _local.conn is None:
        db_path = Path(settings.tracking_db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        _local.conn = sqlite3.connect(str(db_path))
        _local.conn.row_factory = sqlite3.Row
        _init_db(_local.conn)
    return _local.conn


def _init_db(conn: sqlite3.Connection) -> None:
    """Initialize the tracking schema."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS code_suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            mode TEXT NOT NULL,
            prompt_hash TEXT NOT NULL,
            language TEXT,
            suggestion_length INTEGER,
            accepted INTEGER DEFAULT 0,
            rejected INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            accepted_at TEXT,
            rejected_at TEXT
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_suggestions_session
        ON code_suggestions(session_id)
    """)
    conn.commit()


def record_suggestion(
    session_id: str,
    mode: str,
    prompt_hash: str,
    language: str | None = None,
    suggestion_length: int = 0,
) -> int:
    """Record that a code suggestion was made. Returns the suggestion ID."""
    conn = _get_db()
    now = datetime.now(timezone.utc).isoformat()
    cursor = conn.execute(
        """INSERT INTO code_suggestions
           (session_id, mode, prompt_hash, language, suggestion_length, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (session_id, mode, prompt_hash, language, suggestion_length, now),
    )
    conn.commit()
    return cursor.lastrowid


def mark_accepted(suggestion_id: int) -> None:
    """Mark a suggestion as accepted by the user."""
    conn = _get_db()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE code_suggestions SET accepted = 1, accepted_at = ? WHERE id = ?",
        (now, suggestion_id),
    )
    conn.commit()


def mark_rejected(suggestion_id: int) -> None:
    """Mark a suggestion as rejected by the user."""
    conn = _get_db()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE code_suggestions SET rejected = 1, rejected_at = ? WHERE id = ?",
        (now, suggestion_id),
    )
    conn.commit()


def get_acceptance_rate(session_id: str | None = None) -> float:
    """Get the acceptance rate for a session, or overall if no session given."""
    conn = _get_db()
    if session_id:
        row = conn.execute(
            """SELECT
                   COUNT(*) as total,
                   SUM(accepted) as accepted_count
               FROM code_suggestions
               WHERE session_id = ?""",
            (session_id,),
        ).fetchone()
    else:
        row = conn.execute(
            """SELECT
                   COUNT(*) as total,
                   SUM(accepted) as accepted_count
               FROM code_suggestions"""
        ).fetchone()

    total = row["total"] or 0
    if total == 0:
        return 0.0
    return (row["accepted_count"] or 0) / total


def get_stats() -> dict[str, Any]:
    """Get overall tracking statistics."""
    conn = _get_db()
    total = conn.execute("SELECT COUNT(*) as c FROM code_suggestions").fetchone()["c"]
    accepted = conn.execute(
        "SELECT COUNT(*) as c FROM code_suggestions WHERE accepted = 1"
    ).fetchone()["c"]
    rejected = conn.execute(
        "SELECT COUNT(*) as c FROM code_suggestions WHERE rejected = 1"
    ).fetchone()["c"]
    by_mode = conn.execute(
        """SELECT mode, COUNT(*) as count, SUM(accepted) as accepted
           FROM code_suggestions GROUP BY mode"""
    ).fetchall()

    return {
        "total_suggestions": total,
        "accepted": accepted,
        "rejected": rejected,
        "pending": total - accepted - rejected,
        "acceptance_rate": accepted / total if total > 0 else 0.0,
        "by_mode": [dict(r) for r in by_mode],
    }