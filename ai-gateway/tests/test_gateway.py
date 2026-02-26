#!/usr/bin/env python3
"""
Tests for the AI Gateway project
=================================

Covers:
  - CloudClient (mocked HTTP)
  - LocalClient  (mocked HTTP)
  - AIRouter circuit-breaker state machine
  - FastAPI endpoints via TestClient
"""

import sys
import os
import time
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

# ---------------------------------------------------------------------------
# Make sure the gateway package is importable from the test runner's cwd
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ===========================================================================
# CloudClient Tests
# ===========================================================================

class TestCloudClient:
    """Unit tests for CloudClient."""

    def test_health_check_success(self):
        from cloud_client import CloudClient

        client = CloudClient()
        with patch("cloud_client.requests.get") as mock_get:
            mock_get.return_value = MagicMock(status_code=200)
            assert client.health_check() is True

    def test_health_check_failure(self):
        from cloud_client import CloudClient
        import requests

        client = CloudClient()
        with patch("cloud_client.requests.get", side_effect=requests.exceptions.ConnectionError):
            assert client.health_check() is False

    def test_query_missing_api_key(self):
        from cloud_client import CloudClient

        client = CloudClient()
        with patch.dict(os.environ, {}, clear=True):
            # Ensure OPENAI_API_KEY is not set
            os.environ.pop("OPENAI_API_KEY", None)
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                client.query("Hello")

    def test_query_openai_success(self):
        from cloud_client import CloudClient

        client = CloudClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Cloud answer"}}]
        }
        mock_response.raise_for_status = MagicMock()

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch("cloud_client.requests.post", return_value=mock_response):
                result = client.query("What is Python?")
                assert result == "Cloud answer"

    def test_unsupported_provider_raises(self):
        from cloud_client import CloudClient

        client = CloudClient(provider="unknown")
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with pytest.raises(ValueError, match="Unsupported cloud provider"):
                client.query("test")


# ===========================================================================
# LocalClient Tests
# ===========================================================================

class TestLocalClient:
    """Unit tests for LocalClient."""

    def test_health_check_success(self):
        from local_client import LocalClient

        client = LocalClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        with patch("local_client.requests.get", return_value=mock_response):
            assert client.health_check() is True

    def test_health_check_failure(self):
        from local_client import LocalClient
        import requests

        client = LocalClient()
        with patch("local_client.requests.get", side_effect=requests.exceptions.ConnectionError):
            assert client.health_check() is False

    def test_query_success(self):
        from local_client import LocalClient

        client = LocalClient()
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Local answer"}
        mock_response.raise_for_status = MagicMock()

        with patch("local_client.requests.post", return_value=mock_response):
            result = client.query("What is Python?")
            assert result == "Local answer"

    def test_custom_base_url(self):
        from local_client import LocalClient

        client = LocalClient(base_url="http://custom-host:11434")
        assert client.base_url == "http://custom-host:11434"

    def test_trailing_slash_stripped(self):
        from local_client import LocalClient

        client = LocalClient(base_url="http://localhost:11434/")
        assert not client.base_url.endswith("/")


# ===========================================================================
# AIRouter (Circuit Breaker) Tests
# ===========================================================================

class TestAIRouter:
    """Unit tests for the AIRouter circuit-breaker logic."""

    def _make_router(self, failure_threshold=3, recovery_timeout=300):
        from router import AIRouter

        cloud = MagicMock()
        local = MagicMock()
        local.query.return_value = "Local answer"
        return AIRouter(
            cloud=cloud,
            local=local,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
        )

    # --- Happy path ---

    def test_cloud_used_when_available(self):
        from router import CircuitState

        router = self._make_router()
        router.cloud.query.return_value = "Cloud answer"

        result = router.query("Hello")
        assert result["response"] == "Cloud answer"
        assert result["backend"] == "cloud"
        assert result["state"] == CircuitState.CLOSED

    def test_falls_back_to_local_on_single_failure(self):
        router = self._make_router()
        router.cloud.query.side_effect = RuntimeError("timeout")

        result = router.query("Hello")
        assert result["response"] == "Local answer"
        assert result["backend"] == "local"

    # --- Circuit opens after threshold ---

    def test_circuit_opens_after_threshold_failures(self):
        from router import CircuitState

        router = self._make_router(failure_threshold=3)
        router.cloud.query.side_effect = RuntimeError("down")

        for _ in range(3):
            router.query("Hello")

        assert router.state == CircuitState.OPEN

    def test_circuit_stays_open_uses_local(self):
        from router import CircuitState

        router = self._make_router(failure_threshold=2)
        router.cloud.query.side_effect = RuntimeError("down")

        router.query("1")
        router.query("2")  # circuit opens here

        # Next query should NOT call cloud at all
        router.cloud.query.side_effect = None  # Remove side-effect
        router.cloud.query.return_value = "Cloud answer"

        result = router.query("3")
        assert result["backend"] == "local"

    # --- Recovery ---

    def test_circuit_transitions_to_half_open_after_timeout(self):
        from router import CircuitState

        router = self._make_router(failure_threshold=1, recovery_timeout=1)
        router.cloud.query.side_effect = RuntimeError("down")
        router.query("fail")  # opens the circuit

        assert router.state == CircuitState.OPEN

        time.sleep(1.1)  # wait for recovery timeout

        router.cloud.query.side_effect = None
        router.cloud.query.return_value = "Recovered"
        result = router.query("recover")

        assert result["backend"] == "cloud"
        assert router.state == CircuitState.CLOSED

    def test_manual_reset(self):
        from router import CircuitState

        router = self._make_router(failure_threshold=1)
        router.cloud.query.side_effect = RuntimeError("down")
        router.query("fail")

        assert router.state == CircuitState.OPEN

        router.reset()
        assert router.state == CircuitState.CLOSED
        assert router._failure_count == 0

    # --- Failure count resets on success ---

    def test_failure_count_resets_on_cloud_success(self):
        router = self._make_router(failure_threshold=3)
        router.cloud.query.side_effect = RuntimeError("down")
        router.query("fail 1")
        router.query("fail 2")

        # Circuit is still CLOSED (below threshold), now recover
        router.cloud.query.side_effect = None
        router.cloud.query.return_value = "ok"
        router.query("success")

        assert router._failure_count == 0


# ===========================================================================
# FastAPI Endpoint Tests
# ===========================================================================

class TestAPIEndpoints:
    """Integration tests for the FastAPI gateway endpoints."""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from unittest.mock import patch

        # Patch the router used inside ai_gateway so no real HTTP calls are made
        with patch("ai_gateway._router") as mock_router:
            mock_router.query.return_value = {
                "response": "Test answer",
                "backend": "cloud",
                "state": "closed",
            }
            mock_router.state = "closed"
            mock_router.reset = MagicMock()

            import ai_gateway
            with TestClient(ai_gateway.app) as tc:
                tc._mock_router = mock_router
                yield tc

    def test_query_endpoint_success(self, client):
        response = client.post("/ai/query", json={"prompt": "What is Python?"})
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Test answer"
        assert data["backend"] == "cloud"

    def test_query_endpoint_empty_prompt(self, client):
        response = client.post("/ai/query", json={"prompt": ""})
        assert response.status_code == 422  # Pydantic validation error

    def test_health_endpoint(self, client):
        with patch("ai_gateway._cloud") as mock_cloud, \
             patch("ai_gateway._local") as mock_local:
            mock_cloud.health_check.return_value = True
            mock_local.health_check.return_value = False

            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert "cloud_available" in data
            assert "local_available" in data
            assert "circuit_state" in data

    def test_reset_endpoint(self, client):
        response = client.post("/admin/reset")
        assert response.status_code == 200
        assert "reset" in response.json()["message"].lower()

    def test_query_endpoint_all_backends_fail(self):
        from fastapi.testclient import TestClient

        with patch("ai_gateway._router") as mock_router:
            mock_router.query.side_effect = RuntimeError("all down")

            import ai_gateway
            with TestClient(ai_gateway.app) as tc:
                response = tc.post("/ai/query", json={"prompt": "hello"})
                assert response.status_code == 503


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
