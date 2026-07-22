"""
test_e2e_trading.py — PyTest end-to-end tests for the Trading AI Platform.

Requires:
  - Spring Boot app running on http://localhost:8080
  - Mock FIX server running (start via mock_fix_server.py)
  - PostgreSQL accessible (see docker-compose.yml)

Run:
    pytest scripts/testing/test_e2e_trading.py -v
"""
import pytest
import requests
import psycopg2
import os
import time

BASE_URL = os.getenv("APP_URL", "http://localhost:8080")
DB_DSN   = os.getenv(
    "DB_DSN",
    "host=localhost dbname=tradingai user=tradingai ******"
)


@pytest.fixture(scope="session")
def db():
    """Return a live PostgreSQL connection for the test session."""
    conn = psycopg2.connect(DB_DSN)
    conn.autocommit = True
    yield conn
    conn.close()


@pytest.fixture(scope="session", autouse=True)
def wait_for_app():
    """Block until the Spring Boot actuator health endpoint is UP."""
    for _ in range(30):
        try:
            r = requests.get(f"{BASE_URL}/actuator/health", timeout=2)
            if r.status_code == 200 and r.json().get("status") == "UP":
                return
        except requests.ConnectionError:
            pass
        time.sleep(2)
    pytest.fail("Spring Boot app did not become healthy within 60 seconds")


class TestAIOrderFlow:
    """AI chat → propose trade → confirm → FIX order → ExecutionReport → ledger."""

    def test_propose_trade_via_ai(self):
        """AI returns a ProposedAction — does NOT execute automatically (HITL)."""
        payload = {"message": "Buy 100 shares of AAPL at market price"}
        resp = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("type") == "ProposedAction", "Expected HITL confirmation step"
        assert body["action"]["symbol"] == "AAPL"
        assert body["action"]["qty"] == 100

    def test_confirm_trade_creates_fix_order(self, db):
        """Confirming a ProposedAction should route a FIX NewOrderSingle."""
        # Confirm the proposed trade
        resp = requests.post(
            f"{BASE_URL}/api/orders/confirm",
            json={"symbol": "AAPL", "qty": 100, "side": "BUY"},
            timeout=10,
        )
        assert resp.status_code == 201
        order_id = resp.json()["orderId"]

        # Allow async FIX/Kafka processing
        time.sleep(2)

        # Verify the order is persisted in the ledger
        with db.cursor() as cur:
            cur.execute("SELECT status FROM orders WHERE id = %s", (order_id,))
            row = cur.fetchone()
        assert row is not None, f"Order {order_id} not found in DB"
        assert row[0] in ("FILLED", "PENDING", "NEW"), f"Unexpected status: {row[0]}"


class TestPaymentLedger:
    """Double-entry ledger integrity checks."""

    def test_fund_account(self, db):
        resp = requests.post(
            f"{BASE_URL}/api/payments/fund",
            json={"accountId": "test-account-1", "amount": 10000, "currency": "USD"},
            timeout=10,
        )
        assert resp.status_code == 200

        with db.cursor() as cur:
            cur.execute(
                "SELECT balance FROM wallets WHERE account_id = %s",
                ("test-account-1",),
            )
            row = cur.fetchone()
        assert row is not None
        assert float(row[0]) >= 10000
