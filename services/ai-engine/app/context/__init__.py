"""Context management — allows users to bundle code context with requests."""

from __future__ import annotations

import fnmatch
import logging
import os
from pathlib import Path
from typing import Iterator

from app.config import settings
from app.models import ContextBundle, FileContext

logger = logging.getLogger(__name__)

# Common patterns to ignore when scanning directories
IGNORE_PATTERNS = [
    ".git/**",
    "__pycache__/**",
    "node_modules/**",
    "venv/**",
    ".venv/**",
    "*.pyc",
    "*.pyo",
    ".DS_Store",
    ".env",
    "dist/**",
    "build/**",
    ".next/**",
    "target/**",
]


def _should_ignore(file_path: str) -> bool:
    """Check if a file path matches any ignore pattern."""
    for pattern in IGNORE_PATTERNS:
        if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(
            os.path.basename(file_path), pattern
        ):
            return True
    return False


def _get_language_from_path(file_path: str) -> str | None:
    """Infer programming language from file extension."""
    ext_map = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "jsx",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".rs": "rust",
        ".go": "go",
        ".java": "java",
        ".rb": "ruby",
        ".php": "php",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
        ".r": "r",
        ".sql": "sql",
        ".sh": "bash",
        ".bash": "bash",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".json": "json",
        ".xml": "xml",
        ".md": "markdown",
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
        ".less": "less",
    }
    return ext_map.get(Path(file_path).suffix.lower())


def scan_directory(path: str | Path) -> list[FileContext]:
    """Scan a directory and return all readable source files as FileContext objects.

    Respects ignore patterns and max context size.
    """
    path = Path(path)
    if not path.exists():
        logger.warning("Directory %s does not exist", path)
        return []

    files: list[FileContext] = []
    total_chars = 0

    for file_path in _walk_source_files(path):
        if total_chars >= settings.max_context_chars:
            logger.info("Reached max context size, stopping scan")
            break

        rel_path = str(file_path.relative_to(path))
        language = _get_language_from_path(str(file_path))
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            logger.debug("Skipping unreadable file %s", file_path)
            continue

        # Skip binary-like or huge files
        if len(content) > 50_000:
            logger.debug("Skipping large file %s (%d chars)", file_path, len(content))
            continue

        files.append(FileContext(file_path=rel_path, content=content, language=language))
        total_chars += len(content)

    logger.info("Scanned %d files from %s (%d chars)", len(files), path, total_chars)
    return files


def _walk_source_files(root: Path) -> Iterator[Path]:
    """Walk a directory tree yielding source files, respecting ignore patterns."""
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip ignored directories
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir != "." and _should_ignore(rel_dir + "/"):
            dirnames.clear()
            continue

        # Skip ignored directories in-place
        dirnames[:] = [d for d in dirnames if not _should_ignore(os.path.join(rel_dir, d))]

        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(file_path, root)
            if _should_ignore(rel_path):
                continue
            yield Path(file_path)


def bundle_context(
    directory: str | None = None,
    active_file: str | None = None,
    snippets: list[str] | None = None,
) -> ContextBundle:
    """Build a ContextBundle from optional directory scan + active file + snippets.

    Args:
        directory: Path to scan for source files.
        active_file: Path to the currently active file (read its content).
        snippets: Additional code snippets.

    Returns:
        A ContextBundle ready to send with a request.
    """
    bundle = ContextBundle()

    if directory:
        bundle.files = scan_directory(directory)

    if active_file:
        path = Path(active_file)
        if path.exists():
            content = path.read_text(encoding="utf-8", errors="replace")
            bundle.active_file = FileContext(
                file_path=str(path),
                content=content,
                language=_get_language_from_path(str(path)),
            )

    if snippets:
        bundle.snippets = snippets

    return bundle