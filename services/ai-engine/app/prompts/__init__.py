"""Prompt assembly — builds system + user prompts for each mode."""

from __future__ import annotations

from app.models import DebuggingRequest
from app.prompts.system_prompts import (
    DEBUG_SYSTEM_PROMPT,
    GENERATE_SYSTEM_PROMPT,
    REFACTOR_SYSTEM_PROMPT,
)


def build_generate_prompt(
    prompt: str,
    language: str | None = None,
    code_context: str | None = None,
    file_path: str | None = None,
) -> tuple[str, str]:
    """Build system and user prompts for code generation."""
    system = GENERATE_SYSTEM_PROMPT

    user_parts = []
    if file_path:
        user_parts.append(f"Target file: {file_path}")
    if language:
        user_parts.append(f"Language: {language}")
    if code_context:
        user_parts.append(f"Context:\n```{language or ''}\n{code_context}\n```")
    user_parts.append(f"## Request\n{prompt}")
    user_parts.append(
        "\n## Output format\nProvide your response with code blocks. "
        "Include a brief explanation before each code block."
    )

    return system, "\n\n".join(user_parts)


def build_debug_prompt(
    request: DebuggingRequest,
) -> tuple[str, str]:
    """Build system and user prompts for debugging."""
    system = DEBUG_SYSTEM_PROMPT

    user_parts = []
    if request.file_path:
        user_parts.append(f"File: {request.file_path}")
    if request.language:
        user_parts.append(f"Language: {request.language}")
    if request.error_message:
        user_parts.append(f"Error:\n```\n{request.error_message}\n```")
    if request.code_context:
        user_parts.append(
            f"Code:\n```{request.language or ''}\n{request.code_context}\n```"
        )
    user_parts.append(f"## Issue\n{request.prompt}")
    user_parts.append(
        "\n## Output format\n1. **Root cause** — what's wrong\n"
        "2. **Fix** — the corrected code in a code block\n"
        "3. **Explanation** — why the fix works"
    )

    return system, "\n\n".join(user_parts)


def build_refactor_prompt(
    prompt: str,
    refactor_goal: str | None = None,
    language: str | None = None,
    code_context: str | None = None,
    file_path: str | None = None,
) -> tuple[str, str]:
    """Build system and user prompts for refactoring."""
    system = REFACTOR_SYSTEM_PROMPT

    user_parts = []
    if file_path:
        user_parts.append(f"File: {file_path}")
    if language:
        user_parts.append(f"Language: {language}")
    if code_context:
        user_parts.append(
            f"Code to refactor:\n```{language or ''}\n{code_context}\n```"
        )
    if refactor_goal:
        user_parts.append(f"Refactoring goal: {refactor_goal}")
    user_parts.append(f"## Request\n{prompt}")
    user_parts.append(
        "\n## Output format\n1. **Changes made** — summary of what changed\n"
        "2. **Refactored code** — the improved code in a code block\n"
        "3. **Explanation** — why these changes improve the code"
    )

    return system, "\n\n".join(user_parts)