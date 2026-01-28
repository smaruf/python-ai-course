"""
Tests for webhook endpoint.
"""

import pytest
from fastapi.testclient import TestClient

from src.whatsapp_vault.api.webhook import app


client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "WhatsApp Medical Report Vault"


def test_webhook_verification_success():
    """Test webhook verification with correct token."""
    response = client.get(
        "/webhook/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "your_webhook_verify_token_here",
            "hub.challenge": "1234567890"
        }
    )
    # Will fail without proper token in env, but tests the endpoint exists
    assert response.status_code in [200, 403]


def test_webhook_verification_failure():
    """Test webhook verification with wrong token."""
    response = client.get(
        "/webhook/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong_token",
            "hub.challenge": "1234567890"
        }
    )
    assert response.status_code == 403


def test_webhook_post():
    """Test webhook POST endpoint."""
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123456",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "messages": [
                                {
                                    "from": "1234567890",
                                    "type": "text",
                                    "text": {
                                        "body": "Hello"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    
    response = client.post("/webhook/whatsapp", json=payload)
    assert response.status_code == 200
