# CodeMate AI Engine

Core AI service for [CodeMate AI](https://github.com/stevenabdelsayed523-ux/Sxx) — a coding assistant that writes, debugs, and refactors code in real-time.

## Architecture

```
codemate-ai-engine/
├── app/
│   ├── main.py              # FastAPI app with all REST endpoints
│   ├── config.py            # Environment-based configuration
│   ├── models.py            # Pydantic request/response models
│   ├── llm/                 # LLM integration layer
│   │   ├── __init__.py      # Base class + Mock LLM client
│   │   ├── openai_client.py # OpenAI GPT-4 client
│   │   ├── anthropic_client.py # Anthropic Claude client
│   │   └── factory.py       # LLM client factory
│   ├── prompts/
│   │   ├── __init__.py      # Prompt assembly functions
│   │   └── system_prompts.py # System prompts for each mode
│   ├── context/
│   │   └── __init__.py      # Code context management (directory scanning)
│   ├── analysis/
│   │   └── __init__.py      # AST parsing (Python + JS/TS)
│   └── tracking/
│       └── __init__.py      # Code acceptance tracking
├── tests/                   # pytest test suite
├── requirements.txt
├── pyproject.toml
└── README.md
```

## API Endpoints

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |

### Code Generation
| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/generate` | Generate code from natural language |
| POST | `/v1/generate/stream` | Streaming generation via SSE |

### Debugging
| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/debug` | Debug code — explain issues and provide fixes |
| POST | `/v1/debug/stream` | Streaming debugging via SSE |

### Refactoring
| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/refactor` | Refactor code to improve quality |
| POST | `/v1/refactor/stream` | Streaming refactoring via SSE |

### Code Analysis
| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/analyze` | AST analysis of source code |

### Tracking (Code Acceptance KPI)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/tracking/stats` | Overall tracking statistics |
| GET | `/v1/tracking/acceptance-rate` | Code acceptance rate |
| POST | `/v1/tracking/accept/{id}` | Mark suggestion as accepted |
| POST | `/v1/tracking/reject/{id}` | Mark suggestion as rejected |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure LLM provider
cp .env.example .env
# Edit .env with your API keys

# Run with mock provider (no API key needed)
LLM_PROVIDER=mock uvicorn app.main:app --host 0.0.0.0 --port 8000

# Run with OpenAI
# LLM_PROVIDER=openai OPENAI_API_KEY=sk-... uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## LLM Providers

- **OpenAI** — `gpt-4o` (default), configure via `OPENAI_API_KEY` and `OPENAI_MODEL`
- **Anthropic** — `claude-sonnet-4-20250514`, configure via `ANTHROPIC_API_KEY` and `ANTHROPIC_MODEL`
- **Mock** — For testing without API keys (canned responses)

Set `LLM_PROVIDER=openai`, `LLM_PROVIDER=anthropic`, or `LLM_PROVIDER=mock`.

## Example Usage

```python
import httpx

# Generate code
resp = httpx.post("http://localhost:8000/v1/generate", json={
    "mode": "generate",
    "prompt": "Write a Python function to fetch data from an API with retry logic",
    "language": "python",
})
print(resp.json())

# Debug code
resp = httpx.post("http://localhost:8000/v1/debug", json={
    "mode": "debug",
    "prompt": "This crashes on empty input",
    "code_context": "def avg(nums): return sum(nums) / len(nums)",
    "error_message": "ZeroDivisionError: division by zero",
    "language": "python",
})
print(resp.json())

# Stream response
with httpx.stream("POST", "http://localhost:8000/v1/generate/stream", json={
    "mode": "generate",
    "prompt": "Write a React component",
    "language": "typescript",
}) as resp:
    for line in resp.iter_lines():
        if line.startswith("data: "):
            print(line[6:])
```

## Running Tests

```bash
pip install pytest pytest-asyncio httpx
pytest -v
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `openai` | LLM provider: `openai`, `anthropic`, or `mock` |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o` | OpenAI model name |
| `ANTHROPIC_API_KEY` | — | Anthropic API key |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-20250514` | Anthropic model name |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server port |
| `MAX_CONTEXT_CHARS` | `100000` | Max context characters |

## KPI #3 — Code Acceptance Tracking

The tracking module records every AI code suggestion and whether users accept or reject it. This measures the **code-acceptance rate** — a key product KPI.

```bash
# Get overall stats
curl http://localhost:8000/v1/tracking/stats

# Get acceptance rate
curl http://localhost:8000/v1/tracking/acceptance-rate
```