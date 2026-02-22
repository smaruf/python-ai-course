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
from src.cache.cache_layer import QueryCache
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
            "src/cache/cache_layer.py",
            "src/resilience/circuit_breaker.py",
        ]
        for path in expected:
            assert os.path.exists(os.path.join(project_root, path)), f"Missing: {path}"

    def test_requirements_has_expected_deps(self):
        project_root = os.path.join(os.path.dirname(__file__), "..")
        with open(os.path.join(project_root, "requirements.txt")) as f:
            content = f.read()
        for dep in ["fastapi", "pytest", "pydantic", "plantuml", "diagrams"]:
            assert dep in content, f"Missing dependency: {dep}"

    def test_diagram_files_exist(self):
        project_root = os.path.join(os.path.dirname(__file__), "..")
        expected = [
            "diagram_sources/plantuml/component_architecture.puml",
            "diagram_sources/plantuml/class_models.puml",
            "diagram_sources/plantuml/sequence_query_flow.puml",
            "diagram_sources/plantuml/sequence_streaming_ingest.puml",
            "diagram_sources/pydiagram/architecture.py",
            "diagram_sources/pydiagram/data_flow.py",
            "diagram_sources/plantuml_renderer.py",
        ]
        for path in expected:
            assert os.path.exists(os.path.join(project_root, path)), f"Missing: {path}"

    def test_demo_module_exists(self):
        project_root = os.path.join(os.path.dirname(__file__), "..")
        assert os.path.exists(os.path.join(project_root, "demo/presentation.py"))

    def test_puml_files_valid_syntax(self):
        """Each .puml file must start with @startuml and end with @enduml."""
        project_root = os.path.join(os.path.dirname(__file__), "..")
        puml_dir = os.path.join(project_root, "diagram_sources", "plantuml")
        import glob as _glob
        for path in _glob.glob(os.path.join(puml_dir, "*.puml")):
            with open(path) as f:
                content = f.read().strip()
            assert content.startswith("@startuml"), f"{path} missing @startuml"
            assert content.endswith("@enduml"),    f"{path} missing @enduml"


# ---------------------------------------------------------------------------
# Cache layer tests
# ---------------------------------------------------------------------------

class TestQueryCache:

    @pytest.mark.asyncio
    async def test_miss_returns_none(self):
        cache = QueryCache()
        result = await cache.get_query_result("biz-1", "any query")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_then_get_returns_value(self):
        cache = QueryCache()
        payload = {"answer": "Open until 22:00", "confidence": 0.9,
                   "intent": "operational",
                   "evidence": {"structured": True, "reviews_used": 0, "photos_used": 0}}
        await cache.set_query_result("biz-1", "is it open?", payload)
        result = await cache.get_query_result("biz-1", "is it open?")
        assert result is not None
        assert result["answer"] == "Open until 22:00"

    @pytest.mark.asyncio
    async def test_different_queries_different_keys(self):
        cache = QueryCache()
        await cache.set_query_result("biz-1", "query A", {"answer": "A"})
        await cache.set_query_result("biz-1", "query B", {"answer": "B"})
        a = await cache.get_query_result("biz-1", "query A")
        b = await cache.get_query_result("biz-1", "query B")
        assert a["answer"] == "A"
        assert b["answer"] == "B"

    @pytest.mark.asyncio
    async def test_invalidate_clears_entries(self):
        cache = QueryCache()
        await cache.set_query_result("biz-1", "hours query", {"answer": "9-10"})
        await cache.invalidate_business("biz-1")
        result = await cache.get_query_result("biz-1", "hours query")
        assert result is None

    @pytest.mark.asyncio
    async def test_hours_cache(self):
        cache = QueryCache()
        hours = {"monday": {"open": "09:00", "close": "22:00"}}
        await cache.set_business_hours("biz-2", hours)
        result = await cache.get_business_hours("biz-2")
        assert result == hours

    @pytest.mark.asyncio
    async def test_embedding_cache(self):
        cache = QueryCache()
        emb = [0.1, 0.2, 0.3, 0.4]
        await cache.set_embedding("heated patio query", emb)
        result = await cache.get_embedding("heated patio query")
        assert result == emb

    @pytest.mark.asyncio
    async def test_l1_size_increments(self):
        cache = QueryCache()
        assert cache.l1_size() == 0
        await cache.set_query_result("biz-1", "q1", {"answer": "a1"})
        assert cache.l1_size() == 1
        await cache.set_query_result("biz-1", "q2", {"answer": "a2"})
        assert cache.l1_size() == 2

    @pytest.mark.asyncio
    async def test_key_lock_same_key_returns_same_lock(self):
        cache = QueryCache()
        lock1 = await cache.get_key_lock("key-A")
        lock2 = await cache.get_key_lock("key-A")
        assert lock1 is lock2

    @pytest.mark.asyncio
    async def test_l1_bounded_by_maxsize(self):
        from src.cache.cache_layer import _L1Cache
        l1 = _L1Cache(maxsize=5)
        for i in range(10):
            await l1.set(f"key-{i}", f"val-{i}", ttl=60)
        assert l1.size() == 5

    @pytest.mark.asyncio
    async def test_l1_ttl_expiry(self):
        import time as _time
        from src.cache.cache_layer import _L1Cache
        l1 = _L1Cache()
        await l1.set("expiring", "value", ttl=0)   # expires immediately
        # Give the clock a nudge by sleeping a tiny bit
        await asyncio.sleep(0.01)
        result = await l1.get("expiring")
        assert result is None


# ---------------------------------------------------------------------------
# Circuit Breaker tests
# ---------------------------------------------------------------------------

class TestCircuitBreaker:

    @pytest.mark.asyncio
    async def test_closed_state_passes_calls_through(self):
        from src.resilience.circuit_breaker import CircuitBreaker, CircuitState
        cb = CircuitBreaker("svc", failure_threshold=3)
        assert cb.state == CircuitState.CLOSED

        async def _ok():
            return "result"

        result = await cb.call(_ok, fallback="fallback")
        assert result == "result"
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_opens_after_threshold_failures(self):
        from src.resilience.circuit_breaker import CircuitBreaker, CircuitState
        cb = CircuitBreaker("svc", failure_threshold=2)

        async def _fail():
            raise RuntimeError("boom")

        for _ in range(2):
            await cb.call(_fail, fallback=None)
        assert cb.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_open_returns_fallback_immediately(self):
        from src.resilience.circuit_breaker import CircuitBreaker, CircuitState
        cb = CircuitBreaker("svc", failure_threshold=1)

        async def _fail():
            raise RuntimeError("boom")

        await cb.call(_fail, fallback="fallback")
        assert cb.state == CircuitState.OPEN

        call_count = 0

        async def _should_not_be_called():
            nonlocal call_count
            call_count += 1
            return "called"

        result = await cb.call(_should_not_be_called, fallback="fallback")
        assert result == "fallback"
        assert call_count == 0   # function was never invoked

    @pytest.mark.asyncio
    async def test_half_open_after_recovery_timeout(self):
        from src.resilience.circuit_breaker import CircuitBreaker, CircuitState
        cb = CircuitBreaker("svc", failure_threshold=1, recovery_timeout=0.02)

        async def _fail():
            raise RuntimeError("boom")

        await cb.call(_fail, fallback=None)
        assert cb.state == CircuitState.OPEN

        await asyncio.sleep(0.03)

        async def _ok():
            return "ok"

        result = await cb.call(_ok, fallback="fallback")
        # After one success in HALF_OPEN we need success_threshold successes
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_closes_after_successful_half_open_probes(self):
        from src.resilience.circuit_breaker import CircuitBreaker, CircuitState
        cb = CircuitBreaker("svc", failure_threshold=1,
                            recovery_timeout=0.01, success_threshold=2)

        async def _fail():
            raise RuntimeError()

        async def _ok():
            return "ok"

        await cb.call(_fail, fallback=None)
        await asyncio.sleep(0.02)
        await cb.call(_ok, fallback=None)   # first probe — still HALF_OPEN
        await cb.call(_ok, fallback=None)   # second probe — closes
        assert cb.state == CircuitState.CLOSED

    def test_reset_clears_state(self):
        from src.resilience.circuit_breaker import CircuitBreaker, CircuitState
        cb = CircuitBreaker("svc", failure_threshold=0)
        cb._state = CircuitState.OPEN
        cb.reset()
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_with_timeout_returns_fallback_on_expiry(self):
        from src.resilience.circuit_breaker import with_timeout

        async def _slow():
            await asyncio.sleep(10)
            return "done"

        result = await with_timeout(_slow(), timeout_seconds=0.01, fallback="timed_out")
        assert result == "timed_out"

    @pytest.mark.asyncio
    async def test_with_timeout_returns_result_before_expiry(self):
        from src.resilience.circuit_breaker import with_timeout

        async def _fast():
            return "fast_result"

        result = await with_timeout(_fast(), timeout_seconds=5.0, fallback="fallback")
        assert result == "fast_result"

    @pytest.mark.asyncio
    async def test_concurrency_limiter_caps_slots(self):
        from src.resilience.circuit_breaker import ConcurrencyLimiter
        limiter = ConcurrencyLimiter("test", max_concurrent=2)
        assert limiter.available == 2
        async with limiter:
            assert limiter.available == 1
        assert limiter.available == 2


# ---------------------------------------------------------------------------
# PlantUML renderer tests
# ---------------------------------------------------------------------------

class TestPlantUMLRenderer:

    def test_encode_produces_non_empty_string(self):
        from diagram_sources.plantuml_renderer import PlantUMLRenderer
        renderer = PlantUMLRenderer()
        source = "@startuml\nAlice -> Bob : hello\n@enduml"
        encoded = renderer.encode(source)
        assert isinstance(encoded, str)
        assert len(encoded) > 0

    def test_url_for_source_contains_server(self):
        from diagram_sources.plantuml_renderer import PlantUMLRenderer, DEFAULT_SERVER_URL
        renderer = PlantUMLRenderer()
        source = "@startuml\nAlice -> Bob : hi\n@enduml"
        url = renderer.url_for_source(source)
        from urllib.parse import urlparse
        parsed = urlparse(url)
        assert parsed.scheme in ("http", "https")
        assert parsed.netloc != ""

    def test_url_for_file_reads_puml_file(self, tmp_path):
        from diagram_sources.plantuml_renderer import PlantUMLRenderer
        puml_file = tmp_path / "test.puml"
        puml_file.write_text("@startuml\nA -> B : test\n@enduml")
        renderer = PlantUMLRenderer()
        url = renderer.url_for_file(str(puml_file))
        assert isinstance(url, str)
        assert len(url) > 0

    def test_url_for_all_project_puml_files(self):
        from diagram_sources.plantuml_renderer import PlantUMLRenderer
        from urllib.parse import urlparse
        import glob as _glob
        renderer = PlantUMLRenderer()
        project_root = os.path.join(os.path.dirname(__file__), "..")
        puml_dir = os.path.join(project_root, "diagram_sources", "plantuml")
        for path in _glob.glob(os.path.join(puml_dir, "*.puml")):
            url = renderer.url_for_file(path)
            parsed = urlparse(url)
            assert parsed.scheme in ("http", "https"), f"Invalid URL for {path}: {url}"
            assert parsed.netloc != "", f"Missing host in URL for {path}: {url}"

    def test_render_all_returns_mapping(self, tmp_path):
        from diagram_sources.plantuml_renderer import PlantUMLRenderer
        # Create two dummy .puml files
        for name in ("diag_a", "diag_b"):
            (tmp_path / f"{name}.puml").write_text(
                f"@startuml\nA -> B : {name}\n@enduml"
            )
        renderer = PlantUMLRenderer()
        urls = renderer.render_all(str(tmp_path), str(tmp_path / "out"))
        assert "diag_a" in urls
        assert "diag_b" in urls
        assert all(isinstance(u, str) for u in urls.values())


# ---------------------------------------------------------------------------
# PyDiagram (diagrams library) tests
# ---------------------------------------------------------------------------

class TestPyDiagram:

    def test_architecture_module_importable(self):
        from diagram_sources.pydiagram import architecture
        assert callable(architecture.build)

    def test_data_flow_module_importable(self):
        from diagram_sources.pydiagram import data_flow
        assert callable(data_flow.build)

    def test_architecture_renders_png(self, tmp_path):
        from diagram_sources.pydiagram.architecture import build
        build(filename="arch_test", output_dir=str(tmp_path), show=False)
        out = tmp_path / "arch_test.png"
        assert out.exists(), "Architecture PNG was not created"
        assert out.stat().st_size > 0

    def test_data_flow_renders_png(self, tmp_path):
        from diagram_sources.pydiagram.data_flow import build
        build(filename="flow_test", output_dir=str(tmp_path), show=False)
        out = tmp_path / "flow_test.png"
        assert out.exists(), "Data-flow PNG was not created"
        assert out.stat().st_size > 0


# ---------------------------------------------------------------------------
# Presentation / demo module tests
# ---------------------------------------------------------------------------

class TestPresentation:

    @pytest.mark.asyncio
    async def test_demo_intent_classification_runs(self, capsys):
        import demo.presentation as pres
        pres._PAUSE_ENABLED = False
        from demo.presentation import demo_intent_classification
        demo_intent_classification()
        captured = capsys.readouterr()
        assert "operational" in captured.out.lower()
        assert "amenity" in captured.out.lower()

    @pytest.mark.asyncio
    async def test_demo_query_routing_runs(self, capsys):
        import demo.presentation as pres
        pres._PAUSE_ENABLED = False
        from demo.presentation import demo_query_routing
        demo_query_routing()
        captured = capsys.readouterr()
        assert "OPERATIONAL" in captured.out or "operational" in captured.out

    @pytest.mark.asyncio
    async def test_demo_structured_authority_runs(self, capsys):
        import demo.presentation as pres
        pres._PAUSE_ENABLED = False
        from demo.presentation import demo_structured_authority
        await demo_structured_authority()
        captured = capsys.readouterr()
        assert "Golden Fork" in captured.out

    @pytest.mark.asyncio
    async def test_demo_cache_behaviour_runs(self, capsys):
        import demo.presentation as pres
        pres._PAUSE_ENABLED = False
        from demo.presentation import demo_cache_behaviour
        await demo_cache_behaviour()
        captured = capsys.readouterr()
        assert "MISS" in captured.out
        assert "HIT" in captured.out

    @pytest.mark.asyncio
    async def test_demo_circuit_breaker_runs(self, capsys):
        import demo.presentation as pres
        pres._PAUSE_ENABLED = False
        from demo.presentation import demo_circuit_breaker
        await demo_circuit_breaker()
        captured = capsys.readouterr()
        assert "open" in captured.out.lower() or "OPEN" in captured.out

    @pytest.mark.asyncio
    async def test_demo_full_pipeline_runs(self, capsys):
        import demo.presentation as pres
        pres._PAUSE_ENABLED = False
        from demo.presentation import demo_full_pipeline
        await demo_full_pipeline()
        captured = capsys.readouterr()
        assert "Golden Fork" in captured.out
        assert "answer" in captured.out.lower() or "Answer" in captured.out

    @pytest.mark.asyncio
    async def test_demo_ingestion_runs(self, capsys):
        import demo.presentation as pres
        pres._PAUSE_ENABLED = False
        from demo.presentation import demo_ingestion
        await demo_ingestion()
        captured = capsys.readouterr()
        assert "STREAM" in captured.out
        assert "Batch" in captured.out or "batch" in captured.out.lower()

    def test_demo_diagrams_runs(self, capsys):
        from demo.presentation import demo_diagrams
        demo_diagrams()
        captured = capsys.readouterr()
        assert ".puml" in captured.out

    @pytest.mark.asyncio
    async def test_run_demo_all_sections(self, capsys):
        import demo.presentation as pres
        pres._PAUSE_ENABLED = False
        await pres.run_demo()
        captured = capsys.readouterr()
        assert "Demo Complete" in captured.out

    @pytest.mark.asyncio
    async def test_run_demo_single_section(self, capsys):
        import demo.presentation as pres
        pres._PAUSE_ENABLED = False
        await pres.run_demo(sections=["intent"])
        captured = capsys.readouterr()
        assert "Intent" in captured.out

    def test_sections_dict_complete(self):
        from demo.presentation import SECTIONS
        expected_keys = {
            "intent", "routing", "structured", "conflict",
            "cache", "breaker", "pipeline", "ingestion", "diagrams",
        }
        assert expected_keys == set(SECTIONS.keys())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
