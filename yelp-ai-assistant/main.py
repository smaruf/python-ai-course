"""
Yelp-Style AI Assistant — FastAPI Application
=============================================

Implements the API contract from TDD §9:

  POST /assistant/query
  GET  /health
  GET  /health/detailed

Architecture flow (TDD §2.1):
  Query → Cache check → Intent Classification → Query Routing
        → Circuit-broken multi-source Search (parallel, with timeouts)
        → Answer Orchestration → LLM (RAG) → Cache store → Response

High-concurrency design (100k+ users):
  - Two-tier L1+L2 (Redis) query cache — most popular queries served < 10 ms
  - Per-service circuit breakers prevent cascade failures
  - asyncio.wait_for timeouts per service (structured 40 ms, vector 80 ms,
    LLM 1 000 ms) with graceful structured-only fallback
  - Named concurrency semaphores cap in-flight vector/LLM calls
  - X-Correlation-ID propagation for distributed tracing
  - Parallel search via asyncio.gather across all three services
"""

from __future__ import annotations

import asyncio
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from src.cache.cache_layer import QueryCache
from src.intent.classifier import IntentClassifier
from src.models.schemas import (
    BusinessData,
    BusinessHours,
    Photo,
    QueryRequest,
    QueryResponse,
    Review,
)
from src.orchestration.orchestrator import AnswerOrchestrator
from src.rag.rag_service import RAGService
from src.resilience.circuit_breaker import CircuitBreaker, ConcurrencyLimiter, with_timeout
from src.routing.router import QueryRouter
from src.search.services import (
    PhotoHybridRetrievalService,
    ReviewVectorSearchService,
    StructuredSearchService,
)


# ---------------------------------------------------------------------------
# Service singletons (dependency-injection friendly)
# ---------------------------------------------------------------------------

structured_service = StructuredSearchService()
review_service = ReviewVectorSearchService()
photo_service = PhotoHybridRetrievalService()
intent_classifier = IntentClassifier()
query_router = QueryRouter()
orchestrator = AnswerOrchestrator()
rag_service = RAGService(use_mock=True)

# Cache (L1 in-process + L2 Redis)
query_cache = QueryCache()

# Per-service circuit breakers
_cb_structured = CircuitBreaker("structured_search", failure_threshold=5, recovery_timeout=30.0)
_cb_review = CircuitBreaker("review_vector_search", failure_threshold=5, recovery_timeout=30.0)
_cb_photo = CircuitBreaker("photo_hybrid_search", failure_threshold=5, recovery_timeout=30.0)
_cb_llm = CircuitBreaker("llm_rag", failure_threshold=3, recovery_timeout=60.0)

# Concurrency limiters — prevent thundering-herd on expensive resources
_sem_vector = ConcurrencyLimiter("vector_search", max_concurrent=200)
_sem_llm = ConcurrencyLimiter("llm", max_concurrent=50)

# Service timeouts (seconds) — from TDD §8.2 latency budget
_TIMEOUT_STRUCTURED: float = 0.040   # 40 ms
_TIMEOUT_VECTOR: float = 0.080       # 80 ms
_TIMEOUT_LLM: float = 1.000          # 1 000 ms


def _seed_demo_data() -> None:
    """Populate demo business data so the API works out of the box."""
    biz = BusinessData(
        business_id="12345",
        name="The Rustic Table",
        address="123 Main St, New York, NY 10001",
        phone="+1-212-555-0100",
        price_range="$$",
        hours=[
            BusinessHours("monday", "09:00", "22:00"),
            BusinessHours("tuesday", "09:00", "22:00"),
            BusinessHours("wednesday", "09:00", "22:00"),
            BusinessHours("thursday", "09:00", "22:00"),
            BusinessHours("friday", "09:00", "23:00"),
            BusinessHours("saturday", "10:00", "23:00"),
            BusinessHours("sunday", "10:00", "21:00"),
        ],
        amenities={
            "heated_patio": True,
            "parking": False,
            "wifi": True,
            "wheelchair_accessible": True,
        },
        categories=["American", "Brunch", "Bar"],
        rating=4.3,
        review_count=215,
    )
    structured_service.add_business(biz)

    reviews = [
        Review(
            review_id="r1",
            business_id="12345",
            user_id="u1",
            rating=5.0,
            text="Amazing heated patio — perfect for winter evenings. Great cocktails too!",
        ),
        Review(
            review_id="r2",
            business_id="12345",
            user_id="u2",
            rating=4.0,
            text="Lovely atmosphere for a date night. The food was excellent.",
        ),
        Review(
            review_id="r3",
            business_id="12345",
            user_id="u3",
            rating=3.5,
            text="Good for groups. Parking nearby is tricky on weekends.",
        ),
    ]
    for r in reviews:
        review_service.add_review(r)

    photos = [
        Photo(
            photo_id="p1",
            business_id="12345",
            url="https://example.com/photos/rustic-patio-1.jpg",
            caption="Outdoor heated patio with string lights in winter",
        ),
        Photo(
            photo_id="p2",
            business_id="12345",
            url="https://example.com/photos/rustic-interior.jpg",
            caption="Cozy interior with rustic wooden decor",
        ),
    ]
    for p in photos:
        photo_service.add_photo(p)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    await query_cache.connect()
    _seed_demo_data()
    print("🚀 Yelp-Style AI Assistant API started")
    print("📖 Docs: http://localhost:8000/docs")
    yield
    await query_cache.close()
    print("👋 Shutting down AI Assistant API")


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Yelp-Style AI Assistant",
    description=(
        "Production-grade AI assistant for real-time business queries.\n\n"
        "Features:\n"
        "- Intent classification (operational / amenity / quality / photo)\n"
        "- Hybrid freshness data ingestion\n"
        "- Structured + unstructured data separation\n"
        "- Hybrid photo retrieval (caption + embeddings)\n"
        "- Retrieval-Augmented Generation (RAG)\n"
        "- Two-tier L1+L2 Redis cache (5–30 min TTL)\n"
        "- Per-service circuit breakers + timeout fallbacks\n"
        "- Concurrency-limited LLM/vector calls for 100k+ scale"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Correlation-ID middleware
# ---------------------------------------------------------------------------

@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next) -> Response:
    """Attach X-Correlation-ID to every request and response for tracing."""
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    response: Response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Liveness probe."""
    return {
        "status": "healthy",
        "service": "yelp-ai-assistant",
        "version": "1.0.0",
    }


@app.get("/health/detailed", tags=["Health"])
async def health_detailed() -> Dict[str, Any]:
    """Detailed readiness probe — reports circuit breaker states and cache size."""
    return {
        "status": "healthy",
        "service": "yelp-ai-assistant",
        "version": "1.0.0",
        "circuit_breakers": {
            "structured_search": _cb_structured.state,
            "review_vector_search": _cb_review.state,
            "photo_hybrid_search": _cb_photo.state,
            "llm_rag": _cb_llm.state,
        },
        "cache": {
            "l1_entries": query_cache.l1_size(),
        },
        "concurrency": {
            "vector_slots_available": _sem_vector.available,
            "llm_slots_available": _sem_llm.available,
        },
    }


@app.post("/assistant/query", response_model=QueryResponse, tags=["Assistant"])
async def query_assistant(request: QueryRequest) -> QueryResponse:
    """
    Answer a natural-language query about a business.

    High-concurrency flow:
      1. L1/L2 cache check — returns < 10 ms on hit
      2. Intent classification (< 20 ms)
      3. Query routing decision
      4. Parallel circuit-broken searches with per-service timeouts:
           - Structured: 40 ms  (authoritative; fallback = [])
           - Review vec: 80 ms  (anecdotal;  fallback = [])
           - Photo:       80 ms  (visual;     fallback = [])
      5. Answer orchestration + conflict resolution
      6. LLM / RAG call with 1 000 ms timeout + concurrency cap
      7. Store result in cache
    """
    wall_start = time.monotonic()

    # 1. Cache check
    cached = await query_cache.get_query_result(request.business_id, request.query)
    if cached is not None:
        return QueryResponse(**cached)

    # 2. Intent classification (target < 20 ms)
    intent, _confidence, _cls_ms = intent_classifier.classify(request.query)

    # 3. Routing decision
    decision = query_router.decide(intent)

    # 4. Parallel searches with circuit breakers + timeouts
    async def _structured_search():
        return await _cb_structured.call(
            with_timeout,
            structured_service.search(request.query, request.business_id),
            _TIMEOUT_STRUCTURED,
            [],
            "structured_search",
            fallback=[],
        )

    async def _review_search():
        async with _sem_vector:
            return await _cb_review.call(
                with_timeout,
                review_service.search(request.query, request.business_id),
                _TIMEOUT_VECTOR,
                [],
                "review_vector_search",
                fallback=[],
            )

    async def _photo_search():
        async with _sem_vector:
            return await _cb_photo.call(
                with_timeout,
                photo_service.search(request.query, request.business_id),
                _TIMEOUT_VECTOR,
                [],
                "photo_hybrid_search",
                fallback=[],
            )

    coros = []
    if decision.use_structured:
        coros.append(_structured_search())
    else:
        coros.append(_noop([]))

    if decision.use_review_vector:
        coros.append(_review_search())
    else:
        coros.append(_noop([]))

    if decision.use_photo_hybrid:
        coros.append(_photo_search())
    else:
        coros.append(_noop([]))

    try:
        structured_results, review_results, photo_results = await asyncio.gather(*coros)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Search error: {exc}") from exc

    # Build RoutedResults for the orchestrator
    from src.routing.router import RoutedResults
    routed = RoutedResults(
        decision=decision,
        structured_results=structured_results or [],
        review_results=review_results or [],
        photo_results=photo_results or [],
    )

    # 5. Orchestrate evidence
    bundle = orchestrator.orchestrate(routed)

    # 6. LLM / RAG with concurrency cap + circuit breaker + timeout
    async def _llm_call():
        async with _sem_llm:
            return await rag_service.generate_answer(
                query=request.query,
                intent=intent,
                bundle=bundle,
            )

    response: QueryResponse = await _cb_llm.call(
        with_timeout,
        _llm_call(),
        _TIMEOUT_LLM,
        None,
        "llm_rag",
        fallback=None,
    )
    if response is None:
        # LLM timed out / circuit open — return structured-only fallback
        from src.models.schemas import EvidenceSummary
        response = QueryResponse(
            answer=(
                "Service temporarily unavailable — here is what we know from "
                "authoritative data: "
                + (bundle.business.name if bundle.business else "No data available.")
            ),
            confidence=round(bundle.structured_score * 0.4, 2),
            intent=intent,
            evidence=EvidenceSummary(
                structured=bundle.business is not None,
                reviews_used=0,
                photos_used=0,
            ),
        )

    # 7. Store in cache and return
    response.latency_ms = round((time.monotonic() - wall_start) * 1000, 1)
    await query_cache.set_query_result(
        request.business_id, request.query, response.model_dump()
    )
    return response


async def _noop(value: Any) -> Any:
    """Coroutine that immediately returns *value* (used for disabled search paths)."""
    return value


if __name__ == "__main__":
    import asyncio as _asyncio
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
