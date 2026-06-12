"""Abstract base class for LLM clients."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator


class BaseLLMClient(ABC):
    """Abstract LLM client — implementations for OpenAI, Anthropic, etc."""

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> str:
        """Synchronous (non-streaming) completion. Returns full text."""
        ...

    @abstractmethod
    async def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Streaming completion. Yields text chunks as they arrive."""
        ...

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Approximate token count for the given text."""
        ...


class MockLLMClient(BaseLLMClient):
    """Mock client for testing — returns canned responses."""

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> str:
        return f"# Mock response\n\n## System used\n{system_prompt[:100]}...\n\n## User asked\n{user_prompt[:200]}..."

    async def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        yield f"# Mock response\n\n"
        yield f"Based on your request, here's the generated code:\n\n"
        yield f"```python\ndef hello():\n    print('Hello, World!')\n```\n"

    def count_tokens(self, text: str) -> int:
        return len(text) // 4