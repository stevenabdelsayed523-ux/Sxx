"""Main FastAPI application — API entry point for the CodeMate AI engine."""

from __future__ import annotations

import hashlib
import logging
import uuid
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from app.config import settings
from app.llm.factory import get_llm_client
from app.models import (
    AnalysisResult,
    CodeGenerationRequest,
    CodeResponse,
    CodeSuggestion,
    DebuggingRequest,
    RefactoringRequest,
)
from app.prompts import build_debug_prompt, build_generate_prompt, build_refactor_prompt
from app.tracking import (
    get_acceptance_rate,
    get_stats,
    mark_accepted,
    mark_rejected,
    record_suggestion,
)
from app.analysis import analyze_code

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("CodeMate AI Engine starting up...")
    logger.info("LLM Provider: %s", settings.llm_provider)
    yield
    logger.info("CodeMate AI Engine shutting down...")


app = FastAPI(
    title="CodeMate AI Engine",
    description="Core AI service for CodeMate AI — code generation, debugging, and refactoring.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helper ──────────────────────────────────────────────────────

def _parse_code_blocks(text: str) -> list[CodeSuggestion]:
    """Parse markdown code blocks from LLM response into structured suggestions."""
    import re

    suggestions: list[CodeSuggestion] = []
    blocks = re.split(r"(```)", text)

    in_block = False
    current_lines = []
    current_lang = None

    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            if not in_block:
                # Start of code block
                lang = line[3:].strip() or None
                current_lang = lang
                current_lines = []
                in_block = True
            else:
                # End of code block
                code = "\n".join(current_lines)
                if code.strip():
                    suggestions.append(
                        CodeSuggestion(code=code, language=current_lang)
                    )
                current_lines = []
                current_lang = None
                in_block = False
        elif in_block:
            current_lines.append(line)
        i += 1

    return suggestions


def _extract_explanation(text: str) -> str:
    """Extract explanation text (everything outside code blocks)."""
    import re

    parts = re.split(r"```[\w]*\n.*?```", text, flags=re.DOTALL)
    return "\n".join(p.strip() for p in parts if p.strip())


# ── API Endpoints ───────────────────────────────────────────────

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0", "provider": settings.llm_provider}


@app.post("/v1/generate", response_model=CodeResponse)
async def generate_code(request: CodeGenerationRequest):
    """Generate code from a natural language description."""
    session_id = str(uuid.uuid4())
    provider = request.provider if request.provider != "auto" else None

    try:
        client = get_llm_client(provider)
        system_prompt, user_prompt = build_generate_prompt(
            prompt=request.prompt,
            language=request.language,
            code_context=request.code_context,
            file_path=request.file_path,
        )

        prompt_hash = hashlib.sha256(user_prompt.encode()).hexdigest()[:12]
        response_text = await client.generate(system_prompt=system_prompt, user_prompt=user_prompt)

        suggestions = _parse_code_blocks(response_text)
        explanation = _extract_explanation(response_text)

        # Track the suggestion
        for s in suggestions:
            record_suggestion(
                session_id=session_id,
                mode="generate",
                prompt_hash=prompt_hash,
                language=request.language,
                suggestion_length=len(s.code),
            )

        provider_used = provider or settings.llm_provider
        return CodeResponse.from_suggestions(
            mode="generate",
            suggestions=suggestions,
            explanation=explanation,
            provider_used=provider_used,
        )
    except Exception as e:
        logger.exception("Code generation failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/generate/stream")
async def generate_code_stream(request: CodeGenerationRequest):
    """Generate code with SSE streaming response."""
    provider = request.provider if request.provider != "auto" else None
    client = get_llm_client(provider)
    system_prompt, user_prompt = build_generate_prompt(
        prompt=request.prompt,
        language=request.language,
        code_context=request.code_context,
        file_path=request.file_path,
    )

    async def event_generator() -> AsyncIterator[dict]:
        yield {"event": "start", "data": '{"mode": "generate"}'}
        full_text = ""
        async for chunk in client.generate_stream(
            system_prompt=system_prompt, user_prompt=user_prompt
        ):
            full_text += chunk
            yield {"event": "chunk", "data": chunk}
        yield {"event": "done", "data": full_text}

    return EventSourceResponse(event_generator())


@app.post("/v1/debug", response_model=CodeResponse)
async def debug_code(request: DebuggingRequest):
    """Debug code — explain issues and provide fixes."""
    session_id = str(uuid.uuid4())
    provider = request.provider if request.provider != "auto" else None

    try:
        client = get_llm_client(provider)
        system_prompt, user_prompt = build_debug_prompt(request)

        prompt_hash = hashlib.sha256(user_prompt.encode()).hexdigest()[:12]
        response_text = await client.generate(system_prompt=system_prompt, user_prompt=user_prompt)

        suggestions = _parse_code_blocks(response_text)
        explanation = _extract_explanation(response_text)

        for s in suggestions:
            record_suggestion(
                session_id=session_id,
                mode="debug",
                prompt_hash=prompt_hash,
                language=request.language,
                suggestion_length=len(s.code),
            )

        provider_used = provider or settings.llm_provider
        return CodeResponse.from_suggestions(
            mode="debug",
            suggestions=suggestions,
            explanation=explanation,
            provider_used=provider_used,
        )
    except Exception as e:
        logger.exception("Debugging failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/debug/stream")
async def debug_code_stream(request: DebuggingRequest):
    """Debug code with SSE streaming response."""
    provider = request.provider if request.provider != "auto" else None
    client = get_llm_client(provider)
    system_prompt, user_prompt = build_debug_prompt(request)

    async def event_generator() -> AsyncIterator[dict]:
        yield {"event": "start", "data": '{"mode": "debug"}'}
        full_text = ""
        async for chunk in client.generate_stream(
            system_prompt=system_prompt, user_prompt=user_prompt
        ):
            full_text += chunk
            yield {"event": "chunk", "data": chunk}
        yield {"event": "done", "data": full_text}

    return EventSourceResponse(event_generator())


@app.post("/v1/refactor", response_model=CodeResponse)
async def refactor_code(request: RefactoringRequest):
    """Refactor existing code to improve quality without changing behavior."""
    session_id = str(uuid.uuid4())
    provider = request.provider if request.provider != "auto" else None

    try:
        client = get_llm_client(provider)
        system_prompt, user_prompt = build_refactor_prompt(
            prompt=request.prompt,
            refactor_goal=request.refactor_goal,
            language=request.language,
            code_context=request.code_context,
            file_path=request.file_path,
        )

        prompt_hash = hashlib.sha256(user_prompt.encode()).hexdigest()[:12]
        response_text = await client.generate(system_prompt=system_prompt, user_prompt=user_prompt)

        suggestions = _parse_code_blocks(response_text)
        explanation = _extract_explanation(response_text)

        for s in suggestions:
            record_suggestion(
                session_id=session_id,
                mode="refactor",
                prompt_hash=prompt_hash,
                language=request.language,
                suggestion_length=len(s.code),
            )

        provider_used = provider or settings.llm_provider
        return CodeResponse.from_suggestions(
            mode="refactor",
            suggestions=suggestions,
            explanation=explanation,
            provider_used=provider_used,
        )
    except Exception as e:
        logger.exception("Refactoring failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/refactor/stream")
async def refactor_code_stream(request: RefactoringRequest):
    """Refactor code with SSE streaming response."""
    provider = request.provider if request.provider != "auto" else None
    client = get_llm_client(provider)
    system_prompt, user_prompt = build_refactor_prompt(
        prompt=request.prompt,
        refactor_goal=request.refactor_goal,
        language=request.language,
        code_context=request.code_context,
        file_path=request.file_path,
    )

    async def event_generator() -> AsyncIterator[dict]:
        yield {"event": "start", "data": '{"mode": "refactor"}'}
        full_text = ""
        async for chunk in client.generate_stream(
            system_prompt=system_prompt, user_prompt=user_prompt
        ):
            full_text += chunk
            yield {"event": "chunk", "data": chunk}
        yield {"event": "done", "data": full_text}

    return EventSourceResponse(event_generator())


@app.post("/v1/analyze", response_model=AnalysisResult)
async def analyze_code_endpoint(code: str, language: str = "python"):
    """Analyze source code using AST parsing.

    Returns extracted functions, classes, imports, and any syntax errors.
    """
    try:
        result = analyze_code(code, language)
        return result
    except Exception as e:
        logger.exception("Code analysis failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/tracking/stats")
async def tracking_stats():
    """Get code acceptance tracking statistics."""
    return get_stats()


@app.get("/v1/tracking/acceptance-rate")
async def acceptance_rate(session_id: str | None = None):
    """Get the code acceptance rate."""
    rate = get_acceptance_rate(session_id)
    return {"acceptance_rate": rate, "session_id": session_id}


@app.post("/v1/tracking/accept/{suggestion_id}")
async def accept_suggestion(suggestion_id: int):
    """Mark a suggestion as accepted."""
    mark_accepted(suggestion_id)
    return {"status": "accepted", "suggestion_id": suggestion_id}


@app.post("/v1/tracking/reject/{suggestion_id}")
async def reject_suggestion(suggestion_id: int):
    """Mark a suggestion as rejected."""
    mark_rejected(suggestion_id)
    return {"status": "rejected", "suggestion_id": suggestion_id}