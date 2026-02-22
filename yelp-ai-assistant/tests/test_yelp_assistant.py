#!/usr/bin/env python3
"""
Test suite for the Yelp-Style AI Assistant
==========================================

Tests cover:
  - Intent classification
  - Query routing logic
  - Structured / review / photo search services
  - Answer orchestration (scoring, conflict detection)
  - RAG mock answer generation
  - FastAPI endpoint contracts
  - Data ingestion pipelines
"""

from __future__ import annotations

import asyncio
import sys
import os

import pytest

# Make the project root importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.schemas import (
    BusinessData,
    BusinessHours,
    Photo,
    QueryIntent,
    QueryRequest,
    Review,
)
from src.intent.classifier import IntentClassifier
from src.routing.router import QueryRouter
from src.search.services import (
    PhotoHybridRetrievalService,
    ReviewVectorSearchService,
    StructuredSearchService,
)
from src.orchestration.orchestrator import AnswerOrchestrator
from src.rag.rag_service import RAGService
from src.ingestion.pipelines import (
    BatchIngestionPipeline,
    IngestionEvent,
    EventType,
    StreamingIngestionPipeline,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_business() -> BusinessData:
    return BusinessData(
        business_id="biz-001",
        name="Test Bistro",
        address="1 Test Ave, NYC",
        phone="+1-000-000-0000",
        price_range="$$",
        hours=[
            BusinessHours("monday", "09:00", "22:00"),
            BusinessHours("tuesday", "09:00", "22:00"),
            BusinessHours("sunday", "10:00", "21:00"),
        ],
        amenities={"heated_patio": True, "parking": False, "wifi": True},
        rating=4.2,
        review_count=100,
    )


@pytest.fixture
def sample_reviews(sample_business) -> list[Review]:
    return [
        Review(
            review_id="r1",
            business_id=sample_business.business_id,
            user_id="u1",
            rating=5.0,
            text="Heated patio is amazing in winter!",
        ),
        Review(
            review_id="r2",
            business_id=sample_business.business_id,
            user_id="u2",
            rating=4.0,
            text="Great date night spot, romantic atmosphere.",
        ),
    ]


@pytest.fixture
def sample_photos(sample_business) -> list[Photo]:
    return [
        Photo(
            photo_id="p1",
            business_id=sample_business.business_id,
            url="https://example.com/patio.jpg",
            caption="Outdoor heated patio with heaters",
        ),
        Photo(
            photo_id="p2",
            business_id=sample_business.business_id,
            url="https://example.com/interior.jpg",
            caption="Cozy indoor seating area",
        ),
    ]


@pytest.fixture
def structured_svc(sample_business) -> StructuredSearchService:
    svc = StructuredSearchService()
    svc.add_business(sample_business)
    return svc


@pytest.fixture
def review_svc(sample_reviews) -> ReviewVectorSearchService:
    svc = ReviewVectorSearchService()
    for r in sample_reviews:
        svc.add_review(r)
    return svc


@pytest.fixture
def photo_svc(sample_photos) -> PhotoHybridRetrievalService:
    svc = PhotoHybridRetrievalService()
    for p in sample_photos:
        svc.add_photo(p)
    return svc


# ---------------------------------------------------------------------------
# Intent Classifier Tests
# ---------------------------------------------------------------------------

class TestIntentClassifier:

    def setup_method(self):
        self.clf = IntentClassifier()

    def test_operational_intent(self):
        intent, conf, latency = self.clf.classify("Is the restaurant open right now?")
        assert intent == QueryIntent.OPERATIONAL
        assert conf > 0
        assert latency >= 0

    def test_operational_hours(self):
        intent, _, _ = self.clf.classify("What are the business hours on Monday?")
        assert intent == QueryIntent.OPERATIONAL

    def test_amenity_patio(self):
        intent, _, _ = self.clf.classify("Do they have a heated patio?")
        assert intent == QueryIntent.AMENITY

    def test_amenity_parking(self):
        intent, _, _ = self.clf.classify("Is there parking available?")
        assert intent == QueryIntent.AMENITY

    def test_quality_date(self):
        intent, _, _ = self.clf.classify("Is it good for a date night?")
        assert intent == QueryIntent.QUALITY

    def test_photo_intent(self):
        intent, _, _ = self.clf.classify("Show me photos of the outdoor area")
        assert intent == QueryIntent.PHOTO

    def test_photo_pictures(self):
        intent, _, _ = self.clf.classify("Can I see pictures of the heated patio?")
        # "pictures" triggers photo, but "heated patio" triggers amenity — photo wins tie by priority
        assert intent in (QueryIntent.PHOTO, QueryIntent.AMENITY)

    def test_unknown_intent(self):
        intent, conf, _ = self.clf.classify("xyz abc 123")
        assert intent == QueryIntent.UNKNOWN
        assert conf == 0.0

    def test_latency_under_20ms(self):
        import time
        start = time.monotonic()
        for _ in range(100):
            self.clf.classify("Is the restaurant open now?")
        elapsed_ms = (time.monotonic() - start) * 1000
        avg_ms = elapsed_ms / 100
        assert avg_ms < 20, f"Average latency {avg_ms:.2f} ms exceeds 20 ms target"


# ---------------------------------------------------------------------------
# Query Router Tests
# ---------------------------------------------------------------------------

class TestQueryRouter:

    def setup_method(self):
        self.router = QueryRouter()

    def test_operational_uses_structured_only(self):
        decision = self.router.decide(QueryIntent.OPERATIONAL)
        assert decision.use_structured is True
        assert decision.use_review_vector is False
        assert decision.use_photo_hybrid is False

    def test_amenity_uses_all_sources(self):
        decision = self.router.decide(QueryIntent.AMENITY)
        assert decision.use_structured is True
        assert decision.use_review_vector is True
        assert decision.use_photo_hybrid is True

    def test_quality_uses_review_only(self):
        decision = self.router.decide(QueryIntent.QUALITY)
        assert decision.use_structured is False
        assert decision.use_review_vector is True
        assert decision.use_photo_hybrid is False

    def test_photo_uses_photo_only(self):
        decision = self.router.decide(QueryIntent.PHOTO)
        assert decision.use_structured is False
        assert decision.use_review_vector is False
        assert decision.use_photo_hybrid is True

    def test_unknown_falls_back_broadly(self):
        decision = self.router.decide(QueryIntent.UNKNOWN)
        assert decision.use_structured is True
        assert decision.use_review_vector is True

    @pytest.mark.asyncio
    async def test_route_operational(self, structured_svc, review_svc, photo_svc):
        router = QueryRouter()
        results = await router.route(
            query="Is it open on Monday?",
            business_id="biz-001",
            intent=QueryIntent.OPERATIONAL,
            structured_service=structured_svc,
            review_service=review_svc,
            photo_service=photo_svc,
        )
        assert len(results.structured_results) == 1
        assert len(results.review_results) == 0
        assert len(results.photo_results) == 0

    @pytest.mark.asyncio
    async def test_route_quality(self, structured_svc, review_svc, photo_svc):
        router = QueryRouter()
        results = await router.route(
            query="Is it good for a date?",
            business_id="biz-001",
            intent=QueryIntent.QUALITY,
            structured_service=structured_svc,
            review_service=review_svc,
            photo_service=photo_svc,
        )
        assert len(results.review_results) > 0
        assert len(results.photo_results) == 0


# ---------------------------------------------------------------------------
# Structured Search Tests
# ---------------------------------------------------------------------------

class TestStructuredSearchService:

    @pytest.mark.asyncio
    async def test_returns_business(self, structured_svc):
        results = await structured_svc.search("Is it open?", "biz-001")
        assert len(results) == 1
        assert results[0].business.business_id == "biz-001"

    @pytest.mark.asyncio
    async def test_matches_hours_field(self, structured_svc):
        results = await structured_svc.search("What are the hours?", "biz-001")
        assert "hours" in results[0].matched_fields

    @pytest.mark.asyncio
    async def test_matches_amenity_field(self, structured_svc):
        results = await structured_svc.search("Do they have heated patio?", "biz-001")
        assert any("heated_patio" in f for f in results[0].matched_fields)

    @pytest.mark.asyncio
    async def test_unknown_business_returns_empty(self, structured_svc):
        results = await structured_svc.search("anything", "does-not-exist")
        assert results == []

    def test_is_open_at(self, sample_business):
        from datetime import datetime
        monday_evening = datetime(2026, 2, 23, 20, 0)  # Monday 20:00
        assert sample_business.is_open_at(monday_evening) is True
        monday_midnight = datetime(2026, 2, 23, 23, 0)  # Monday 23:00
        assert sample_business.is_open_at(monday_midnight) is False


# ---------------------------------------------------------------------------
# Review Vector Search Tests
# ---------------------------------------------------------------------------

class TestReviewVectorSearchService:

    @pytest.mark.asyncio
    async def test_returns_reviews(self, review_svc):
        results = await review_svc.search("heated patio", "biz-001")
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_scores_are_between_0_and_1(self, review_svc):
        results = await review_svc.search("romantic date night", "biz-001")
        for r in results:
            assert 0.0 <= r.similarity_score <= 1.0

    @pytest.mark.asyncio
    async def test_results_sorted_by_similarity(self, review_svc):
        results = await review_svc.search("date night romantic", "biz-001")
        if len(results) > 1:
            scores = [r.similarity_score for r in results]
            assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_unknown_business_empty(self, review_svc):
        results = await review_svc.search("patio", "unknown-biz")
        assert results == []


# ---------------------------------------------------------------------------
# Photo Hybrid Retrieval Tests
# ---------------------------------------------------------------------------

class TestPhotoHybridRetrievalService:

    @pytest.mark.asyncio
    async def test_returns_photos(self, photo_svc):
        results = await photo_svc.search("heated patio outdoor", "biz-001")
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_combined_score_formula(self, photo_svc):
        results = await photo_svc.search("outdoor patio", "biz-001")
        for r in results:
            expected = 0.5 * r.caption_score + 0.5 * r.image_similarity
            assert abs(r.combined_score - expected) < 1e-6

    @pytest.mark.asyncio
    async def test_results_sorted_by_combined_score(self, photo_svc):
        results = await photo_svc.search("patio heaters outdoor", "biz-001")
        if len(results) > 1:
            scores = [r.combined_score for r in results]
            assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_unknown_business_empty(self, photo_svc):
        results = await photo_svc.search("anything", "unknown-biz")
        assert results == []


# ---------------------------------------------------------------------------
# Answer Orchestrator Tests
# ---------------------------------------------------------------------------

class TestAnswerOrchestrator:

    def setup_method(self):
        self.orc = AnswerOrchestrator()

    @pytest.mark.asyncio
    async def test_orchestrate_sets_business(
        self, structured_svc, review_svc, photo_svc
    ):
        router = QueryRouter()
        routed = await router.route(
            query="Is it open?",
            business_id="biz-001",
            intent=QueryIntent.OPERATIONAL,
            structured_service=structured_svc,
            review_service=review_svc,
            photo_service=photo_svc,
        )
        bundle = self.orc.orchestrate(routed)
        assert bundle.business is not None
        assert bundle.business.business_id == "biz-001"

    @pytest.mark.asyncio
    async def test_final_score_range(self, structured_svc, review_svc, photo_svc):
        router = QueryRouter()
        routed = await router.route(
            query="Is it good for date?",
            business_id="biz-001",
            intent=QueryIntent.QUALITY,
            structured_service=structured_svc,
            review_service=review_svc,
            photo_service=photo_svc,
        )
        bundle = self.orc.orchestrate(routed)
        assert 0.0 <= bundle.final_score <= 1.0

    def test_build_llm_context_contains_canonical_header(
        self, structured_svc, sample_business
    ):
        from src.routing.router import RoutedResults, RoutingDecision
        from src.search.services import StructuredSearchResult

        decision = RoutingDecision(intent=QueryIntent.OPERATIONAL, use_structured=True)
        routed = RoutedResults(
            decision=decision,
            structured_results=[
                StructuredSearchResult(business=sample_business, matched_fields=["hours"], score=1.0)
            ],
        )
        bundle = self.orc.orchestrate(routed)
        context = self.orc.build_llm_context(bundle, "Is it open?")
        assert "Canonical Facts" in context
        assert "Instructions" in context
        assert "Test Bistro" in context

    def test_conflict_detection(self, sample_business, sample_reviews):
        from src.routing.router import RoutedResults, RoutingDecision
        from src.search.services import ReviewSearchResult, StructuredSearchResult

        # Override amenity to False so review mention creates a conflict
        sample_business.amenities["heated_patio"] = False
        decision = RoutingDecision(intent=QueryIntent.AMENITY, use_structured=True)
        routed = RoutedResults(
            decision=decision,
            structured_results=[
                StructuredSearchResult(business=sample_business, matched_fields=["amenities.heated_patio"], score=1.0)
            ],
            review_results=[
                ReviewSearchResult(review=sample_reviews[0], similarity_score=0.8)
            ],
        )
        bundle = self.orc.orchestrate(routed)
        # The review mentions "heated patio" but canonical says False → conflict note
        assert len(bundle.conflict_notes) > 0


# ---------------------------------------------------------------------------
# RAG Service Tests
# ---------------------------------------------------------------------------

class TestRAGService:

    def setup_method(self):
        self.rag = RAGService(use_mock=True)
        self.orc = AnswerOrchestrator()

    @pytest.mark.asyncio
    async def test_operational_answer_contains_hours(
        self, structured_svc, review_svc, photo_svc
    ):
        router = QueryRouter()
        routed = await router.route(
            query="What are the hours on Monday?",
            business_id="biz-001",
            intent=QueryIntent.OPERATIONAL,
            structured_service=structured_svc,
            review_service=review_svc,
            photo_service=photo_svc,
        )
        bundle = self.orc.orchestrate(routed)
        response = await self.rag.generate_answer(
            query="What are the hours on Monday?",
            intent=QueryIntent.OPERATIONAL,
            bundle=bundle,
        )
        assert "09:00" in response.answer or "hours" in response.answer.lower()
        assert response.evidence.structured is True

    @pytest.mark.asyncio
    async def test_amenity_answer_confirms_patio(
        self, structured_svc, review_svc, photo_svc
    ):
        router = QueryRouter()
        routed = await router.route(
            query="Do they have a heated patio?",
            business_id="biz-001",
            intent=QueryIntent.AMENITY,
            structured_service=structured_svc,
            review_service=review_svc,
            photo_service=photo_svc,
        )
        bundle = self.orc.orchestrate(routed)
        response = await self.rag.generate_answer(
            query="Do they have a heated patio?",
            intent=QueryIntent.AMENITY,
            bundle=bundle,
        )
        assert "Yes" in response.answer or "heated patio" in response.answer.lower()

    @pytest.mark.asyncio
    async def test_quality_answer_mentions_reviews(
        self, structured_svc, review_svc, photo_svc
    ):
        router = QueryRouter()
        routed = await router.route(
            query="Is it good for a date?",
            business_id="biz-001",
            intent=QueryIntent.QUALITY,
            structured_service=structured_svc,
            review_service=review_svc,
            photo_service=photo_svc,
        )
        bundle = self.orc.orchestrate(routed)
        response = await self.rag.generate_answer(
            query="Is it good for a date?",
            intent=QueryIntent.QUALITY,
            bundle=bundle,
        )
        assert "review" in response.answer.lower() or "rating" in response.answer.lower()

    @pytest.mark.asyncio
    async def test_response_confidence_range(
        self, structured_svc, review_svc, photo_svc
    ):
        router = QueryRouter()
        routed = await router.route(
            query="Is it open?",
            business_id="biz-001",
            intent=QueryIntent.OPERATIONAL,
            structured_service=structured_svc,
            review_service=review_svc,
            photo_service=photo_svc,
        )
        bundle = self.orc.orchestrate(routed)
        response = await self.rag.generate_answer("Is it open?", QueryIntent.OPERATIONAL, bundle)
        assert 0.0 <= response.confidence <= 1.0


# ---------------------------------------------------------------------------
# Ingestion Pipeline Tests
# ---------------------------------------------------------------------------

class TestStreamingIngestionPipeline:

    @pytest.mark.asyncio
    async def test_publish_and_process(self):
        pipeline = StreamingIngestionPipeline()
        received = []

        async def handler(event: IngestionEvent):
            received.append(event)

        pipeline.register_handler(EventType.REVIEW_CREATED, handler)

        event = IngestionEvent(
            event_type=EventType.REVIEW_CREATED,
            business_id="biz-001",
            payload={"review_id": "r99", "text": "Loved it!"},
        )
        await pipeline.publish(event)
        processed = await pipeline.process_one()

        assert processed is not None
        assert processed.processed_at is not None
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_drain_processes_all(self):
        pipeline = StreamingIngestionPipeline()
        events = [
            IngestionEvent(EventType.REVIEW_CREATED, "biz-001", {}),
            IngestionEvent(EventType.RATING_UPDATED, "biz-001", {}),
            IngestionEvent(EventType.HOURS_CHANGED, "biz-001", {}),
        ]
        for e in events:
            await pipeline.publish(e)

        processed = await pipeline.drain()
        assert len(processed) == 3

    @pytest.mark.asyncio
    async def test_freshness_sla(self):
        pipeline = StreamingIngestionPipeline()
        event = IngestionEvent(
            event_type=EventType.REVIEW_CREATED,
            business_id="biz-001",
            payload={},
        )
        await pipeline.publish(event)
        processed = await pipeline.process_one()
        assert pipeline.check_freshness_sla(processed) is True

    @pytest.mark.asyncio
    async def test_empty_queue_returns_none(self):
        pipeline = StreamingIngestionPipeline()
        result = await pipeline.process_one()
        assert result is None


class TestBatchIngestionPipeline:

    @pytest.mark.asyncio
    async def test_batch_run(self):
        pipeline = BatchIngestionPipeline()
        processed_counts = []

        def menu_job(records):
            processed_counts.append(len(records))
            return len(records)

        pipeline.register_job(menu_job)
        records = [{"menu_item": "Burger"}, {"menu_item": "Salad"}]
        summary = await pipeline.run(records)

        assert summary["records_in"] == 2
        assert summary["records_processed"] == 2
        assert len(pipeline.run_history) == 1

    @pytest.mark.asyncio
    async def test_batch_error_captured(self):
        pipeline = BatchIngestionPipeline()

        def bad_job(records):
            raise ValueError("bad data")

        pipeline.register_job(bad_job)
        summary = await pipeline.run([{"x": 1}])
        assert len(summary["errors"]) == 1


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------

class TestAPIEndpoints:

    def setup_method(self):
        # Import here to avoid module-level import errors if httpx is unavailable
        try:
            from fastapi.testclient import TestClient
            from main import app
            self.client = TestClient(app)
        except ImportError:
            self.client = None

    def test_health_endpoint(self):
        if self.client is None:
            pytest.skip("TestClient / httpx not available")
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "yelp-ai-assistant"

    def test_query_endpoint_operational(self):
        if self.client is None:
            pytest.skip("TestClient / httpx not available")
        payload = {
            "query": "Is the restaurant open right now?",
            "business_id": "12345",
        }
        response = self.client.post("/assistant/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "confidence" in data
        assert "intent" in data
        assert "evidence" in data

    def test_query_endpoint_amenity(self):
        if self.client is None:
            pytest.skip("TestClient / httpx not available")
        payload = {
            "query": "Do they have a heated patio?",
            "business_id": "12345",
        }
        response = self.client.post("/assistant/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == QueryIntent.AMENITY

    def test_query_endpoint_missing_fields(self):
        if self.client is None:
            pytest.skip("TestClient / httpx not available")
        response = self.client.post("/assistant/query", json={"query": "test"})
        assert response.status_code == 422  # Validation error


# ---------------------------------------------------------------------------
# Project structure tests
# ---------------------------------------------------------------------------

class TestProjectStructure:

    def test_main_files_exist(self):
        project_root = os.path.join(os.path.dirname(__file__), "..")
        assert os.path.exists(os.path.join(project_root, "README.md"))
        assert os.path.exists(os.path.join(project_root, "requirements.txt"))
        assert os.path.exists(os.path.join(project_root, "main.py"))

    def test_src_modules_exist(self):
        project_root = os.path.join(os.path.dirname(__file__), "..")
        expected = [
            "src/models/schemas.py",
            "src/intent/classifier.py",
            "src/routing/router.py",
            "src/search/services.py",
            "src/orchestration/orchestrator.py",
            "src/rag/rag_service.py",
            "src/ingestion/pipelines.py",
        ]
        for path in expected:
            assert os.path.exists(os.path.join(project_root, path)), f"Missing: {path}"

    def test_requirements_has_expected_deps(self):
        project_root = os.path.join(os.path.dirname(__file__), "..")
        with open(os.path.join(project_root, "requirements.txt")) as f:
            content = f.read()
        for dep in ["fastapi", "pytest", "pydantic"]:
            assert dep in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
