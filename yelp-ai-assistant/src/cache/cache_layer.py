"""
Cache Layer
===========

Two-tier cache for high-concurrency production scale (TDD §10.2):

  L1 — in-process LRU dict (zero-latency, per-replica)
  L2 — Redis (shared across all replicas, TTL-backed)

Three logical namespaces (key spaces):

  qr:{business_id}:{query_hash}   — full QueryResponse objects (TTL 5 min)
  hours:{business_id}             — business hours structs (TTL 5 min)
  emb:{query_hash}                — query embeddings (TTL 30 min)

When Redis is unavailable the cache degrades gracefully to L1-only so the
API keeps serving without errors.

Key design choices for 100k+ concurrency:
  - All cache calls are async-friendly (non-blocking).
  - Stampede protection via a per-key asyncio.Lock prevents multiple
    concurrent workers all recomputing the same missing value simultaneously.
  - L1 is bounded by MAX_L1_SIZE entries to avoid unbounded memory growth.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from collections import OrderedDict
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# TTL constants (seconds) — matches TDD §10.2 / sequence diagram §8
TTL_QUERY_RESULT: int = 300    # 5 min
TTL_BUSINESS_HOURS: int = 300  # 5 min
TTL_EMBEDDING: int = 1800      # 30 min

MAX_L1_SIZE: int = 10_000      # entries per replica


# ---------------------------------------------------------------------------
# In-process L1 cache (bounded LRU)
# ---------------------------------------------------------------------------

class _L1Cache:
    """Thread-safe bounded LRU cache backed by an OrderedDict."""

    def __init__(self, maxsize: int = MAX_L1_SIZE):
        self._store: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._maxsize = maxsize
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if time.monotonic() > expires_at:
                self._store.pop(key, None)
                return None
            # Move to end (most recently used)
            self._store.move_to_end(key)
            return value

    async def set(self, key: str, value: Any, ttl: int) -> None:
        async with self._lock:
            expires_at = time.monotonic() + ttl
            self._store[key] = (value, expires_at)
            self._store.move_to_end(key)
            # Evict oldest entries when over capacity
            while len(self._store) > self._maxsize:
                self._store.popitem(last=False)

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._store.pop(key, None)

    async def delete_prefix(self, prefix: str) -> int:
        """Delete all keys that start with *prefix*. Returns count deleted."""
        async with self._lock:
            to_delete = [k for k in self._store if k.startswith(prefix)]
            for k in to_delete:
                del self._store[k]
            return len(to_delete)

    def size(self) -> int:
        return len(self._store)


# ---------------------------------------------------------------------------
# Redis backend (optional)
# ---------------------------------------------------------------------------

class _RedisBackend:
    """
    Thin async wrapper around redis.asyncio.Redis.

    Falls back silently to no-ops if the Redis client is not installed or
    the connection cannot be established — ensuring the cache layer never
    takes the API down.
    """

    def __init__(self, url: str = "redis://localhost:6379/0"):
        self._url = url
        self._client: Any = None
        self._available = False

    async def connect(self) -> None:
        try:
            import redis.asyncio as aioredis  # type: ignore
            self._client = aioredis.from_url(self._url, decode_responses=True)
            await self._client.ping()
            self._available = True
            logger.info("Redis cache connected: %s", self._url)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Redis unavailable — L1-only cache mode: %s", exc)
            self._available = False

    async def get(self, key: str) -> Optional[str]:
        if not self._available or self._client is None:
            return None
        try:
            return await self._client.get(key)
        except Exception:  # noqa: BLE001
            return None

    async def set(self, key: str, value: str, ttl: int) -> None:
        if not self._available or self._client is None:
            return
        try:
            await self._client.set(key, value, ex=ttl)
        except Exception:  # noqa: BLE001
            pass

    async def delete(self, key: str) -> None:
        if not self._available or self._client is None:
            return
        try:
            await self._client.delete(key)
        except Exception:  # noqa: BLE001
            pass

    async def delete_prefix(self, prefix: str) -> int:
        """Delete all keys matching prefix* via SCAN (non-blocking)."""
        if not self._available or self._client is None:
            return 0
        try:
            count = 0
            async for key in self._client.scan_iter(f"{prefix}*"):
                await self._client.delete(key)
                count += 1
            return count
        except Exception:  # noqa: BLE001
            return 0

    async def close(self) -> None:
        if self._client is not None:
            try:
                await self._client.aclose()
            except Exception:  # noqa: BLE001
                pass


# ---------------------------------------------------------------------------
# Public QueryCache — unified L1 + L2 API
# ---------------------------------------------------------------------------

class QueryCache:
    """
    Two-tier cache for QueryResponse objects, business hours, and embeddings.

    Usage
    -----
    cache = QueryCache()
    await cache.connect()          # establishes Redis connection (optional)

    # Store / retrieve a full query response
    await cache.set_query_result(business_id, query, response_dict)
    result = await cache.get_query_result(business_id, query)

    # Invalidate on data change
    await cache.invalidate_business(business_id)
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self._l1 = _L1Cache()
        self._redis = _RedisBackend(redis_url)
        # Per-key locks prevent thundering-herd stampedes
        self._key_locks: Dict[str, asyncio.Lock] = {}
        self._key_locks_lock = asyncio.Lock()

    async def connect(self) -> None:
        """Connect to Redis (call once at application startup)."""
        await self._redis.connect()

    async def close(self) -> None:
        """Release resources (call at application shutdown)."""
        await self._redis.close()

    # ------------------------------------------------------------------
    # Query result cache
    # ------------------------------------------------------------------

    @staticmethod
    def _query_key(business_id: str, query: str) -> str:
        qhash = hashlib.sha256(query.encode()).hexdigest()[:16]
        return f"qr:{business_id}:{qhash}"

    async def get_query_result(
        self, business_id: str, query: str
    ) -> Optional[Dict[str, Any]]:
        """Return cached query response dict, or None on miss."""
        key = self._query_key(business_id, query)
        # L1 check
        hit = await self._l1.get(key)
        if hit is not None:
            return hit
        # L2 check
        raw = await self._redis.get(key)
        if raw is not None:
            try:
                value = json.loads(raw)
                await self._l1.set(key, value, TTL_QUERY_RESULT)
                return value
            except json.JSONDecodeError:
                pass
        return None

    async def set_query_result(
        self, business_id: str, query: str, response: Dict[str, Any]
    ) -> None:
        """Store a query response in both cache tiers."""
        key = self._query_key(business_id, query)
        await self._l1.set(key, response, TTL_QUERY_RESULT)
        await self._redis.set(key, json.dumps(response), TTL_QUERY_RESULT)

    # ------------------------------------------------------------------
    # Business hours cache
    # ------------------------------------------------------------------

    @staticmethod
    def _hours_key(business_id: str) -> str:
        return f"hours:{business_id}"

    async def get_business_hours(self, business_id: str) -> Optional[Dict[str, Any]]:
        key = self._hours_key(business_id)
        hit = await self._l1.get(key)
        if hit is not None:
            return hit
        raw = await self._redis.get(key)
        if raw is not None:
            try:
                value = json.loads(raw)
                await self._l1.set(key, value, TTL_BUSINESS_HOURS)
                return value
            except json.JSONDecodeError:
                pass
        return None

    async def set_business_hours(
        self, business_id: str, hours: Dict[str, Any]
    ) -> None:
        key = self._hours_key(business_id)
        await self._l1.set(key, hours, TTL_BUSINESS_HOURS)
        await self._redis.set(key, json.dumps(hours), TTL_BUSINESS_HOURS)

    # ------------------------------------------------------------------
    # Embedding cache
    # ------------------------------------------------------------------

    @staticmethod
    def _emb_key(query: str) -> str:
        qhash = hashlib.sha256(query.encode()).hexdigest()[:16]
        return f"emb:{qhash}"

    async def get_embedding(self, query: str) -> Optional[list]:
        key = self._emb_key(query)
        hit = await self._l1.get(key)
        if hit is not None:
            return hit
        raw = await self._redis.get(key)
        if raw is not None:
            try:
                value = json.loads(raw)
                await self._l1.set(key, value, TTL_EMBEDDING)
                return value
            except json.JSONDecodeError:
                pass
        return None

    async def set_embedding(self, query: str, embedding: list) -> None:
        key = self._emb_key(query)
        await self._l1.set(key, embedding, TTL_EMBEDDING)
        await self._redis.set(key, json.dumps(embedding), TTL_EMBEDDING)

    # ------------------------------------------------------------------
    # Invalidation
    # ------------------------------------------------------------------

    async def invalidate_business(self, business_id: str) -> None:
        """
        Invalidate all cache entries for a business.

        Called by the streaming ingestion pipeline whenever a review,
        hours, or photo update arrives for *business_id*.
        """
        prefix = f"qr:{business_id}:"
        await self._l1.delete_prefix(prefix)
        await self._redis.delete_prefix(prefix)
        hours_key = self._hours_key(business_id)
        await self._l1.delete(hours_key)
        await self._redis.delete(hours_key)

    # ------------------------------------------------------------------
    # Key-level lock for stampede prevention
    # ------------------------------------------------------------------

    async def get_key_lock(self, key: str) -> asyncio.Lock:
        """Return (or create) a per-key asyncio.Lock for stampede protection."""
        async with self._key_locks_lock:
            if key not in self._key_locks:
                self._key_locks[key] = asyncio.Lock()
            return self._key_locks[key]

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def l1_size(self) -> int:
        return self._l1.size()
