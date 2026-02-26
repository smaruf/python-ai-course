#!/usr/bin/env python3
"""
AI Router — 3-Tier Circuit Breaker + Health-Check Failover
===========================================================

Implements a 3-tier circuit-breaker pattern:

  Tier 1 (primary)   : GitHub Copilot
  Tier 2 (secondary) : Cloud LLM (OpenAI or other)
  Tier 3 (fallback)  : Local Ollama (no circuit breaker — always tried last)

Each of the first two tiers has its own independent circuit breaker:
    CLOSED    → tier is healthy, requests are sent to it
    OPEN      → tier is down, skip and try next tier
    HALF_OPEN → trial request sent to test recovery; success → CLOSED

Routing order:
    Copilot (CLOSED/HALF_OPEN) → Cloud (CLOSED/HALF_OPEN) → Local (always)
"""

import time
import logging
from enum import Enum
from threading import Lock
from typing import Optional

from copilot_client import CopilotClient
from cloud_client import CloudClient
from local_client import LocalClient

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    CLOSED = "closed"       # Tier healthy — in use
    OPEN = "open"           # Tier down — skipped
    HALF_OPEN = "half_open" # Testing recovery


class AIRouter:
    """
    Routes AI queries through a 3-tier failover chain using per-tier circuit breakers.

    Args:
        copilot: CopilotClient instance (primary backend).
        cloud: CloudClient instance (secondary backend).
        local: LocalClient instance (tertiary / offline fallback).
        failure_threshold: Consecutive failures before a tier's circuit opens.
        recovery_timeout: Seconds to wait before probing a failed tier again.
    """

    def __init__(
        self,
        copilot: Optional[CopilotClient] = None,
        cloud: Optional[CloudClient] = None,
        local: Optional[LocalClient] = None,
        failure_threshold: int = 3,
        recovery_timeout: int = 300,
    ):
        self.copilot = copilot or CopilotClient()
        self.cloud = cloud or CloudClient()
        self.local = local or LocalClient()
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        # Per-tier circuit state: keyed by tier name
        def _new_tier() -> dict:
            return {"state": CircuitState.CLOSED, "failures": 0, "opened_at": None}

        self._tier: dict[str, dict] = {
            "copilot": _new_tier(),
            "cloud": _new_tier(),
        }

        self._lock = Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def state(self) -> CircuitState:
        """Return the primary (Copilot) circuit state."""
        return self._tier["copilot"]["state"]

    def query(self, prompt: str) -> dict:
        """
        Route a query through the 3-tier failover chain.

        Returns a dict with keys:
            response (str): The model's answer.
            backend  (str): Which backend answered ("copilot", "cloud", or "local").
            state    (str): Primary (Copilot) circuit state after this call.
        """
        with self._lock:
            self._maybe_recover("copilot")
            self._maybe_recover("cloud")

            # Tier 1 — GitHub Copilot (primary)
            if self._tier["copilot"]["state"] in (CircuitState.CLOSED, CircuitState.HALF_OPEN):
                try:
                    response = self.copilot.query(prompt)
                    self._on_success("copilot")
                    return {"response": response, "backend": "copilot", "state": self._tier["copilot"]["state"]}
                except Exception as exc:
                    logger.warning("Copilot query failed: %s", exc)
                    self._on_failure("copilot")

            # Tier 2 — Cloud LLM (secondary)
            if self._tier["cloud"]["state"] in (CircuitState.CLOSED, CircuitState.HALF_OPEN):
                try:
                    response = self.cloud.query(prompt)
                    self._on_success("cloud")
                    return {"response": response, "backend": "cloud", "state": self._tier["copilot"]["state"]}
                except Exception as exc:
                    logger.warning("Cloud query failed: %s", exc)
                    self._on_failure("cloud")

            # Tier 3 — Local Ollama (fallback, no circuit breaker)
            response = self.local.query(prompt)
            return {"response": response, "backend": "local", "state": self._tier["copilot"]["state"]}

    def reset(self) -> None:
        """Manually reset both circuit breakers to CLOSED state."""
        with self._lock:
            for ts in self._tier.values():
                ts["state"] = CircuitState.CLOSED
                ts["failures"] = 0
                ts["opened_at"] = None
            logger.info("All circuit breakers reset to CLOSED")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _on_success(self, tier: str) -> None:
        ts = self._tier[tier]
        if ts["state"] == CircuitState.HALF_OPEN:
            logger.info("%s recovered — circuit CLOSED", tier.capitalize())
        ts["state"] = CircuitState.CLOSED
        ts["failures"] = 0
        ts["opened_at"] = None

    def _on_failure(self, tier: str) -> None:
        ts = self._tier[tier]
        ts["failures"] += 1
        logger.warning("%s failure %d/%d", tier.capitalize(), ts["failures"], self.failure_threshold)
        if ts["failures"] >= self.failure_threshold:
            ts["state"] = CircuitState.OPEN
            ts["opened_at"] = time.monotonic()
            logger.error(
                "%s circuit OPEN — skipping for %ds",
                tier.capitalize(), self.recovery_timeout
            )

    def _maybe_recover(self, tier: str) -> None:
        """Transition a tier from OPEN to HALF_OPEN when the recovery timeout expires."""
        ts = self._tier[tier]
        opened_at = ts["opened_at"]
        if (
            ts["state"] == CircuitState.OPEN
            and opened_at is not None
            and (time.monotonic() - opened_at) >= self.recovery_timeout
        ):
            logger.info("%s recovery timeout elapsed — HALF-OPEN, probing", tier.capitalize())
            ts["state"] = CircuitState.HALF_OPEN
