"""OpenAI LLM client implementation."""

from __future__ import annotations

import logging
from typing import Any, AsyncIterator

import tiktoken

from openai import AsyncOpenAI

from app.config import settings
from app.llm import BaseLLMClient

logger = logging.getLogger(__name__)


class OpenAIClient(BaseLLMClient):
    """Client for OpenAI GPT models."""

    def __init__(self) -> None:
        self._client: AsyncOpenAI | None = None
        self._model = settings.openai_model
        self._encoder: tiktoken.Encoding | None = None

    def _ensure_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        return self._client

    def _get_encoder(self) -> tiktoken.Encoding:
        if self._encoder is None:
            try:
                self._encoder = tiktoken.encoding_for_model(self._model)
            except Exception:
                self._encoder = tiktoken.get_encoding("cl100k_base")
        return self._encoder

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> str:
        client = self._ensure_client()
        response = await client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    async def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        client = self._ensure_client()
        stream = await client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content

    def count_tokens(self, text: str) -> int:
        encoder = self._get_encoder()
        return len(encoder.encode(text))