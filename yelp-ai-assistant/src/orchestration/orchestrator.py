"""
Answer Orchestration Layer
===========================

Merges signals from all search services into a single ranked evidence
bundle that is handed to the LLM for final answer generation (TDD §7).

Key responsibilities:
  - Enforce structured authority (canonical fields always win)
  - Remove contradictions between structured and review/photo data
  - Score and rank evidence
  - Prepare the LLM context string

Final score formula (TDD §7):
    final_score = 0.4 * structured_match + 0.3 * review_similarity + 0.3 * photo_similarity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from src.models.schemas import (
    BusinessData,
    PhotoSearchResult,
    QueryIntent,
    ReviewSearchResult,
    StructuredSearchResult,
)
from src.routing.router import RoutedResults


# ---------------------------------------------------------------------------
# Evidence bundle
# ---------------------------------------------------------------------------

@dataclass
class EvidenceBundle:
    """Ranked, conflict-resolved evidence ready for LLM context."""

    business: Optional[BusinessData] = None
    structured_score: float = 0.0
    review_results: List[ReviewSearchResult] = field(default_factory=list)
    photo_results: List[PhotoSearchResult] = field(default_factory=list)
    final_score: float = 0.0
    conflict_notes: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class AnswerOrchestrator:
    """
    Merges multi-source search results into a ranked evidence bundle
    and formats an LLM prompt context string.
    """

    # Scoring weights from TDD §7
    W_STRUCTURED = 0.4
    W_REVIEW = 0.3
    W_PHOTO = 0.3

    def orchestrate(self, routed: RoutedResults) -> EvidenceBundle:
        """
        Build an EvidenceBundle from RoutedResults.

        Conflict rule: if structured data contains an explicit answer for a
        field, review/photo results that contradict it are flagged but NOT
        used to override the canonical value.
        """
        bundle = EvidenceBundle()

        # --- Structured ---
        if routed.structured_results:
            best_structured = routed.structured_results[0]
            bundle.business = best_structured.business
            bundle.structured_score = best_structured.score

        # --- Reviews ---
        bundle.review_results = list(routed.review_results)

        # --- Photos ---
        bundle.photo_results = list(routed.photo_results)

        # --- Conflict detection ---
        if bundle.business and bundle.review_results:
            bundle.conflict_notes.extend(
                self._detect_conflicts(bundle.business, bundle.review_results)
            )

        # --- Final score ---
        avg_review = (
            sum(r.similarity_score for r in bundle.review_results) / len(bundle.review_results)
            if bundle.review_results
            else 0.0
        )
        avg_photo = (
            sum(p.combined_score for p in bundle.photo_results) / len(bundle.photo_results)
            if bundle.photo_results
            else 0.0
        )
        bundle.final_score = round(
            self.W_STRUCTURED * bundle.structured_score
            + self.W_REVIEW * avg_review
            + self.W_PHOTO * avg_photo,
            4,
        )
        return bundle

    def build_llm_context(self, bundle: EvidenceBundle, query: str) -> str:
        """
        Format the evidence bundle into a structured LLM prompt context
        following the template from TDD §8.1.
        """
        lines: List[str] = []
        lines.append(f"User query: {query}\n")

        # --- Canonical facts ---
        lines.append("## Canonical Facts (authoritative — do not contradict)")
        if bundle.business:
            biz = bundle.business
            lines.append(f"- Name: {biz.name}")
            lines.append(f"- Address: {biz.address}")
            lines.append(f"- Phone: {biz.phone}")
            lines.append(f"- Price range: {biz.price_range}")
            if biz.hours:
                hours_str = "; ".join(
                    f"{h.day}: {h.open_time}–{h.close_time}" if not h.is_closed else f"{h.day}: closed"
                    for h in biz.hours
                )
                lines.append(f"- Hours: {hours_str}")
            if biz.amenities:
                amenity_lines = [
                    f"  - {k.replace('_', ' ').title()}: {'Yes' if v else 'No'}"
                    for k, v in biz.amenities.items()
                ]
                lines.append("- Amenities:")
                lines.extend(amenity_lines)
        else:
            lines.append("- No structured data available.")

        # --- Conflict notes ---
        if bundle.conflict_notes:
            lines.append("\n## Conflict Notes")
            for note in bundle.conflict_notes:
                lines.append(f"- {note}")

        # --- Relevant reviews ---
        lines.append("\n## Relevant Reviews (anecdotal — treat as supporting evidence)")
        if bundle.review_results:
            for i, rr in enumerate(bundle.review_results[:3], 1):
                lines.append(f"{i}. [{rr.review.rating}/5] {rr.review.text[:300]}")
        else:
            lines.append("- No relevant reviews found.")

        # --- Photo evidence ---
        lines.append("\n## Photo Evidence")
        if bundle.photo_results:
            for i, pr in enumerate(bundle.photo_results[:3], 1):
                lines.append(
                    f"{i}. Caption: \"{pr.photo.caption}\" (score: {pr.combined_score:.2f})"
                )
        else:
            lines.append("- No relevant photos found.")

        lines.append(
            "\n## Instructions\n"
            "Answer the user query using ONLY the information above.\n"
            "Structured canonical facts take priority over reviews and photos.\n"
            "Do NOT fabricate or infer information that is not present above.\n"
            "If information is unavailable, say so clearly."
        )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _detect_conflicts(
        self, business: BusinessData, reviews: List[ReviewSearchResult]
    ) -> List[str]:
        """
        Detect cases where reviews appear to contradict canonical amenity data.
        Returns human-readable conflict notes.
        """
        notes: List[str] = []
        for amenity_key, canonical_value in business.amenities.items():
            amenity_label = amenity_key.replace("_", " ")
            # Check if any review mentions the amenity with contradictory signal
            for rr in reviews:
                text_lower = rr.review.text.lower()
                if amenity_label in text_lower:
                    # Heuristic: review mentions amenity but canonical says No
                    if not canonical_value and amenity_label in text_lower:
                        notes.append(
                            f"Canonical data: no {amenity_label}. "
                            f"Some reviews mention '{amenity_label}' — "
                            f"treat as anecdotal."
                        )
                        break
        return notes
