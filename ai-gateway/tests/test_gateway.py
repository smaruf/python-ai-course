#!/usr/bin/env python3
"""
Tests for the AI Gateway project
=================================

Covers:
  - CopilotClient (mocked HTTP)
  - CloudClient   (mocked HTTP)
  - LocalClient   (mocked HTTP)
  - AIRouter 3-tier circuit-breaker state machine
  - FastAPI endpoints via TestClient
"""

import sys
import os
import time
import pytest
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Make sure the gateway package is importable from the test runner's cwd
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ===========================================================================
# CopilotClient Tests
# ===========================================================================

class TestCopilotClient:
    """Unit tests for CopilotClient (primary backend)."""

    def test_health_check_success(self):
        from copilot_client import CopilotClient

        client = CopilotClient()
        with patch("copilot_client.requests.get") as mock_get:
            mock_get.return_value = MagicMock(status_code=200)
            assert client.health_check() is True

    def test_health_check_failure(self):
        from copilot_client import CopilotClient
        import requests

        client = CopilotClient()
        with patch("copilot_client.requests.get", side_effect=requests.exceptions.ConnectionError):
            assert client.health_check() is False

    def test_query_uses_env_token(self):
        from copilot_client import CopilotClient

        client = CopilotClient()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Copilot answer"}}]
        }
        mock_response.raise_for_status = MagicMock()

        with patch.dict(os.environ, {"GITHUB_COPILOT_TOKEN": "test-token"}):
            with patch("copilot_client.requests.post", return_value=mock_response) as mock_post:
                result = client.query("What is Python?")
                assert result == "Copilot answer"
                # Verify Bearer token was sent
                call_headers = mock_post.call_args.kwargs["headers"]
                assert call_headers["Authorization"] == "Bearer test-token"

    def test_query_missing_token_raises(self):
        from copilot_client import CopilotClient

        client = CopilotClient()
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("GITHUB_COPILOT_TOKEN", None)
            # Also ensure no config file exists by patching os.path.exists
            with patch("copilot_client.os.path.exists", return_value=False):
                with pytest.raises(ValueError, match="GITHUB_COPILOT_TOKEN"):
                    client.query("Hello")

    def test_query_reads_vscode_config_token(self, tmp_path):
        """Token can be read from VS Code Copilot hosts.json."""
        from copilot_client import CopilotClient, _TOKEN_CONFIG_PATHS

        config_file = tmp_path / "hosts.json"
        config_file.write_text('{"github.com": {"oauth_token": "vscode-token"}}')

        client = CopilotClient()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "VS Code token answer"}}]
        }
        mock_response.raise_for_status = MagicMock()

        # Remove env var and inject our temp config path
        patched_paths = [str(config_file)]
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("GITHUB_COPILOT_TOKEN", None)
            with patch("copilot_client._TOKEN_CONFIG_PATHS", patched_paths):
                with patch("copilot_client.requests.post", return_value=mock_response):
                    result = client.query("Hello")
                    assert result == "VS Code token answer"


# ===========================================================================
# CloudClient Tests
# ===========================================================================

class TestCloudClient:
    """Unit tests for CloudClient (secondary backend)."""

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
    """Unit tests for LocalClient (tertiary / offline fallback)."""

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
# AIRouter (3-Tier Circuit Breaker) Tests
# ===========================================================================

class TestAIRouter:
    """Unit tests for the AIRouter 3-tier circuit-breaker logic."""

    def _make_router(self, failure_threshold=3, recovery_timeout=300):
        from router import AIRouter

        copilot = MagicMock()
        cloud = MagicMock()
        local = MagicMock()
        local.query.return_value = "Local answer"
        return AIRouter(
            copilot=copilot,
            cloud=cloud,
            local=local,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
        )

    # --- Tier 1: Copilot (primary) ---

    def test_copilot_used_when_available(self):
        from router import CircuitState

        router = self._make_router()
        router.copilot.query.return_value = "Copilot answer"

        result = router.query("Hello")
        assert result["response"] == "Copilot answer"
        assert result["backend"] == "copilot"
        assert result["state"] == CircuitState.CLOSED
        router.cloud.query.assert_not_called()

    def test_falls_back_to_cloud_when_copilot_fails(self):
        router = self._make_router()
        router.copilot.query.side_effect = RuntimeError("copilot down")
        router.cloud.query.return_value = "Cloud answer"

        result = router.query("Hello")
        assert result["response"] == "Cloud answer"
        assert result["backend"] == "cloud"

    def test_falls_back_to_local_when_both_cloud_tiers_fail(self):
        router = self._make_router()
        router.copilot.query.side_effect = RuntimeError("copilot down")
        router.cloud.query.side_effect = RuntimeError("cloud down")

        result = router.query("Hello")
        assert result["response"] == "Local answer"
        assert result["backend"] == "local"

    # --- Circuit opens after threshold ---

    def test_copilot_circuit_opens_after_threshold_failures(self):
        from router import CircuitState

        router = self._make_router(failure_threshold=3)
        router.copilot.query.side_effect = RuntimeError("down")
        router.cloud.query.return_value = "Cloud fallback"

        for _ in range(3):
            router.query("Hello")

        assert router._tier["copilot"]["state"] == CircuitState.OPEN

    def test_cloud_circuit_opens_after_threshold_failures(self):
        from router import CircuitState

        router = self._make_router(failure_threshold=2)
        router.copilot.query.side_effect = RuntimeError("down")
        router.cloud.query.side_effect = RuntimeError("down")

        for _ in range(2):
            router.query("Hello")

        assert router._tier["cloud"]["state"] == CircuitState.OPEN

    def test_copilot_circuit_open_skips_copilot(self):
        from router import CircuitState

        router = self._make_router(failure_threshold=1)
        router.copilot.query.side_effect = RuntimeError("down")
        router.cloud.query.return_value = "Cloud answer"

        router.query("fail")  # opens copilot circuit
        assert router._tier["copilot"]["state"] == CircuitState.OPEN

        # Now copilot circuit is OPEN — should go straight to cloud
        router.copilot.query.side_effect = None
        router.copilot.query.return_value = "Should not be called"
        result = router.query("next")

        assert result["backend"] == "cloud"
        router.copilot.query.assert_called_once()  # only called once (during the failing query)

    # --- Recovery ---

    def test_copilot_circuit_recovers_after_timeout(self):
        from router import CircuitState

        router = self._make_router(failure_threshold=1, recovery_timeout=1)
        router.copilot.query.side_effect = RuntimeError("down")
        router.cloud.query.return_value = "Cloud fallback"
        router.query("fail")

        assert router._tier["copilot"]["state"] == CircuitState.OPEN

        time.sleep(1.1)

        router.copilot.query.side_effect = None
        router.copilot.query.return_value = "Copilot recovered"
        result = router.query("recover")

        assert result["backend"] == "copilot"
        assert router._tier["copilot"]["state"] == CircuitState.CLOSED

    def test_manual_reset_clears_both_circuits(self):
        from router import CircuitState

        router = self._make_router(failure_threshold=1)
        router.copilot.query.side_effect = RuntimeError("down")
        router.cloud.query.side_effect = RuntimeError("down")
        router.query("fail")

        assert router._tier["copilot"]["state"] == CircuitState.OPEN
        assert router._tier["cloud"]["state"] == CircuitState.OPEN

        router.reset()
        assert router._tier["copilot"]["state"] == CircuitState.CLOSED
        assert router._tier["cloud"]["state"] == CircuitState.CLOSED
        assert router._tier["copilot"]["failures"] == 0
        assert router._tier["cloud"]["failures"] == 0

    def test_failure_count_resets_on_copilot_success(self):
        router = self._make_router(failure_threshold=3)
        router.copilot.query.side_effect = RuntimeError("down")
        router.cloud.query.return_value = "cloud"
        router.query("fail 1")
        router.query("fail 2")

        # Still below threshold — now recover
        router.copilot.query.side_effect = None
        router.copilot.query.return_value = "ok"
        router.query("success")

        assert router._tier["copilot"]["failures"] == 0


# ===========================================================================
# FastAPI Endpoint Tests
# ===========================================================================

class TestAPIEndpoints:
    """Integration tests for the FastAPI gateway endpoints."""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient

        with patch("ai_gateway._router") as mock_router:
            mock_router.query.return_value = {
                "response": "Test answer",
                "backend": "copilot",
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
        assert data["backend"] == "copilot"

    def test_query_endpoint_empty_prompt(self, client):
        response = client.post("/ai/query", json={"prompt": ""})
        assert response.status_code == 422  # Pydantic validation error

    def test_health_endpoint_includes_copilot(self, client):
        with patch("ai_gateway._copilot") as mock_copilot, \
             patch("ai_gateway._cloud") as mock_cloud, \
             patch("ai_gateway._local") as mock_local:
            mock_copilot.health_check.return_value = True
            mock_cloud.health_check.return_value = True
            mock_local.health_check.return_value = False

            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert "copilot_available" in data
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
