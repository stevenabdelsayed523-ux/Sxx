"""Tests for the FastAPI endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
def client():
    """Create an async test client."""
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    """Health check should return ok."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data


@pytest.mark.asyncio
async def test_generate_endpoint(client: AsyncClient):
    """Generate endpoint should return suggestions."""
    resp = await client.post(
        "/v1/generate",
        json={
            "mode": "generate",
            "prompt": "Write a Python function that calculates fibonacci numbers",
            "language": "python",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "generate"
    assert "suggestions" in data
    assert "explanation" in data


@pytest.mark.asyncio
async def test_debug_endpoint(client: AsyncClient):
    """Debug endpoint should return fixes."""
    resp = await client.post(
        "/v1/debug",
        json={
            "mode": "debug",
            "prompt": "This function crashes on empty input",
            "code_context": "def divide(a, b): return a / b",
            "language": "python",
            "error_message": "ZeroDivisionError: division by zero",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "debug"
    assert "suggestions" in data


@pytest.mark.asyncio
async def test_refactor_endpoint(client: AsyncClient):
    """Refactor endpoint should return improvements."""
    resp = await client.post(
        "/v1/refactor",
        json={
            "mode": "refactor",
            "prompt": "Improve this code",
            "code_context": "def f(x): return x * 2",
            "language": "python",
            "refactor_goal": "add type hints",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "refactor"
    assert "suggestions" in data


@pytest.mark.asyncio
async def test_analyze_endpoint(client: AsyncClient):
    """Analyze endpoint should parse code structure."""
    code = """
def hello(name: str) -> str:
    return f"Hello, {name}!"

class Greeter:
    def greet(self, name: str) -> str:
        return hello(name)
"""
    resp = await client.post(
        "/v1/analyze",
        params={"code": code, "language": "python"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["language"] == "python"
    assert len(data["functions"]) > 0
    assert any(f["name"] == "hello" for f in data["functions"])


@pytest.mark.asyncio
async def test_generate_streaming(client: AsyncClient):
    """Streaming endpoint should return SSE events."""
    async with client.stream(
        "POST",
        "/v1/generate/stream",
        json={
            "mode": "generate",
            "prompt": "Write a simple Python function",
            "language": "python",
        },
    ) as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_tracking_stats(client: AsyncClient):
    """Tracking stats should return valid data."""
    resp = await client.get("/v1/tracking/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_suggestions" in data
    assert "acceptance_rate" in data


@pytest.mark.asyncio
async def test_invalid_payload(client: AsyncClient):
    """Invalid requests should return 422."""
    resp = await client.post(
        "/v1/generate",
        json={"mode": "generate"},  # missing 'prompt'
    )
    assert resp.status_code == 422