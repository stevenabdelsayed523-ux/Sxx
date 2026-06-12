"""Pydantic models for the AI engine API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


# ── Request models ──────────────────────────────────────────────

class CodeRequest(BaseModel):
    """Base request for all AI code operations."""
    prompt: str = Field(..., description="The user's natural language request or code question.")
    code_context: str | None = Field(None, description="Optional surrounding code for context.")
    language: str | None = Field(None, description="Target programming language (e.g. 'python', 'javascript').")
    file_path: str | None = Field(None, description="Path hint for the file being edited.")
    provider: Literal["auto", "openai", "anthropic"] = Field("auto", description="LLM provider preference.")


class CodeGenerationRequest(CodeRequest):
    """Request for generating new code from a natural language description."""
    mode: Literal["generate"] = "generate"


class DebuggingRequest(CodeRequest):
    """Request for debugging — explain and fix broken code."""
    mode: Literal["debug"] = "debug"
    error_message: str | None = Field(None, description="Error message or stack trace, if available.")


class RefactoringRequest(CodeRequest):
    """Request for refactoring existing code."""
    mode: Literal["refactor"] = "refactor"
    refactor_goal: str | None = Field(None, description="Specific refactoring goal (e.g. 'extract function', 'add types').")


# ── Response models ─────────────────────────────────────────────

class CodeSuggestion(BaseModel):
    """A single code suggestion block."""
    code: str = Field(..., description="The generated/fixed/refactored code.")
    explanation: str = Field("", description="Explanation of the change.")
    language: str | None = Field(None, description="Detected code language.")
    line_start: int | None = Field(None, description="Suggested insertion line start.")
    line_end: int | None = Field(None, description="Suggested insertion line end.")


class CodeResponse(BaseModel):
    """Response from any AI code operation."""
    mode: str
    suggestions: list[CodeSuggestion] = Field(default_factory=list)
    explanation: str = Field("", description="Overall explanation or summary.")
    token_usage: dict[str, int] = Field(default_factory=dict)
    provider_used: str = ""

    @classmethod
    def from_suggestions(
        cls,
        mode: str,
        suggestions: list[CodeSuggestion],
        explanation: str = "",
        token_usage: dict[str, int] | None = None,
        provider_used: str = "",
    ) -> CodeResponse:
        return cls(
            mode=mode,
            suggestions=suggestions,
            explanation=explanation,
            token_usage=token_usage or {},
            provider_used=provider_used,
        )


# ── Context / Analysis models ───────────────────────────────────

class FileContext(BaseModel):
    """Represents a file in the user's codebase context."""
    file_path: str
    content: str
    language: str | None = None


class ContextBundle(BaseModel):
    """Aggregated context sent with a request."""
    files: list[FileContext] = Field(default_factory=list)
    active_file: FileContext | None = None
    snippets: list[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    """Result of AST/code analysis."""
    language: str
    functions: list[dict[str, Any]] = Field(default_factory=list)
    classes: list[dict[str, Any]] = Field(default_factory=list)
    imports: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)