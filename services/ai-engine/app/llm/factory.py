"""LLM client factory — returns the right client based on config."""

from __future__ import annotations

import logging

from app.config import settings
from app.llm import BaseLLMClient, MockLLMClient
from app.llm.anthropic_client import AnthropicClient
from app.llm.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


def get_llm_client(provider: str | None = None) -> BaseLLMClient:
    """Resolve and return the appropriate LLM client.

    Args:
        provider: One of "openai", "anthropic", "mock", or None to use the default.

    Returns:
        An LLM client instance.
    """
    provider = provider or settings.llm_provider

    if provider == "openai":
        logger.info("Using OpenAI client (model=%s)", settings.openai_model)
        return OpenAIClient()
    elif provider == "anthropic":
        logger.info("Using Anthropic client (model=%s)", settings.anthropic_model)
        return AnthropicClient()
    elif provider == "mock":
        logger.info("Using Mock LLM client (for testing)")
        return MockLLMClient()
    else:
        logger.warning("Unknown provider '%s', falling back to openai", provider)
        return OpenAIClient()