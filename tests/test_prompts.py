"""Tests for prompt templates."""

from __future__ import annotations

from app.prompts import build_generate_prompt, build_debug_prompt, build_refactor_prompt
from app.models import DebuggingRequest


def test_generate_prompt_includes_language():
    """Generation prompt should mention the target language."""
    system, user = build_generate_prompt(
        prompt="Write a sort function",
        language="python",
    )
    assert "python" in user.lower()
    assert "sort" in user


def test_generate_prompt_includes_context():
    """Generation prompt should include code context."""
    system, user = build_generate_prompt(
        prompt="Add error handling",
        code_context="def divide(a, b): return a / b",
        language="python",
    )
    assert "divide" in user
    assert "error handling" in user


def test_debug_prompt_includes_error():
    """Debug prompt should include the error message."""
    request = DebuggingRequest(
        mode="debug",
        prompt="Fix this function",
        code_context="def f(x): return 1/x",
        error_message="ZeroDivisionError",
        language="python",
    )
    system, user = build_debug_prompt(request)
    assert "ZeroDivisionError" in user
    assert "Root cause" in user


def test_refactor_prompt_includes_goal():
    """Refactor prompt should include the refactoring goal."""
    system, user = build_refactor_prompt(
        prompt="Improve naming",
        refactor_goal="Use more descriptive variable names",
        code_context="def f(x, y): return x + y",
        language="python",
    )
    assert "descriptive" in user.lower()
    assert "f(x, y)" in user


def test_refactor_prompt_format():
    """Refactor prompt should specify output format."""
    system, user = build_refactor_prompt(
        prompt="Optimize this",
        code_context="for i in range(10): print(i)",
    )
    assert "Changes made" in user
    assert "Refactored code" in user
    assert "Explanation" in user