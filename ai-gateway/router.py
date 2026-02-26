#!/usr/bin/env python3
"""
AI Router — Circuit Breaker + Health-Check Failover
====================================================

Implements a circuit-breaker pattern that:
  • Prefers the cloud LLM (primary)
  • Automatically falls back to the local LLM (fallback) when the cloud
    experiences consecutive failures or becomes unreachable
  • Periodically re-probes the cloud to restore normal operation

State machine:
    CLOSED  → normal operation, cloud is used
    OPEN    → cloud is marked DOWN, all requests go to local
    HALF-OPEN → trial request sent to cloud; if it succeeds, move to CLOSED
"""

import time
import logging
from enum import Enum
from threading import Lock
from typing import Optional

from cloud_client import CloudClient
from local_client import LocalClient

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    CLOSED = "closed"       # Cloud healthy — use cloud
    OPEN = "open"           # Cloud down — use local
    HALF_OPEN = "half_open" # Testing cloud recovery


class AIRouter:
    """
    Routes AI queries between cloud and local backends using a circuit breaker.

    Args:
        cloud: CloudClient instance (primary backend).
        local: LocalClient instance (fallback backend).
        failure_threshold: Number of consecutive cloud failures before opening circuit.
        recovery_timeout: Seconds to wait before attempting cloud recovery.
    """

    def __init__(
        self,
        cloud: Optional[CloudClient] = None,
        local: Optional[LocalClient] = None,
        failure_threshold: int = 3,
        recovery_timeout: int = 300,
    ):
        self.cloud = cloud or CloudClient()
        self.local = local or LocalClient()
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._opened_at: Optional[float] = None
        self._lock = Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def state(self) -> CircuitState:
        return self._state

    def query(self, prompt: str) -> dict:
        """
        Route a query to the best available backend.

        Returns a dict with keys:
            response (str): The model's answer.
            backend  (str): Which backend was used ("cloud" or "local").
            state    (str): Circuit state after this call.
        """
        with self._lock:
            self._maybe_attempt_recovery()

            if self._state in (CircuitState.CLOSED, CircuitState.HALF_OPEN):
                try:
                    response = self.cloud.query(prompt)
                    self._on_cloud_success()
                    return {"response": response, "backend": "cloud", "state": self._state}
                except Exception as exc:
                    logger.warning("Cloud query failed: %s", exc)
                    self._on_cloud_failure()

            # OPEN state or cloud just failed → use local
            response = self.local.query(prompt)
            return {"response": response, "backend": "local", "state": self._state}

    def reset(self) -> None:
        """Manually reset the circuit breaker to CLOSED state."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._opened_at = None
            logger.info("Circuit breaker manually reset to CLOSED")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _on_cloud_success(self) -> None:
        self._failure_count = 0
        if self._state == CircuitState.HALF_OPEN:
            logger.info("Cloud recovered — circuit CLOSED")
        self._state = CircuitState.CLOSED
        self._opened_at = None

    def _on_cloud_failure(self) -> None:
        self._failure_count += 1
        logger.warning(
            "Cloud failure %d/%d", self._failure_count, self.failure_threshold
        )
        if self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            self._opened_at = time.monotonic()
            logger.error(
                "Circuit OPEN — switching to local LLM for %ds", self.recovery_timeout
            )

    def _maybe_attempt_recovery(self) -> None:
        """Transition from OPEN to HALF_OPEN once the recovery timeout expires."""
        if (
            self._state == CircuitState.OPEN
            and self._opened_at is not None
            and (time.monotonic() - self._opened_at) >= self.recovery_timeout
        ):
            logger.info("Recovery timeout elapsed — circuit HALF-OPEN, probing cloud")
            self._state = CircuitState.HALF_OPEN
