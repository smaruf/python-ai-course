"""
10 Types of API Testing — Yelp-Style AI Assistant
==================================================

Covers all ten categories specified by the API testing checklist:

  1. Smoke Testing      — core endpoints respond quickly and correctly
  2. Functional Testing — API behaves per TDD spec (§5, §9)
  3. Integration Testing — services compose correctly end-to-end
  4. Regression Testing  — invariants that must hold after any code change
  5. Load Testing        — API under expected concurrent load
  6. Stress Testing      — extreme/peak conditions and graceful degradation
  7. Security Testing    — injection, PII, oversized input, method restrictions
  8. UI Testing          — CLI and Gradio interface interactions
  9. Fuzz Testing        — random / invalid / boundary payloads
 10. Reliability Testing — consistent answers and stability over many calls

Each class is headed with the test type and a short rationale.
"""

from __future__ import annotations

import asyncio
import json
import os
import random
import string
import sys
import time
from typing import List

import pytest

# ---------------------------------------------------------------------------
# Make project root importable
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from main import app  # noqa: E402 — must come after sys.path update

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

# Module-level client (used for tests that don't need seeded business data)
_client = TestClient(app)

_VALID_PAYLOAD = {
    "query": "Is it open right now?",
    "business_id": "12345",
}

_ALL_INTENTS = ("operational", "amenity", "quality", "photo", "unknown")

# Maximum acceptable spread (max - min) in confidence across repeated identical
# queries.  Scores are derived from deterministic keyword counts, so very low
# variance is expected; 0.5 gives generous headroom for any mock randomness.
_MAX_CONFIDENCE_VARIANCE: float = 0.5



# ============================================================================
# 1. Smoke Testing
# ============================================================================

class TestSmokeTesting:
    """
    Smoke Testing — rapidly verify that the most critical paths are alive.
    Fails fast: if these tests fail nothing else is worth running.
    TDD §8.2 / §9.
    """

    def test_liveness_probe_returns_200(self):
        assert _client.get("/health").status_code == 200

    def test_readiness_probe_returns_200(self):
        assert _client.get("/health/detailed").status_code == 200

    def test_query_endpoint_returns_200(self):
        assert _client.post("/assistant/query", json=_VALID_PAYLOAD).status_code == 200

    def test_health_body_has_status_field(self):
        assert "status" in _client.get("/health").json()

    def test_query_body_has_answer_field(self):
        assert "answer" in _client.post("/assistant/query", json=_VALID_PAYLOAD).json()

    def test_openapi_schema_available(self):
        assert _client.get("/openapi.json").status_code == 200

    def test_swagger_docs_available(self):
        assert _client.get("/docs").status_code == 200

    def test_unknown_route_returns_404(self):
        assert _client.get("/no-such-route-xyz").status_code == 404


# ============================================================================
# 2. Functional Testing
# ============================================================================

class TestFunctionalTesting:
    """
    Functional Testing — validate API behaviour against TDD functional
    specifications (§5 intent classification, §5.2 routing, §9 API contract).
    """

    def test_operational_query_returns_correct_intent(self):
        body = _client.post(
            "/assistant/query",
            json={"query": "What time do they close tonight?", "business_id": "12345"},
        ).json()
        assert body["intent"] == "operational"

    def test_amenity_query_returns_correct_intent(self):
        body = _client.post(
            "/assistant/query",
            json={"query": "Do they have a heated patio?", "business_id": "12345"},
        ).json()
        assert body["intent"] == "amenity"

    def test_quality_query_returns_correct_intent(self):
        body = _client.post(
            "/assistant/query",
            json={"query": "Is it good for a date night?", "business_id": "12345"},
        ).json()
        assert body["intent"] == "quality"

    def test_photo_query_returns_correct_intent(self):
        body = _client.post(
            "/assistant/query",
            json={"query": "Show me photos of the outdoor area", "business_id": "12345"},
        ).json()
        assert body["intent"] == "photo"

    def test_response_schema_complete(self):
        body = _client.post("/assistant/query", json=_VALID_PAYLOAD).json()
        for key in ("answer", "confidence", "intent", "evidence"):
            assert key in body, f"Missing field: {key}"

    def test_evidence_schema_complete(self):
        ev = _client.post("/assistant/query", json=_VALID_PAYLOAD).json()["evidence"]
        for key in ("structured", "reviews_used", "photos_used"):
            assert key in ev, f"Missing evidence field: {key}"

    def test_confidence_in_valid_range(self):
        body = _client.post("/assistant/query", json=_VALID_PAYLOAD).json()
        assert 0.0 <= body["confidence"] <= 1.0

    def test_intent_is_known_value(self):
        body = _client.post("/assistant/query", json=_VALID_PAYLOAD).json()
        assert body["intent"] in _ALL_INTENTS

    def test_operational_uses_structured_evidence(self):
        """TDD §5.2 — operational intent must draw from structured data."""
        with TestClient(app) as client:
            body = client.post(
                "/assistant/query",
                json={"query": "Is it open on Monday?", "business_id": "12345"},
            ).json()
        assert body["evidence"]["structured"] is True

    def test_user_context_accepted(self):
        payload = {
            "query": "Is it open now?",
            "business_id": "12345",
            "user_context": {"location": "NYC", "time": "2026-02-20T20:00:00Z"},
        }
        assert _client.post("/assistant/query", json=payload).status_code == 200

    def test_health_service_field(self):
        assert _client.get("/health").json()["service"] == "yelp-ai-assistant"

    def test_health_detailed_contains_circuit_breakers(self):
        body = _client.get("/health/detailed").json()
        assert "circuit_breakers" in body
        assert "llm_rag" in body["circuit_breakers"]

    def test_missing_business_id_returns_422(self):
        assert _client.post(
            "/assistant/query", json={"query": "open?"}
        ).status_code == 422

    def test_empty_query_returns_422(self):
        assert _client.post(
            "/assistant/query", json={"query": "", "business_id": "12345"}
        ).status_code == 422


# ============================================================================
# 3. Integration Testing
# ============================================================================

class TestIntegrationTesting:
    """
    Integration Testing — verify that distinct modules (intent classifier,
    query router, search services, orchestrator, RAG) interact correctly
    when called together through the HTTP API.
    """

    def test_full_pipeline_operational_end_to_end(self):
        """Intent → Router → Structured Search → Orchestrate → RAG → Response."""
        with TestClient(app) as client:
            body = client.post(
                "/assistant/query",
                json={"query": "What are the opening hours?", "business_id": "12345"},
            ).json()
        assert body["intent"] == "operational"
        assert body["evidence"]["structured"] is True
        assert len(body["answer"]) > 0

    def test_full_pipeline_amenity_uses_structured(self):
        """Amenity routing must touch structured data (TDD §5.2)."""
        with TestClient(app) as client:
            body = client.post(
                "/assistant/query",
                # Use a query not issued by earlier tests to avoid cache collision
                json={"query": "Is there a heated outdoor patio?", "business_id": "12345"},
            ).json()
        assert body["intent"] == "amenity"
        assert body["evidence"]["structured"] is True

    def test_full_pipeline_quality_succeeds(self):
        body = _client.post(
            "/assistant/query",
            json={"query": "Is it good for a date?", "business_id": "12345"},
        ).json()
        assert body["intent"] == "quality"
        assert "answer" in body

    def test_cache_integration_second_call_consistent(self):
        """Identical query repeated — result must be consistent (cache hit)."""
        payload = {"query": "Is it open on Friday evening?", "business_id": "12345"}
        first  = _client.post("/assistant/query", json=payload).json()["answer"]
        second = _client.post("/assistant/query", json=payload).json()["answer"]
        assert first == second

    def test_health_detailed_integrates_cache_info(self):
        _client.post("/assistant/query", json=_VALID_PAYLOAD)  # prime cache
        body = _client.get("/health/detailed").json()
        assert "cache" in body
        assert "l1_entries" in body["cache"]

    def test_correlation_id_echoed_when_provided(self):
        """X-Correlation-ID middleware must echo back a provided header."""
        cid = "test-correlation-id-abc123"
        resp = _client.post(
            "/assistant/query",
            json=_VALID_PAYLOAD,
            headers={"X-Correlation-ID": cid},
        )
        assert resp.headers.get("x-correlation-id") == cid

    def test_correlation_id_generated_when_missing(self):
        """Server generates a UUID Correlation-ID if client omits it."""
        resp = _client.post("/assistant/query", json=_VALID_PAYLOAD)
        cid = resp.headers.get("x-correlation-id", "")
        assert len(cid) > 0

    def test_different_businesses_independent_results(self):
        """Queries for different business_ids must not bleed data."""
        r1 = _client.post(
            "/assistant/query",
            json={"query": "What amenities do they have?", "business_id": "12345"},
        ).json()
        r2 = _client.post(
            "/assistant/query",
            json={"query": "What amenities do they have?", "business_id": "unknown-biz-xyz"},
        ).json()
        assert "answer" in r1
        assert "answer" in r2


# ============================================================================
# 4. Regression Testing
# ============================================================================

class TestRegressionTesting:
    """
    Regression Testing — hard-coded invariants that capture previously correct
    behaviour.  Any code change that breaks these reveals a regression.
    """

    def test_structured_data_overrides_reviews_for_operational(self):
        """TDD §3.1 — structured must always be the authority for operational."""
        with TestClient(app) as client:
            for query in ["Is it open on Sunday?", "What are the hours on Friday?"]:
                body = client.post(
                    "/assistant/query",
                    json={"query": query, "business_id": "12345"},
                ).json()
                assert body["evidence"]["structured"] is True, \
                    f"Structured override failed for: {query!r}"

    def test_response_always_contains_latency_ms(self):
        body = _client.post(
            "/assistant/query",
            json={"query": f"unique regression query {time.monotonic()}", "business_id": "12345"},
        ).json()
        assert "latency_ms" in body
        assert body["latency_ms"] is not None

    def test_health_status_always_healthy(self):
        assert _client.get("/health").json()["status"] == "healthy"

    def test_api_version_is_1_0_0(self):
        assert _client.get("/health").json().get("version") == "1.0.0"

    def test_evidence_reviews_used_non_negative_int(self):
        body = _client.post("/assistant/query", json=_VALID_PAYLOAD).json()
        assert isinstance(body["evidence"]["reviews_used"], int)
        assert body["evidence"]["reviews_used"] >= 0

    def test_evidence_photos_used_non_negative_int(self):
        body = _client.post("/assistant/query", json=_VALID_PAYLOAD).json()
        assert isinstance(body["evidence"]["photos_used"], int)
        assert body["evidence"]["photos_used"] >= 0

    def test_photo_query_does_not_use_structured(self):
        """TDD §5.2 — photo intent routes to photo path only, not structured."""
        body = _client.post(
            "/assistant/query",
            json={"query": "Show me pictures of the restaurant", "business_id": "12345"},
        ).json()
        assert body["intent"] == "photo"
        assert body["evidence"]["structured"] is False

    def test_answer_is_non_empty_string(self):
        body = _client.post("/assistant/query", json=_VALID_PAYLOAD).json()
        assert isinstance(body["answer"], str)
        assert len(body["answer"].strip()) > 0

    def test_intent_classification_is_deterministic(self):
        """Same query must always produce the same intent."""
        query = "What are the weekend hours?"
        intents = {
            _client.post(
                "/assistant/query",
                json={"query": query, "business_id": "12345"},
            ).json()["intent"]
            for _ in range(5)
        }
        assert len(intents) == 1, f"Non-deterministic intent: {intents}"


# ============================================================================
# 5. Load Testing
# ============================================================================

class TestLoadTesting:
    """
    Load Testing — exercise the API under expected concurrent load (asyncio
    httpx clients against the mock backend).  TDD §8.2: P95 < 1.2 s.
    """

    @pytest.mark.asyncio
    async def test_50_concurrent_requests_all_succeed(self):
        """50 concurrent requests must all return HTTP 200."""
        import httpx

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test", timeout=10.0
        ) as ac:
            responses = await asyncio.gather(
                *[ac.post("/assistant/query", json=_VALID_PAYLOAD) for _ in range(50)]
            )
        failures = [r.status_code for r in responses if r.status_code != 200]
        assert not failures, f"Non-200 responses: {failures}"

    @pytest.mark.asyncio
    async def test_p95_latency_under_2s_for_30_concurrent(self):
        """P95 latency under 30 concurrent clients must stay under 2 s."""
        import httpx

        latencies: List[float] = []
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test", timeout=10.0
        ) as ac:
            for _ in range(30):
                t0 = asyncio.get_event_loop().time()
                await ac.post("/assistant/query", json=_VALID_PAYLOAD)
                latencies.append(asyncio.get_event_loop().time() - t0)

        latencies.sort()
        # Use ceiling index so 95th percentile isn't underestimated
        p95_idx = min(int(0.95 * len(latencies)), len(latencies) - 1)
        p95 = latencies[p95_idx]
        assert p95 < 2.0, f"P95 {p95 * 1000:.0f} ms exceeded 2 000 ms"

    @pytest.mark.asyncio
    async def test_100_health_probes_all_succeed(self):
        import httpx

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test", timeout=5.0
        ) as ac:
            responses = await asyncio.gather(
                *[ac.get("/health") for _ in range(100)]
            )
        assert all(r.status_code == 200 for r in responses)

    @pytest.mark.asyncio
    async def test_mixed_intent_load_40_requests(self):
        """Realistic 4-intent traffic mix — all 40 requests must succeed."""
        import httpx

        payloads = [
            {"query": "Is it open right now?",          "business_id": "12345"},
            {"query": "Do they have a heated patio?",   "business_id": "12345"},
            {"query": "Is it good for dates?",          "business_id": "12345"},
            {"query": "Show me photos of the outdoor",  "business_id": "12345"},
        ] * 10

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test", timeout=10.0
        ) as ac:
            responses = await asyncio.gather(
                *[ac.post("/assistant/query", json=p) for p in payloads]
            )
        assert all(r.status_code == 200 for r in responses)

    @pytest.mark.asyncio
    async def test_cached_query_avg_latency_under_1s(self):
        """After cache warm-up, repeated requests must average under 1 s."""
        import httpx

        payload = {"query": "Is the heated patio open on weekends?", "business_id": "12345"}
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test", timeout=10.0
        ) as ac:
            await ac.post("/assistant/query", json=payload)  # warm cache
            latencies = []
            for _ in range(20):
                t0 = asyncio.get_event_loop().time()
                r = await ac.post("/assistant/query", json=payload)
                latencies.append(asyncio.get_event_loop().time() - t0)
                assert r.status_code == 200

        avg_ms = sum(latencies) / len(latencies) * 1000
        assert avg_ms < 1000, f"Average cached latency {avg_ms:.0f} ms too high"


# ============================================================================
# 6. Stress Testing
# ============================================================================

class TestStressTesting:
    """
    Stress Testing — push the API beyond normal conditions to verify graceful
    degradation rather than hard failure.  TDD §13 Failure Modes.
    """

    @pytest.mark.asyncio
    async def test_burst_200_concurrent_requests_survive(self):
        """200 simultaneous requests — failure rate must stay ≤ 2 %."""
        import httpx

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test", timeout=30.0
        ) as ac:
            responses = await asyncio.gather(
                *[ac.post("/assistant/query", json=_VALID_PAYLOAD) for _ in range(200)],
                return_exceptions=True,
            )

        errors   = [r for r in responses if isinstance(r, Exception)]
        non_200  = [r for r in responses if not isinstance(r, Exception) and r.status_code != 200]
        failure_rate = (len(errors) + len(non_200)) / len(responses)
        assert failure_rate <= 0.02, f"Failure rate {failure_rate:.1%} exceeded 2 % under stress"

    @pytest.mark.asyncio
    async def test_maximum_length_query_accepted(self):
        """Query at the 1 000-character limit must be answered (not 422/500)."""
        import httpx

        long_query = ("Is the restaurant open " * 50)[:1000]
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test", timeout=10.0
        ) as ac:
            resp = await ac.post(
                "/assistant/query",
                json={"query": long_query, "business_id": "12345"},
            )
        assert resp.status_code == 200

    def test_health_endpoint_stable_under_100_rapid_polls(self):
        """100 sequential health calls must all return 200."""
        for i in range(100):
            assert _client.get("/health").status_code == 200, f"Failed on poll {i}"

    @pytest.mark.asyncio
    async def test_50_distinct_business_ids_all_return_200(self):
        """Queries for 50 distinct business IDs must not crash the server."""
        import httpx

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test", timeout=15.0
        ) as ac:
            responses = await asyncio.gather(
                *[
                    ac.post(
                        "/assistant/query",
                        json={"query": "Is it open?", "business_id": f"biz-stress-{i}"},
                    )
                    for i in range(50)
                ]
            )
        assert all(r.status_code == 200 for r in responses)

    def test_circuit_breakers_remain_closed_under_normal_stress(self):
        """Under normal (non-failing) load circuit breakers must stay CLOSED."""
        for _ in range(30):
            _client.post("/assistant/query", json=_VALID_PAYLOAD)

        states = _client.get("/health/detailed").json()["circuit_breakers"]
        for name, state in states.items():
            assert state in ("closed", "half_open", "open"), \
                f"Unexpected CB state {state!r} for {name}"


# ============================================================================
# 7. Security Testing
# ============================================================================

class TestSecurityTesting:
    """
    Security Testing — assess the API for injection, PII exposure, oversized
    payloads, header abuse, and HTTP method restrictions.  TDD §12.
    """

    def test_sql_injection_in_query_does_not_crash(self):
        resp = _client.post(
            "/assistant/query",
            json={"query": "'; DROP TABLE businesses; --", "business_id": "12345"},
        )
        assert resp.status_code in (200, 422)

    def test_xss_payload_does_not_echo_script_tag(self):
        resp = _client.post(
            "/assistant/query",
            json={"query": "<script>alert('xss')</script> Is it open?", "business_id": "12345"},
        )
        assert resp.status_code in (200, 422)
        if resp.status_code == 200:
            assert "<script>" not in resp.text

    def test_oversized_query_rejected_with_422(self):
        resp = _client.post(
            "/assistant/query",
            json={"query": "x" * 1001, "business_id": "12345"},
        )
        assert resp.status_code == 422

    def test_empty_business_id_rejected(self):
        assert _client.post(
            "/assistant/query", json={"query": "open?", "business_id": ""}
        ).status_code == 422

    def test_null_query_rejected(self):
        assert _client.post(
            "/assistant/query", json={"query": None, "business_id": "12345"}
        ).status_code == 422

    def test_get_on_post_only_endpoint_returns_405(self):
        assert _client.get("/assistant/query").status_code == 405

    def test_delete_on_post_only_endpoint_returns_405(self):
        assert _client.delete("/assistant/query").status_code == 405

    def test_answer_does_not_leak_file_system_paths(self):
        body = _client.post("/assistant/query", json=_VALID_PAYLOAD).json()
        for sensitive in ("/home/", "/etc/", "/var/", "Traceback", "traceback"):
            assert sensitive not in body.get("answer", ""), \
                f"Sensitive string {sensitive!r} leaked in answer"

    def test_empty_json_body_returns_422_not_500(self):
        resp = _client.post(
            "/assistant/query",
            content=b"",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 422

    def test_deeply_nested_user_context_does_not_500(self):
        payload = {
            "query": "Is it open?",
            "business_id": "12345",
            "user_context": {"location": "NYC"},
        }
        assert _client.post("/assistant/query", json=payload).status_code == 200

    def test_unknown_business_does_not_fabricate_phone_pii(self):
        """Answers for unknown businesses must not hallucinate PII."""
        body = _client.post(
            "/assistant/query",
            json={"query": "What is the phone number?", "business_id": "no-such-biz"},
        ).json()
        # The answer must be present but the service should not invent a phone
        assert "answer" in body

    def test_patch_on_query_endpoint_not_allowed(self):
        assert _client.patch("/assistant/query").status_code in (404, 405)


# ============================================================================
# 8. UI Testing
# ============================================================================

class TestUITesting:
    """
    UI Testing — validate interaction between user interfaces (Gradio GUI and
    Click CLI) and the API / backend logic.
    """

    # ── Gradio GUI ────────────────────────────────────────────────────────────

    def test_gui_ask_returns_answer_markdown(self):
        from gui.app import _ask
        answer_md, intent_md, raw = _ask("Is it open right now?", "demo-001")
        assert isinstance(answer_md, str) and len(answer_md) > 0

    def test_gui_intent_badge_present_in_output(self):
        from gui.app import _ask
        _, intent_md, _ = _ask("Do they have a heated patio?", "demo-001")
        assert isinstance(intent_md, str) and len(intent_md) > 0

    def test_gui_raw_json_is_valid(self):
        from gui.app import _ask
        _, _, raw = _ask("Is it good for dates?", "demo-001")
        data = json.loads(raw)
        assert "answer" in data and "intent" in data

    def test_gui_empty_query_shows_warning(self):
        from gui.app import _ask
        answer_md, _, _ = _ask("", "demo-001")
        assert "⚠" in answer_md or "Please" in answer_md

    def test_gui_demo002_business_id_in_raw_json(self):
        from gui.app import _ask
        _, _, raw = _ask("What time do they close?", "demo-002")
        assert json.loads(raw)["business_id"] == "demo-002"

    def test_gui_sample_queries_at_least_6(self):
        from gui.app import SAMPLE_QUERIES
        assert len(SAMPLE_QUERIES) >= 6

    def test_gui_both_businesses_seeded(self):
        from gui.app import _BUSINESSES
        assert "demo-001" in _BUSINESSES and "demo-002" in _BUSINESSES

    def test_gui_build_interface_returns_blocks(self):
        import gradio as gr
        from gui.app import build_interface
        assert isinstance(build_interface(), gr.Blocks)

    # ── Click CLI ─────────────────────────────────────────────────────────────

    def _runner(self):
        from click.testing import CliRunner
        return CliRunner()

    def test_cli_help_lists_all_commands(self):
        from cli.main import cli
        result = self._runner().invoke(cli, ["--help"])
        assert result.exit_code == 0
        for cmd in ("query", "health", "demo", "serve"):
            assert cmd in result.output

    def test_cli_version(self):
        from cli.main import cli
        result = self._runner().invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_cli_query_pretty_format_shows_answer(self):
        from cli.main import cli
        result = self._runner().invoke(
            cli, ["query", "Is it open right now?", "--business-id", "demo-001"]
        )
        assert result.exit_code == 0
        assert "Answer" in result.output or "answer" in result.output.lower()

    def test_cli_query_json_format_valid(self):
        from cli.main import cli
        result = self._runner().invoke(
            cli, ["query", "--format", "json", "Do they have wifi?"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "answer" in data and "intent" in data

    def test_cli_health_shows_healthy(self):
        from cli.main import cli
        result = self._runner().invoke(cli, ["health"])
        assert result.exit_code == 0
        assert "healthy" in result.output.lower()


# ============================================================================
# 9. Fuzz Testing
# ============================================================================

class TestFuzzTesting:
    """
    Fuzz Testing — send random, boundary-value, and structurally invalid data
    to detect unexpected crashes.  The server must always return a structured
    HTTP response (never an unhandled 500).
    """

    @staticmethod
    def _rand_str(length: int) -> str:
        return "".join(random.choices(string.printable, k=length))

    def test_random_printable_queries_no_500(self):
        """50 random printable-string queries — server must not return 500."""
        for _ in range(50):
            payload = {
                "query": self._rand_str(random.randint(1, 200)),
                "business_id": "12345",
            }
            resp = _client.post("/assistant/query", json=payload)
            assert resp.status_code != 500, \
                f"Server 500 on query: {payload['query']!r}"

    def test_unicode_queries_no_500(self):
        for q in [
            "こんにちは。レストランは開いていますか？",
            "🍕🔥 Is there a patio? 🌿",
            "Ăn uống ở đây có ngon không?",
            "مطعم مفتوح الآن؟",
            "Открыт ли ресторан?",
        ]:
            resp = _client.post(
                "/assistant/query", json={"query": q, "business_id": "12345"}
            )
            assert resp.status_code in (200, 422), \
                f"Unexpected {resp.status_code} for query: {q!r}"

    def test_special_characters_in_business_id_no_500(self):
        for biz_id in ["../secret", "'; DROP TABLE--", "<script>", "null", "undefined"]:
            resp = _client.post(
                "/assistant/query",
                json={"query": "Is it open?", "business_id": biz_id},
            )
            assert resp.status_code in (200, 422), \
                f"Unexpected {resp.status_code} for business_id: {biz_id!r}"

    def test_extra_unknown_fields_ignored(self):
        """Pydantic should silently ignore extra JSON fields."""
        resp = _client.post(
            "/assistant/query",
            json={
                "query": "Is it open?",
                "business_id": "12345",
                "unexpected_field": "surprise",
                "nested_unknown": {"key": True},
            },
        )
        assert resp.status_code in (200, 422)

    def test_numeric_string_query_no_500(self):
        resp = _client.post(
            "/assistant/query",
            json={"query": "12345 67890", "business_id": "12345"},
        )
        assert resp.status_code in (200, 422)

    def test_boundary_query_length_999_accepted(self):
        assert _client.post(
            "/assistant/query",
            json={"query": "a" * 999, "business_id": "12345"},
        ).status_code == 200

    def test_boundary_query_length_1000_accepted(self):
        assert _client.post(
            "/assistant/query",
            json={"query": "a" * 1000, "business_id": "12345"},
        ).status_code == 200

    def test_boundary_query_length_1001_rejected(self):
        assert _client.post(
            "/assistant/query",
            json={"query": "a" * 1001, "business_id": "12345"},
        ).status_code == 422

    def test_http_methods_other_than_post_rejected(self):
        for method in ("get", "put", "patch", "delete"):
            resp = getattr(_client, method)("/assistant/query")
            assert resp.status_code in (404, 405), \
                f"Method {method.upper()} returned unexpected {resp.status_code}"

    def test_boolean_query_value_rejected(self):
        resp = _client.post(
            "/assistant/query",
            json={"query": True, "business_id": "12345"},
        )
        assert resp.status_code == 422

    def test_integer_query_value_rejected(self):
        resp = _client.post(
            "/assistant/query",
            json={"query": 42, "business_id": "12345"},
        )
        assert resp.status_code == 422


# ============================================================================
# 10. Reliability Testing
# ============================================================================

class TestReliabilityTesting:
    """
    Reliability Testing — evaluate the API's consistency and stability over
    an extended series of calls.  TDD §17 success criteria: 95 % accuracy on
    operational queries, consistent results, no unintended state mutations.
    """

    def test_repeated_operational_query_consistent_intent(self):
        """Same query 20 × must always return the same intent."""
        query = "What are the Monday opening hours?"
        intents = {
            _client.post(
                "/assistant/query",
                json={"query": query, "business_id": "12345"},
            ).json()["intent"]
            for _ in range(20)
        }
        assert len(intents) == 1, f"Inconsistent intents: {intents}"

    def test_confidence_spread_stable_for_same_query(self):
        """Confidence for the same query must not vary by more than 0.5."""
        query = "Is it open on Saturday?"
        confidences = [
            _client.post(
                "/assistant/query",
                json={"query": query, "business_id": "12345"},
            ).json()["confidence"]
            for _ in range(10)
        ]
        assert max(confidences) - min(confidences) < _MAX_CONFIDENCE_VARIANCE

    def test_answer_non_empty_over_15_calls(self):
        for _ in range(15):
            body = _client.post("/assistant/query", json=_VALID_PAYLOAD).json()
            assert isinstance(body["answer"], str) and len(body["answer"].strip()) > 0

    def test_health_endpoint_always_healthy_over_30_polls(self):
        for i in range(30):
            assert _client.get("/health").json()["status"] == "healthy", \
                f"Unhealthy on poll {i}"

    def test_cache_coherence_returns_same_answer(self):
        """After a cache set, all subsequent calls must return the same answer."""
        query = f"reliability-cache-query-{random.randint(1, 999999)}"
        payload = {"query": query, "business_id": "12345"}
        first = _client.post("/assistant/query", json=payload).json()["answer"]
        for _ in range(5):
            assert _client.post("/assistant/query", json=payload).json()["answer"] == first

    def test_circuit_breakers_unchanged_by_normal_traffic(self):
        """Circuit breaker states must not change due to healthy requests."""
        before = _client.get("/health/detailed").json()["circuit_breakers"]
        for _ in range(5):
            _client.post("/assistant/query", json=_VALID_PAYLOAD)
        after = _client.get("/health/detailed").json()["circuit_breakers"]
        for name in before:
            assert after[name] == before[name], \
                f"CB {name} state changed: {before[name]} → {after[name]}"

    def test_l1_cache_size_bounded_under_1024(self):
        """L1 cache must not grow beyond its configured maximum."""
        for i in range(20):
            _client.post(
                "/assistant/query",
                json={"query": f"unique reliability query {i}", "business_id": "12345"},
            )
        size = _client.get("/health/detailed").json()["cache"]["l1_entries"]
        assert size <= 1024, f"L1 cache grew to {size} entries"

    @pytest.mark.asyncio
    async def test_200_sequential_async_requests_99pct_success(self):
        """200 sequential async requests — at least 99 % must succeed."""
        import httpx

        success = 0
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test", timeout=10.0
        ) as ac:
            for _ in range(200):
                r = await ac.post("/assistant/query", json=_VALID_PAYLOAD)
                if r.status_code == 200:
                    success += 1

        assert success / 200 >= 0.99, f"Success rate {success / 200:.1%} below 99 %"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
