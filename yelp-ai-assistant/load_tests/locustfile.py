"""
Locust Load Test — Yelp-Style AI Assistant
==========================================

Simulates realistic production traffic (100k+ concurrent users) against
the FastAPI server at POST /assistant/query and GET /health.

User scenarios
--------------
  AssistantUser      — submits realistic natural-language queries across
                       all four intent types (operational, amenity, quality,
                       photo), weighted to reflect real-world traffic.

  HealthCheckUser    — lightweight liveness probe; represents monitoring
                       agents and load balancers.

  HeavyQueryUser     — simulates power users making back-to-back queries
                       with no wait; stress-tests the circuit breakers and
                       concurrency limits.

Running
-------
  # Web UI (recommended for 100k simulation)
  locust -f load_tests/locustfile.py --host http://localhost:8000

  # Headless, 100 concurrent users, spawn 10/s, run 60 s
  locust -f load_tests/locustfile.py \\
         --host http://localhost:8000 \\
         --headless -u 100 -r 10 --run-time 60s

  # Full 100k simulation (requires a real server cluster)
  locust -f load_tests/locustfile.py \\
         --host http://localhost:8000 \\
         --headless -u 100000 -r 500 --run-time 300s

Metrics to watch
----------------
  - p95 response time  < 1200 ms  (TDD §8.2)
  - error rate         < 1 %
  - cache hit rate     visible in /health/detailed
"""

from __future__ import annotations

import json
import random
from typing import Dict, List

from locust import HttpUser, between, events, task


# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

_BUSINESS_IDS: List[str] = ["12345", "demo-001", "demo-002", "biz-xyz"]

_OPERATIONAL_QUERIES: List[str] = [
    "Is it open right now?",
    "What time do they close on Friday?",
    "Are they open on Sunday morning?",
    "What are the weekend hours?",
    "Are they open late tonight?",
]

_AMENITY_QUERIES: List[str] = [
    "Do they have a heated patio?",
    "Is there parking nearby?",
    "Is the restaurant wheelchair accessible?",
    "Do they have wifi?",
    "Do they offer vegan options?",
    "Is it dog friendly?",
]

_QUALITY_QUERIES: List[str] = [
    "Is this place good for a romantic date?",
    "What do people say about the food quality?",
    "Is it good for large groups?",
    "How are the cocktails?",
    "Is the service fast?",
]

_PHOTO_QUERIES: List[str] = [
    "Show me photos of the outdoor seating",
    "Can I see pictures of the patio?",
    "What does the interior look like?",
    "Show me food photos",
]


def _random_payload(query_list: List[str]) -> Dict:
    return {
        "query": random.choice(query_list),
        "business_id": random.choice(_BUSINESS_IDS),
        "user_context": {
            "location": random.choice(["NYC", "SF", "LA", "Chicago"]),
        },
    }


# ---------------------------------------------------------------------------
# AssistantUser — primary realistic traffic
# ---------------------------------------------------------------------------

class AssistantUser(HttpUser):
    """
    Realistic mixed-intent user.

    Wait 1–3 seconds between tasks — simulates a human browsing a business
    page and asking follow-up questions.
    """

    wait_time = between(1, 3)

    # ── Operational (40 % weight — most common query type) ──────────────────

    @task(4)
    def ask_operational(self):
        with self.client.post(
            "/assistant/query",
            json=_random_payload(_OPERATIONAL_QUERIES),
            catch_response=True,
            name="/assistant/query [operational]",
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"HTTP {resp.status_code}")

    # ── Amenity (30 % weight) ────────────────────────────────────────────────

    @task(3)
    def ask_amenity(self):
        with self.client.post(
            "/assistant/query",
            json=_random_payload(_AMENITY_QUERIES),
            catch_response=True,
            name="/assistant/query [amenity]",
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"HTTP {resp.status_code}")

    # ── Quality (20 % weight) ────────────────────────────────────────────────

    @task(2)
    def ask_quality(self):
        with self.client.post(
            "/assistant/query",
            json=_random_payload(_QUALITY_QUERIES),
            catch_response=True,
            name="/assistant/query [quality]",
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"HTTP {resp.status_code}")

    # ── Photo (10 % weight) ──────────────────────────────────────────────────

    @task(1)
    def ask_photo(self):
        with self.client.post(
            "/assistant/query",
            json=_random_payload(_PHOTO_QUERIES),
            catch_response=True,
            name="/assistant/query [photo]",
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"HTTP {resp.status_code}")

    # ── Health check (occasional) ────────────────────────────────────────────

    @task(1)
    def check_health(self):
        self.client.get("/health", name="/health")


# ---------------------------------------------------------------------------
# HealthCheckUser — monitoring probes
# ---------------------------------------------------------------------------

class HealthCheckUser(HttpUser):
    """
    Lightweight liveness / readiness probe user.

    Represents load balancers and monitoring agents.
    No wait between checks — hammers the health endpoints continuously.
    """

    wait_time = between(0.5, 1.0)

    @task(3)
    def liveness(self):
        with self.client.get(
            "/health",
            catch_response=True,
            name="/health [liveness]",
        ) as resp:
            if resp.status_code == 200 and resp.json().get("status") == "healthy":
                resp.success()
            else:
                resp.failure("unhealthy response")

    @task(1)
    def readiness(self):
        with self.client.get(
            "/health/detailed",
            catch_response=True,
            name="/health/detailed [readiness]",
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"HTTP {resp.status_code}")


# ---------------------------------------------------------------------------
# HeavyQueryUser — power user / cache stress
# ---------------------------------------------------------------------------

class HeavyQueryUser(HttpUser):
    """
    Power user who sends back-to-back queries with minimal wait.

    Stress-tests the circuit breakers, concurrency semaphores, and L1 cache.
    Repeats the same query to exercise the cache hit path.
    """

    wait_time = between(0.1, 0.3)

    # Repeat the same question to generate cache hits
    _CACHED_QUERY = {
        "query": "Is it open right now?",
        "business_id": "12345",
    }

    @task(5)
    def repeated_cached_query(self):
        """Same query repeatedly — should hit L1/L2 cache after first request."""
        with self.client.post(
            "/assistant/query",
            json=self._CACHED_QUERY,
            catch_response=True,
            name="/assistant/query [cache-stress]",
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"HTTP {resp.status_code}")

    @task(1)
    def burst_mixed(self):
        """Single random query."""
        all_queries = (
            _OPERATIONAL_QUERIES + _AMENITY_QUERIES
            + _QUALITY_QUERIES + _PHOTO_QUERIES
        )
        with self.client.post(
            "/assistant/query",
            json={
                "query": random.choice(all_queries),
                "business_id": random.choice(_BUSINESS_IDS),
            },
            catch_response=True,
            name="/assistant/query [burst]",
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"HTTP {resp.status_code}")


# ---------------------------------------------------------------------------
# Locust event hooks — custom statistics
# ---------------------------------------------------------------------------

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print(
        "\n"
        "════════════════════════════════════════════\n"
        "  Yelp-Style AI Assistant — Load Test\n"
        "  Target P95 latency: < 1200 ms (TDD §8.2)\n"
        "  Target error rate:  < 1 %\n"
        "════════════════════════════════════════════\n"
    )


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    stats = environment.stats.total
    p95 = stats.get_response_time_percentile(0.95) or 0
    rps = stats.current_rps
    err_pct = (
        (stats.num_failures / stats.num_requests * 100)
        if stats.num_requests > 0 else 0
    )

    p95_ok  = "✅" if p95 < 1200 else "❌"
    err_ok  = "✅" if err_pct < 1.0 else "❌"

    print(
        "\n"
        "════════════════════════════════════════════\n"
        "  Load Test Complete\n"
        f"  {p95_ok} P95 latency : {p95:.0f} ms  (target < 1200 ms)\n"
        f"  {err_ok} Error rate  : {err_pct:.2f} %  (target < 1 %)\n"
        f"     Requests/s  : {rps:.1f}\n"
        "════════════════════════════════════════════\n"
    )
