"""
Level 6 — Vector & Semantic Layer: load scenarios for the RAG REST API.

Tests:
  POST /api/ask           — natural language question → RAG answer
  POST /api/embed         — embed a document and store it
  GET  /api/search        — semantic similarity search
"""

import random
import uuid

from locust import HttpUser, between, task, tag


_MARKET_QUESTIONS = [
    "What happened with Apple earnings last quarter?",
    "Are there any anomalies in Tesla stock movement today?",
    "What is the current sentiment around Federal Reserve rate decisions?",
    "Summarise recent news about Amazon cloud services",
    "What are analysts saying about oil prices this week?",
    "How is Microsoft performing versus earnings estimates?",
    "Any news about biotech sector this month?",
    "What caused the recent drop in S&P 500?",
]

_SAMPLE_DOCUMENTS = [
    "Apple Inc reported record services revenue of $24.2 billion in Q3 2024, "
    "up 14 percent year-over-year. CEO Tim Cook highlighted AI integration in products.",
    "The Federal Reserve held benchmark interest rates unchanged at 5.25-5.50 percent. "
    "Chair Powell signalled data-dependency for future decisions.",
    "Brent crude fell below $75 per barrel after OPEC+ members failed to agree on "
    "production cut extensions, sending energy stocks lower.",
]


class Level6RagUser(HttpUser):
    """Simulates clients querying the RAG pipeline for market intelligence."""

    wait_time = between(1.5, 5.0)
    weight = 2

    @tag("level6", "rag", "ask")
    @task(5)
    def ask_question(self) -> None:
        """POST a natural language market question to the RAG endpoint."""
        question = random.choice(_MARKET_QUESTIONS)
        with self.client.post(
            "/api/ask",
            json={"question": question},
            headers={"Content-Type": "application/json"},
            catch_response=True,
            name="POST /api/ask",
        ) as resp:
            if resp.status_code not in (200, 202):
                resp.failure(f"RAG ask failed: {resp.status_code}")

    @tag("level6", "embed")
    @task(2)
    def embed_document(self) -> None:
        """POST a document to be embedded and stored in the vector DB."""
        payload = {
            "id": str(uuid.uuid4()),
            "text": random.choice(_SAMPLE_DOCUMENTS),
            "metadata": {
                "source": random.choice(["Reuters", "Bloomberg", "CNBC"]),
                "symbol": random.choice(["AAPL", "MSFT", "GOOGL", "AMZN"]),
            },
        }
        with self.client.post(
            "/api/embed",
            json=payload,
            headers={"Content-Type": "application/json"},
            catch_response=True,
            name="POST /api/embed",
        ) as resp:
            if resp.status_code not in (200, 201, 202):
                resp.failure(f"Embed document failed: {resp.status_code}")

    @tag("level6", "search")
    @task(3)
    def semantic_search(self) -> None:
        """GET semantic similarity search results for a query."""
        query = random.choice(_MARKET_QUESTIONS)
        with self.client.get(
            "/api/search",
            params={"q": query, "limit": 5},
            catch_response=True,
            name="GET /api/search",
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Semantic search failed: {resp.status_code}")
