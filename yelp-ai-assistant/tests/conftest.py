"""
Shared pytest fixtures for the Yelp-Style AI Assistant test suite.

Provides a session-scoped TestClient that properly runs the FastAPI lifespan
(startup/shutdown), ensuring demo data is seeded before any test runs.
"""

from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from main import app  # noqa: E402


@pytest.fixture(scope="session")
def started_client():
    """Session-scoped TestClient with lifespan (startup + shutdown) active."""
    with TestClient(app) as client:
        yield client
