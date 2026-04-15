"""
Level 7 — Finance Domain: load scenarios for the market data REST API.

Tests:
  POST /api/ticks           — ingest a simulated market tick
  GET  /api/alerts          — retrieve current anomaly alerts
  GET  /api/alerts/critical — retrieve only critical-severity alerts
  GET  /api/symbols/{sym}   — fetch recent ticks for a symbol
"""

import random
import time
import uuid

from locust import HttpUser, between, task, tag


_SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX"]


def _random_tick() -> dict:
    symbol = random.choice(_SYMBOLS)
    base_price = {
        "AAPL": 185.0, "MSFT": 415.0, "GOOGL": 175.0, "AMZN": 195.0,
        "TSLA": 180.0, "NVDA": 875.0, "META": 520.0, "NFLX": 650.0,
    }[symbol]
    # Occasional spike to trigger anomaly detection
    spike = random.random() < 0.02
    price_change_pct = random.uniform(-0.5, 0.5) if not spike else random.uniform(5.0, 15.0)
    price = round(base_price * (1 + price_change_pct / 100), 4)
    volume = random.randint(100, 10_000) if not spike else random.randint(50_000, 200_000)
    return {
        "id": str(uuid.uuid4()),
        "symbol": symbol,
        "price": price,
        "volume": volume,
        "side": random.choice(["BUY", "SELL"]),
        "timestamp": int(time.time() * 1000),
    }


class Level7MarketDataUser(HttpUser):
    """Simulates a high-frequency market data producer and alert consumer."""

    wait_time = between(0.1, 1.0)
    weight = 1

    @tag("level7", "ingest")
    @task(10)
    def ingest_tick(self) -> None:
        """POST a simulated market tick to the ingestion endpoint."""
        with self.client.post(
            "/api/ticks",
            json=_random_tick(),
            headers={"Content-Type": "application/json"},
            catch_response=True,
            name="POST /api/ticks",
        ) as resp:
            if resp.status_code not in (200, 201, 202):
                resp.failure(f"Tick ingestion failed: {resp.status_code}")

    @tag("level7", "alerts")
    @task(3)
    def get_alerts(self) -> None:
        """GET all current anomaly alerts."""
        with self.client.get(
            "/api/alerts",
            catch_response=True,
            name="GET /api/alerts",
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Alerts endpoint failed: {resp.status_code}")

    @tag("level7", "alerts", "critical")
    @task(2)
    def get_critical_alerts(self) -> None:
        """GET only critical-severity anomaly alerts."""
        with self.client.get(
            "/api/alerts/critical",
            catch_response=True,
            name="GET /api/alerts/critical",
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Critical alerts endpoint failed: {resp.status_code}")

    @tag("level7", "symbol")
    @task(4)
    def get_symbol_ticks(self) -> None:
        """GET recent ticks for a random symbol."""
        symbol = random.choice(_SYMBOLS)
        with self.client.get(
            f"/api/symbols/{symbol}",
            params={"limit": 50},
            catch_response=True,
            name="GET /api/symbols/{symbol}",
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Symbol ticks failed: {resp.status_code}")
