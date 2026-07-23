import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_requires_file():
    response = client.post("/api/documents/upload")
    assert response.status_code == 422  # Unprocessable Entity — file is required
