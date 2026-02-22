"""
Circuit Breaker + Timeout Wrapper
==================================

Provides resilience for downstream service calls at 100k+ concurrency
(TDD §13 Failure Modes & Mitigation).

Circuit Breaker States
----------------------
  CLOSED     — normal operation; failures are counted
  OPEN       — downstream is presumed failed; calls short-circuit immediately
  HALF_OPEN  — one probe call is allowed to test recovery

Timeout Wrapper
---------------
``with_timeout(coro, seconds)`` wraps any coroutine with an asyncio timeout.
On expiry it returns a configurable fallback value instead of raising, so the
calling code can degrade gracefully (e.g. return an empty list from a vector
search and proceed with structured-only results).

Concurrency Semaphore
---------------------
``ConcurrencyLimiter`` is a named asyncio.Semaphore that caps simultaneous
in-flight calls to expensive services (vector DB, LLM).  This prevents
thundering-herd overload at high request rates.

Usage
-----
    breaker = CircuitBreaker("review_vector_search", failure_threshold=5,
                             recovery_timeout=30.0)
    result = await breaker.call(review_service.search, query, business_id)

    # Or wrap with a per-call timeout and fallback:
    result = await with_timeout(
        review_service.search(query, business_id),
        timeout_seconds=0.08,
        fallback=[],
    )
"""

from __future__ import annotations

import asyncio
import logging
import time
from enum import Enum
from typing import Any, Awaitable, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Circuit Breaker
# ---------------------------------------------------------------------------

class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpenError(Exception):
    """Raised when a call is rejected because the circuit is OPEN."""


class CircuitBreaker:
    """
    Per-service circuit breaker.

    Parameters
    ----------
    name                : human-readable service name (for logs/metrics)
    failure_threshold   : consecutive failures before opening the circuit
    recovery_timeout    : seconds to wait before transitioning OPEN → HALF_OPEN
    success_threshold   : consecutive successes in HALF_OPEN to close again
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        success_threshold: int = 2,
    ):
        self.name = name
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._success_threshold = success_threshold

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float = 0.0
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitState:
        return self._state

    async def call(
        self,
        func: Callable[..., Awaitable[T]],
        *args: Any,
        fallback: Optional[T] = None,
        **kwargs: Any,
    ) -> T:
        """
        Invoke *func* through the circuit breaker.

        If the circuit is OPEN and the recovery window has not elapsed,
        the fallback value is returned immediately without calling *func*.
        """
        async with self._lock:
            if self._state == CircuitState.OPEN:
                if time.monotonic() - self._last_failure_time >= self._recovery_timeout:
                    self._state = CircuitState.HALF_OPEN
                    self._success_count = 0
                    logger.info("Circuit %s → HALF_OPEN", self.name)
                else:
                    logger.debug("Circuit %s OPEN — short-circuiting", self.name)
                    return fallback  # type: ignore[return-value]

        try:
            result = await func(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            await self._on_failure(exc)
            return fallback  # type: ignore[return-value]

        await self._on_success()
        return result

    async def _on_success(self) -> None:
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self._success_threshold:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    logger.info("Circuit %s → CLOSED (recovered)", self.name)
            elif self._state == CircuitState.CLOSED:
                self._failure_count = 0

    async def _on_failure(self, exc: Exception) -> None:
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()
            logger.warning(
                "Circuit %s failure %d/%d: %s",
                self.name,
                self._failure_count,
                self._failure_threshold,
                exc,
            )
            if self._failure_count >= self._failure_threshold:
                self._state = CircuitState.OPEN
                logger.error("Circuit %s → OPEN", self.name)

    def reset(self) -> None:
        """Manually reset to CLOSED (useful in tests)."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0


# ---------------------------------------------------------------------------
# Timeout wrapper
# ---------------------------------------------------------------------------

async def with_timeout(
    coro: Awaitable[T],
    timeout_seconds: float,
    fallback: T,
    service_name: str = "",
) -> T:
    """
    Await *coro* with a hard timeout.

    Returns *fallback* on expiry instead of raising, enabling graceful
    degradation (e.g. empty vector results → structured-only answer).
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        label = f" [{service_name}]" if service_name else ""
        logger.warning("Timeout%s after %.0f ms", label, timeout_seconds * 1000)
        return fallback


# ---------------------------------------------------------------------------
# Concurrency limiter
# ---------------------------------------------------------------------------

class ConcurrencyLimiter:
    """
    Named semaphore that caps simultaneous in-flight calls to a service.

    Prevents thundering-herd overload on expensive resources (vector DB,
    LLM) at 100k+ concurrent request rates.

    Usage
    -----
        limiter = ConcurrencyLimiter("llm", max_concurrent=50)
        async with limiter:
            response = await llm_service.generate(...)
    """

    def __init__(self, name: str, max_concurrent: int):
        self.name = name
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def __aenter__(self) -> "ConcurrencyLimiter":
        await self._semaphore.acquire()
        return self

    async def __aexit__(self, *args: Any) -> None:
        self._semaphore.release()

    @property
    def available(self) -> int:
        """Number of additional concurrent slots available."""
        return self._semaphore._value  # type: ignore[attr-defined]
