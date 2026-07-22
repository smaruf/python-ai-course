"""
locustfile.py — Load test for Trading AI Platform.

Simulates concurrent REST and WebSocket traffic.

Run (headless, 200 users, 60 s):
    locust -f scripts/load/locustfile.py \
        --headless -u 200 -r 20 --run-time 60s \
        --host http://localhost:8080
"""
from locust import HttpUser, task, between
import random


SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]


class TradingApiUser(HttpUser):
    """Simulates a retail trader using the REST API."""
    wait_time = between(0.5, 2)

    @task(3)
    def get_market_data(self):
        symbol = random.choice(SYMBOLS)
        with self.client.get(
            f"/api/market-data/{symbol}",
            name="/api/market-data/[symbol]",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Unexpected status {resp.status_code}")

    @task(2)
    def chat_propose_trade(self):
        symbol = random.choice(SYMBOLS)
        qty = random.randint(1, 500)
        with self.client.post(
            "/api/chat",
            json={"message": f"Buy {qty} shares of {symbol}"},
            name="/api/chat",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Unexpected status {resp.status_code}")
            elif resp.json().get("type") != "ProposedAction":
                resp.failure("Expected ProposedAction (HITL), got direct execution")

    @task(1)
    def get_wallet_balance(self):
        with self.client.get(
            "/api/payments/balance",
            headers={"X-Account-Id": "load-test-user"},
            name="/api/payments/balance",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Unexpected status {resp.status_code}")
