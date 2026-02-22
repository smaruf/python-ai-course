"""
Query Router
============

Routes an incoming query to the appropriate search service(s) based on
the classified intent.  Implements the routing logic from TDD §5.2.

  OPERATIONAL → structured index only
  AMENITY     → structured first, fallback to review + photo
  QUALITY     → review vector search
  PHOTO       → hybrid photo retrieval
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from src.models.schemas import (
    PhotoSearchResult,
    QueryIntent,
    ReviewSearchResult,
    StructuredSearchResult,
)


@dataclass
class RoutingDecision:
    """Describes which services will be queried and why."""

    intent: QueryIntent
    use_structured: bool = False
    use_review_vector: bool = False
    use_photo_hybrid: bool = False
    reason: str = ""


@dataclass
class RoutedResults:
    """Aggregated raw results from all queried services."""

    decision: RoutingDecision
    structured_results: List[StructuredSearchResult] = field(default_factory=list)
    review_results: List[ReviewSearchResult] = field(default_factory=list)
    photo_results: List[PhotoSearchResult] = field(default_factory=list)


class QueryRouter:
    """
    Stateless query router.

    Accepts a pre-classified intent and invokes the relevant search
    services to produce a RoutedResults bundle.
    """

    def decide(self, intent: QueryIntent) -> RoutingDecision:
        """Return a routing decision for the given intent."""
        if intent == QueryIntent.OPERATIONAL:
            return RoutingDecision(
                intent=intent,
                use_structured=True,
                use_review_vector=False,
                use_photo_hybrid=False,
                reason="Operational queries use authoritative structured data only.",
            )
        if intent == QueryIntent.AMENITY:
            return RoutingDecision(
                intent=intent,
                use_structured=True,
                use_review_vector=True,
                use_photo_hybrid=True,
                reason="Amenity queries check structured first, then review + photo fallback.",
            )
        if intent == QueryIntent.QUALITY:
            return RoutingDecision(
                intent=intent,
                use_structured=False,
                use_review_vector=True,
                use_photo_hybrid=False,
                reason="Quality queries use review vector search.",
            )
        if intent == QueryIntent.PHOTO:
            return RoutingDecision(
                intent=intent,
                use_structured=False,
                use_review_vector=False,
                use_photo_hybrid=True,
                reason="Photo queries use hybrid photo retrieval.",
            )
        # UNKNOWN — return all sources as a safe fallback
        return RoutingDecision(
            intent=intent,
            use_structured=True,
            use_review_vector=True,
            use_photo_hybrid=False,
            reason="Unknown intent — broad fallback search.",
        )

    async def route(
        self,
        query: str,
        business_id: str,
        intent: QueryIntent,
        structured_service,
        review_service,
        photo_service,
    ) -> RoutedResults:
        """
        Execute search across relevant services and return combined results.

        Parameters
        ----------
        query            : raw user query string
        business_id      : target business identifier
        intent           : pre-classified query intent
        structured_service : instance of StructuredSearchService
        review_service     : instance of ReviewVectorSearchService
        photo_service      : instance of PhotoHybridRetrievalService
        """
        decision = self.decide(intent)
        results = RoutedResults(decision=decision)

        if decision.use_structured:
            results.structured_results = await structured_service.search(
                query, business_id
            )

        if decision.use_review_vector:
            results.review_results = await review_service.search(query, business_id)

        if decision.use_photo_hybrid:
            results.photo_results = await photo_service.search(query, business_id)

        # Amenity-specific narrowing: if structured data provides a definitive
        # answer, discard review/photo results to avoid contradictions.
        if intent == QueryIntent.AMENITY and results.structured_results:
            best = results.structured_results[0]
            if best.matched_fields:
                results.review_results = []
                results.photo_results = []

        return results
