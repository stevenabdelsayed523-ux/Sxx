"""Anthropic Claude LLM client implementation."""

from __future__ import annotations

import logging
from typing import AsyncIterator

from anthropic import AsyncAnthropic

from app.config import settings
from app.llm import BaseLLMClient

logger = logging.getLogger(__name__)


class AnthropicClient(BaseLLMClient):
    """Client for Anthropic Claude models."""

    def __init__(self) -> None:
        self._client: AsyncAnthropic | None = None
        self._model = settings.anthropic_model

    def _ensure_client(self) -> AsyncAnthropic:
        if self._client is None:
            self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        return self._client

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> str:
        client = self._ensure_client()
        message = await client.messages.create(
            model=self._model,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return "".join(
            block.text for block in message.content if block.type == "text"
        )

    async def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        client = self._ensure_client()
        async with client.messages.stream(
            model=self._model,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        ) as stream:
            async for text in stream.text_stream:
                yield text

    def count_tokens(self, text: str) -> int:
        # Rough approximation: ~4 chars per token
        return len(text) // 4