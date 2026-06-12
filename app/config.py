"""Application configuration — loads from environment variables with sensible defaults."""

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    # LLM provider: "openai", "anthropic", or "mock" (for testing)
    llm_provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "openai"))

    # OpenAI
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o"))

    # Anthropic
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    anthropic_model: str = field(default_factory=lambda: os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"))

    # Server
    host: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "8000")))

    # Max context length (approx characters)
    max_context_chars: int = field(default_factory=lambda: int(os.getenv("MAX_CONTEXT_CHARS", "100000")))

    # Code acceptance tracking DB path
    tracking_db_path: str = field(default_factory=lambda: os.getenv("TRACKING_DB_PATH", "data/tracking.db"))


settings = Settings()