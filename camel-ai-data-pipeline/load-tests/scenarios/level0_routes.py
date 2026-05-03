"""
Level 0 — Fundamentals: REST endpoint load scenarios.

Tests:
  POST /api/message  — echo endpoint (basic routing)
  GET  /actuator/health — Spring Boot health check
"""

import json
import random
import string

from locust import HttpUser, between, task, tag


def _random_string(length: int = 16) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


class Level0User(HttpUser):
    """Simulates a client hammering the Level 0 REST routes."""

    wait_time = between(0.5, 2.0)
    weight = 3

    @tag("level0")
    @task(3)
    def post_message(self) -> None:
        """POST a JSON message to the echo endpoint."""
        payload = {
            "type": random.choice(["alert", "info", "debug"]),
            "message": _random_string(32),
            "timestamp": "2024-01-01T00:00:00Z",
        }
        with self.client.post(
            "/api/message",
            json=payload,
            headers={"Content-Type": "application/json"},
            catch_response=True,
            name="POST /api/message",
        ) as resp:
            if resp.status_code not in (200, 201):
                resp.failure(f"Unexpected status {resp.status_code}")

    @tag("level0", "health")
    @task(1)
    def health_check(self) -> None:
        """GET Spring Boot actuator health."""
        with self.client.get(
            "/actuator/health",
            catch_response=True,
            name="GET /actuator/health",
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Health check failed: {resp.status_code}")
            else:
                body = resp.json()
                if body.get("status") != "UP":
                    resp.failure(f"Health status not UP: {body}")
