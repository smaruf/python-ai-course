#!/usr/bin/env python3
"""
AI Gateway — FastAPI REST Service
==================================

Exposes a single endpoint:

    POST /ai/query
    {
        "prompt": "Your question here"
    }

The gateway internally routes requests through the circuit-breaker router,
preferring the cloud LLM and falling back to the local Ollama instance
when the cloud is unavailable.

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
        "Cloud-first AI query gateway with automatic local-LLM failover. "
        "Implements circuit-breaker pattern for resilient AI access."
    ),
    version="1.0.0",
)

# Build clients from environment variables (with sensible defaults)
_cloud = CloudClient(
    provider=os.getenv("CLOUD_PROVIDER", "openai"),
    model=os.getenv("CLOUD_MODEL", "gpt-4o-mini"),
)
_local = LocalClient(
    model=os.getenv("LOCAL_MODEL", "llama3"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
)
_router = AIRouter(
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
    backend: str = Field(..., description="Which backend answered: 'cloud' or 'local'")
    state: str = Field(..., description="Current circuit-breaker state")


class HealthResponse(BaseModel):
    status: str
    cloud_available: bool
    local_available: bool
    circuit_state: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/ai/query", response_model=QueryResponse, summary="Send a query to the AI")
def ai_query(request: QueryRequest) -> QueryResponse:
    """
    Route the prompt to the best available AI backend.

    - Uses the cloud LLM (e.g. OpenAI) by default.
    - Automatically switches to the local Ollama model if the cloud
      becomes unavailable (circuit breaker opens after 3 consecutive failures).
    - Retries the cloud after a configurable recovery timeout (default 5 min).
    """
    try:
        result = _router.query(request.prompt)
        return QueryResponse(**result)
    except Exception as exc:
        logger.error("All backends failed: %s", exc)
        raise HTTPException(status_code=503, detail=f"All AI backends unavailable: {exc}")


@app.get("/health", response_model=HealthResponse, summary="Gateway health check")
def health() -> HealthResponse:
    """Return the current availability of cloud and local backends."""
    return HealthResponse(
        status="ok",
        cloud_available=_cloud.health_check(),
        local_available=_local.health_check(),
        circuit_state=_router.state,
    )


@app.post("/admin/reset", summary="Reset the circuit breaker")
def reset_circuit() -> dict:
    """Manually reset the circuit breaker to CLOSED (cloud-preferred) state."""
    _router.reset()
    return {"message": "Circuit breaker reset to CLOSED"}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
