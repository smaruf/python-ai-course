#!/usr/bin/env python3
"""
AI Gateway — FastAPI REST Service
==================================

Endpoints:

    POST /ai/query
    {
        "prompt": "Your question here"
    }

    POST /ai/query/rag
    {
        "prompt": "Your question here",
        "documents": ["Context chunk 1", "Context chunk 2", ...]
    }

The gateway routes requests through a 3-tier circuit-breaker:

  Tier 1 (primary)   : GitHub Copilot
  Tier 2 (secondary) : Cloud LLM (e.g. OpenAI)
  Tier 3 (fallback)  : Local Ollama

The RAG endpoint prepends the supplied context documents to the prompt
(simple context injection — no GPU, no vector store required).

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
from typing import List

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
        "→ Local Ollama (fallback). Implements per-tier circuit-breaker pattern. "
        "Supports plain queries and RAG (context-augmented) queries. "
        "Language-agnostic REST API — usable from Python, Java, C#, Go, or any HTTP client."
    ),
    version="2.1.0",
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


class RAGRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="The question or instruction for the AI")
    documents: List[str] = Field(
        ...,
        min_length=1,
        description="Context documents to augment the prompt (text chunks / passages)",
    )
    max_context_chars: int = Field(
        default=4000,
        ge=100,
        le=16000,
        description=(
            "Maximum total characters of context to inject before the prompt. "
            "Keeps the request within model context limits."
        ),
    )


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
# Helpers
# ---------------------------------------------------------------------------

def _build_rag_prompt(prompt: str, documents: List[str], max_context_chars: int) -> str:
    """
    Build a RAG-augmented prompt by prepending context documents.

    Concatenates documents (separated by '---') up to *max_context_chars*
    so the total context fits within typical model limits without a GPU or
    vector store.
    """
    separator = "\n---\n"
    context_parts: List[str] = []
    total = 0
    for doc in documents:
        chunk = doc.strip()
        if not chunk:
            continue
        needed = len(chunk) + (len(separator) if context_parts else 0)
        if total + needed > max_context_chars:
            # Include as much of this chunk as fits, then stop
            remaining = max_context_chars - total - (len(separator) if context_parts else 0)
            if remaining > 0:
                context_parts.append(chunk[:remaining])
            break
        context_parts.append(chunk)
        total += needed

    context = separator.join(context_parts)
    return f"Context:\n{context}\n\nQuestion: {prompt}"


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


@app.post("/ai/query/rag", response_model=QueryResponse, summary="RAG-augmented query")
def ai_query_rag(request: RAGRequest) -> QueryResponse:
    """
    Answer a question grounded in the supplied context documents (RAG).

    The gateway prepends the provided text chunks to the prompt before
    routing through the same 3-tier failover chain.  No GPU, embeddings
    model, or vector database is required — making it suitable for a
    single laptop environment.

    **Example use cases**
    - Chat over a local code-base snippet
    - Answer questions about a pasted document
    - Ground responses in retrieved database rows
    """
    augmented_prompt = _build_rag_prompt(
        request.prompt, request.documents, request.max_context_chars
    )
    try:
        result = _router.query(augmented_prompt)
        return QueryResponse(**result)
    except Exception as exc:
        logger.error("All backends failed (RAG): %s", exc)
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
