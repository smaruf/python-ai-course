#!/usr/bin/env python3
"""
AI Gateway — FastAPI REST Service
==================================

Exposes a single endpoint:

    POST /ai/query
    {
        "prompt": "Your question here"
    }

The gateway routes requests through a 3-tier circuit-breaker:

  Tier 1 (primary)   : GitHub Copilot
  Tier 2 (secondary) : Cloud LLM (e.g. OpenAI)
  Tier 3 (fallback)  : Local Ollama

Usage:
    uvicorn ai_gateway:app --host 0.0.0.0 --port 8000 --reload

VS Code / GitHub Copilot:
    Open this project folder in VS Code — Copilot will auto-complete
    based on the patterns defined here. See .vscode/settings.json for
    recommended settings.
"""

import logging
import os
import sys

# Allow running from the project root without installing the package
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from copilot_client import CopilotClient
from cloud_client import CloudClient
from local_client import LocalClient
from router import AIRouter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AI Gateway",
    description=(
        "3-tier AI query gateway: GitHub Copilot (primary) → Cloud LLM (secondary) "
        "→ Local Ollama (fallback). Implements per-tier circuit-breaker pattern."
    ),
    version="2.0.0",
)

# Build clients from environment variables (with sensible defaults)
_copilot = CopilotClient(
    model=os.getenv("COPILOT_MODEL", "gpt-4o"),
)
_cloud = CloudClient(
    provider=os.getenv("CLOUD_PROVIDER", "openai"),
    model=os.getenv("CLOUD_MODEL", "gpt-4o-mini"),
)
_local = LocalClient(
    model=os.getenv("LOCAL_MODEL", "llama3"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
)
_router = AIRouter(
    copilot=_copilot,
    cloud=_cloud,
    local=_local,
    failure_threshold=int(os.getenv("FAILURE_THRESHOLD", "3")),
    recovery_timeout=int(os.getenv("RECOVERY_TIMEOUT", "300")),
)


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="The question or instruction for the AI")


class QueryResponse(BaseModel):
    response: str = Field(..., description="The AI model's answer")
    backend: str = Field(..., description="Which backend answered: 'copilot', 'cloud', or 'local'")
    state: str = Field(..., description="Primary (Copilot) circuit-breaker state")


class HealthResponse(BaseModel):
    status: str
    copilot_available: bool
    cloud_available: bool
    local_available: bool
    circuit_state: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/ai/query", response_model=QueryResponse, summary="Send a query to the AI")
def ai_query(request: QueryRequest) -> QueryResponse:
    """
    Route the prompt through the 3-tier failover chain.

    - Tries GitHub Copilot first (primary).
    - Falls back to OpenAI / cloud LLM if Copilot is unavailable.
    - Falls back to local Ollama if both cloud tiers are unavailable.
    - Each cloud tier has an independent circuit breaker that opens after
      N consecutive failures and re-probes after a configurable timeout.
    """
    try:
        result = _router.query(request.prompt)
        return QueryResponse(**result)
    except Exception as exc:
        logger.error("All backends failed: %s", exc)
        raise HTTPException(status_code=503, detail=f"All AI backends unavailable: {exc}")


@app.get("/health", response_model=HealthResponse, summary="Gateway health check")
def health() -> HealthResponse:
    """Return the current availability of all three backends."""
    return HealthResponse(
        status="ok",
        copilot_available=_copilot.health_check(),
        cloud_available=_cloud.health_check(),
        local_available=_local.health_check(),
        circuit_state=_router.state,
    )


@app.post("/admin/reset", summary="Reset all circuit breakers")
def reset_circuit() -> dict:
    """Manually reset all circuit breakers to CLOSED (Copilot-preferred) state."""
    _router.reset()
    return {"message": "All circuit breakers reset to CLOSED"}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
