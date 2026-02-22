"""
Yelp-Style AI Assistant — FastAPI Application
=============================================

Implements the API contract from TDD §9:

  POST /assistant/query
  GET  /health

Architecture flow (TDD §2.1):
  Query → Intent Classification → Query Routing → Multi-source Search
        → Answer Orchestration → LLM (RAG) → Response
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.intent.classifier import IntentClassifier
from src.models.schemas import BusinessData, BusinessHours, Photo, QueryRequest, QueryResponse, Review
from src.orchestration.orchestrator import AnswerOrchestrator
from src.rag.rag_service import RAGService
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
    _seed_demo_data()
    print("🚀 Yelp-Style AI Assistant API started")
    print("📖 Docs: http://localhost:8000/docs")
    yield
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
        "- Retrieval-Augmented Generation (RAG)"
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
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "yelp-ai-assistant",
        "version": "1.0.0",
    }


@app.post("/assistant/query", response_model=QueryResponse, tags=["Assistant"])
async def query_assistant(request: QueryRequest) -> QueryResponse:
    """
    Answer a natural-language query about a business.

    Flow: Intent Classification → Query Routing → Multi-source Search
          → Answer Orchestration → RAG → Response
    """
    wall_start = time.monotonic()

    # 1. Intent classification (target < 20 ms)
    intent, _confidence, _cls_ms = intent_classifier.classify(request.query)

    # 2. Route and retrieve
    try:
        routed = await query_router.route(
            query=request.query,
            business_id=request.business_id,
            intent=intent,
            structured_service=structured_service,
            review_service=review_service,
            photo_service=photo_service,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Search error: {exc}") from exc

    # 3. Orchestrate evidence
    bundle = orchestrator.orchestrate(routed)

    # 4. Generate answer via RAG
    response = await rag_service.generate_answer(
        query=request.query,
        intent=intent,
        bundle=bundle,
    )

    # Overwrite latency with end-to-end wall time
    response.latency_ms = round((time.monotonic() - wall_start) * 1000, 1)
    return response


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
