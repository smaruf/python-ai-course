"""
Level 3 — AI Integration: load scenarios for the AI enrichment REST API.

Tests:
  POST /api/enrich/sentiment  — single news enrichment (AI call)
  POST /api/enrich/batch      — batch news enrichment
  GET  /api/enrich/status     — pipeline health / queue depth
"""

import random
import uuid

from locust import HttpUser, between, task, tag


_SAMPLE_HEADLINES = [
    "Apple beats Q3 earnings expectations by 12 percent",
    "Federal Reserve signals rate pause amid cooling inflation",
    "Tesla deliveries disappoint analysts for second straight quarter",
    "OpenAI launches new reasoning model with 200k context window",
    "Amazon Web Services outage disrupts cloud services globally",
    "Microsoft Azure revenue surges 29 percent year-over-year",
    "Oil prices drop as OPEC fails to reach output agreement",
    "Biotech startup raises 500 million for cancer immunotherapy",
]

_SAMPLE_BODIES = [
    "The company reported revenue of $89.5 billion, surpassing consensus estimates. "
    "Strong iPhone and services segments drove the outperformance.",
    "Central bank officials cited easing wage growth and stabilising energy costs "
    "as key factors supporting the decision to hold rates steady.",
    "The electric vehicle maker delivered 435,000 units versus the expected 470,000. "
    "Supply chain bottlenecks in Germany were cited as the primary driver.",
]


def _random_news_event() -> dict:
    return {
        "id": str(uuid.uuid4()),
        "title": random.choice(_SAMPLE_HEADLINES),
        "body": random.choice(_SAMPLE_BODIES),
        "source": random.choice(["Reuters", "Bloomberg", "CNBC", "WSJ"]),
        "timestamp": "2024-01-15T09:30:00Z",
    }


class Level3AiEnrichUser(HttpUser):
    """Simulates clients sending news articles for AI enrichment."""

    wait_time = between(1.0, 4.0)
    weight = 2

    @tag("level3", "ai")
    @task(4)
    def enrich_single_article(self) -> None:
        """POST a single news article for AI sentiment enrichment."""
        with self.client.post(
            "/api/enrich/sentiment",
            json=_random_news_event(),
            headers={"Content-Type": "application/json"},
            catch_response=True,
            name="POST /api/enrich/sentiment",
        ) as resp:
            if resp.status_code not in (200, 202):
                resp.failure(f"Unexpected status {resp.status_code}")
                return
            body = resp.json()
            if "sentiment" not in body and "status" not in body:
                resp.failure("Response missing 'sentiment' field")

    @tag("level3", "ai", "batch")
    @task(1)
    def enrich_batch(self) -> None:
        """POST a batch of news articles for bulk enrichment."""
        batch_size = random.randint(2, 5)
        payload = {"items": [_random_news_event() for _ in range(batch_size)]}
        with self.client.post(
            "/api/enrich/batch",
            json=payload,
            headers={"Content-Type": "application/json"},
            catch_response=True,
            name="POST /api/enrich/batch",
        ) as resp:
            if resp.status_code not in (200, 202):
                resp.failure(f"Batch enrichment failed: {resp.status_code}")

    @tag("level3", "status")
    @task(2)
    def pipeline_status(self) -> None:
        """GET pipeline processing status and queue depth."""
        with self.client.get(
            "/api/enrich/status",
            catch_response=True,
            name="GET /api/enrich/status",
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Status endpoint failed: {resp.status_code}")
