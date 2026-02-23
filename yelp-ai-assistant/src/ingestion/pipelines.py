"""
Data Ingestion Pipelines
========================

Implements the hybrid freshness strategy from TDD §4:

  - StreamingIngestionPipeline   : high/medium velocity data (reviews, ratings,
                                   hours changes, photos) arriving via Kafka CDC
  - BatchIngestionPipeline       : low-velocity static content (menus, etc.)
                                   processed on a weekly schedule

Both pipelines use an in-memory event queue so they work without external
infrastructure.  In production, replace the queue with real Kafka consumers
and S3/object-storage writers.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Event model
# ---------------------------------------------------------------------------

class EventType(str, Enum):
    REVIEW_CREATED = "review.created"
    REVIEW_UPDATED = "review.updated"
    RATING_UPDATED = "rating.updated"
    HOURS_CHANGED = "hours.changed"
    PHOTO_UPLOADED = "photo.uploaded"
    MENU_UPDATED = "menu.updated"


@dataclass
class IngestionEvent:
    """A CDC or application-generated data change event."""

    event_type: EventType
    business_id: str
    payload: Dict[str, Any]
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    processed_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Freshness SLA targets (seconds)
# ---------------------------------------------------------------------------

FRESHNESS_SLA: Dict[EventType, int] = {
    EventType.REVIEW_CREATED: 600,    # < 10 minutes
    EventType.REVIEW_UPDATED: 600,
    EventType.RATING_UPDATED: 600,
    EventType.HOURS_CHANGED: 300,     # < 5 minutes
    EventType.PHOTO_UPLOADED: 300,
    EventType.MENU_UPDATED: 7 * 24 * 3600,  # weekly batch
}


# ---------------------------------------------------------------------------
# Streaming pipeline
# ---------------------------------------------------------------------------

class StreamingIngestionPipeline:
    """
    Processes high- and medium-velocity events in near real-time.

    Events are placed on an asyncio Queue (simulating a Kafka consumer).
    Registered handlers are called for each matching event type.
    """

    def __init__(self):
        self._queue: asyncio.Queue = asyncio.Queue()
        self._handlers: Dict[EventType, List[Callable]] = {e: [] for e in EventType}
        self._processed: List[IngestionEvent] = []

    def register_handler(self, event_type: EventType, handler: Callable) -> None:
        """Register a coroutine or callable to process events of *event_type*."""
        self._handlers[event_type].append(handler)

    async def publish(self, event: IngestionEvent) -> None:
        """Publish an event to the internal queue (simulates Kafka producer)."""
        await self._queue.put(event)
        logger.debug("Published %s for business %s", event.event_type, event.business_id)

    async def process_one(self) -> Optional[IngestionEvent]:
        """
        Process a single event from the queue.

        Returns the processed event, or None if the queue was empty.
        """
        try:
            event: IngestionEvent = self._queue.get_nowait()
        except asyncio.QueueEmpty:
            return None

        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception:  # noqa: BLE001
                logger.exception("Handler error for event %s", event.event_type)

        event.processed_at = datetime.now(timezone.utc)
        self._processed.append(event)
        self._queue.task_done()
        logger.debug("Processed %s in %.1f s", event.event_type,
                     (event.processed_at - event.occurred_at).total_seconds())
        return event

    async def drain(self) -> List[IngestionEvent]:
        """Process all queued events and return them."""
        results: List[IngestionEvent] = []
        while not self._queue.empty():
            event = await self.process_one()
            if event:
                results.append(event)
        return results

    def check_freshness_sla(self, event: IngestionEvent) -> bool:
        """
        Return True if the event was processed within its SLA window.

        Requires event.processed_at to be set.
        """
        if event.processed_at is None:
            return False
        sla_seconds = FRESHNESS_SLA.get(event.event_type, 3600)
        elapsed = (event.processed_at - event.occurred_at).total_seconds()
        return elapsed <= sla_seconds

    @property
    def processed_events(self) -> List[IngestionEvent]:
        return list(self._processed)


# ---------------------------------------------------------------------------
# Batch pipeline
# ---------------------------------------------------------------------------

class BatchIngestionPipeline:
    """
    Processes low-velocity static content on a scheduled (weekly) basis.

    Each batch job is a callable that receives the list of raw records and
    returns a count of successfully processed items.
    """

    def __init__(self):
        self._jobs: List[Callable] = []
        self._run_history: List[Dict[str, Any]] = []

    def register_job(self, job: Callable) -> None:
        """Register a batch processing callable."""
        self._jobs.append(job)

    async def run(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute all registered batch jobs against *records*.

        Returns a summary dict with counts and timing.
        """
        start = datetime.now(timezone.utc)
        total_processed = 0
        errors: List[str] = []

        for job in self._jobs:
            try:
                if asyncio.iscoroutinefunction(job):
                    count = await job(records)
                else:
                    count = job(records)
                total_processed += count or 0
            except Exception as exc:  # noqa: BLE001
                errors.append(str(exc))
                logger.exception("Batch job error: %s", exc)

        summary = {
            "started_at": start.isoformat(),
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "records_in": len(records),
            "records_processed": total_processed,
            "errors": errors,
        }
        self._run_history.append(summary)
        return summary

    @property
    def run_history(self) -> List[Dict[str, Any]]:
        return list(self._run_history)
