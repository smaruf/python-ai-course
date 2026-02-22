"""
RAG / LLM Integration
=====================

Sends the orchestrated evidence context to an LLM and returns the final
answer (TDD §8).

Rules enforced:
  - Structured data is marked authoritative in the prompt
  - Reviews are treated as anecdotal
  - LLM must not fabricate missing data

The LLM call is mocked by default so the service works without API keys.
A real OpenAI backend can be activated via environment variables.
"""

from __future__ import annotations

import os
import time
from typing import Optional

from src.models.schemas import EvidenceSummary, QueryIntent, QueryResponse
from src.orchestration.orchestrator import AnswerOrchestrator, EvidenceBundle


class RAGService:
    """
    Retrieval-Augmented Generation service.

    Calls the configured LLM with the structured context from the
    AnswerOrchestrator and returns a QueryResponse.
    """

    def __init__(self, use_mock: bool = True):
        """
        Parameters
        ----------
        use_mock : bool
            When True (default) the LLM call is simulated without any
            external API call.  Set to False to enable real OpenAI calls
            (requires OPENAI_API_KEY in the environment).
        """
        self._use_mock = use_mock
        self._orchestrator = AnswerOrchestrator()

    async def generate_answer(
        self,
        query: str,
        intent: QueryIntent,
        bundle: EvidenceBundle,
    ) -> QueryResponse:
        """
        Generate a natural-language answer for *query* given the evidence
        bundle and return a QueryResponse.
        """
        start = time.monotonic()
        context = self._orchestrator.build_llm_context(bundle, query)

        if self._use_mock:
            answer = self._mock_answer(query, intent, bundle)
        else:
            answer = await self._call_openai(context)

        latency_ms = round((time.monotonic() - start) * 1000, 1)

        evidence = EvidenceSummary(
            structured=bundle.business is not None,
            reviews_used=len(bundle.review_results),
            photos_used=len(bundle.photo_results),
        )
        return QueryResponse(
            answer=answer,
            confidence=round(bundle.final_score, 2),
            intent=intent,
            evidence=evidence,
            latency_ms=latency_ms,
        )

    # ------------------------------------------------------------------
    # Mock LLM
    # ------------------------------------------------------------------

    def _mock_answer(
        self, query: str, intent: QueryIntent, bundle: EvidenceBundle
    ) -> str:
        """Generate a deterministic answer from structured data (no LLM)."""
        biz = bundle.business

        if intent == QueryIntent.OPERATIONAL:
            if biz and biz.hours:
                hours_str = "; ".join(
                    f"{h.day.title()}: {h.open_time}–{h.close_time}"
                    if not h.is_closed
                    else f"{h.day.title()}: Closed"
                    for h in biz.hours
                )
                return f"Business hours for {biz.name}: {hours_str}."
            return "Business hours are not available."

        if intent == QueryIntent.AMENITY:
            if biz and biz.amenities:
                query_lower = query.lower()
                for key, value in biz.amenities.items():
                    label = key.replace("_", " ")
                    if label in query_lower or key in query_lower:
                        status = "Yes" if value else "No"
                        answer = f"{biz.name} — {label}: {status} (canonical)."
                        if bundle.conflict_notes:
                            answer += " Note: " + bundle.conflict_notes[0]
                        return answer
            return "Amenity information is not available in our records."

        if intent == QueryIntent.QUALITY:
            if bundle.review_results:
                avg_rating = sum(r.review.rating for r in bundle.review_results) / len(
                    bundle.review_results
                )
                return (
                    f"Based on {len(bundle.review_results)} relevant review(s), "
                    f"average rating: {avg_rating:.1f}/5."
                )
            return "No relevant reviews found to assess quality."

        if intent == QueryIntent.PHOTO:
            if bundle.photo_results:
                captions = [p.photo.caption for p in bundle.photo_results if p.photo.caption]
                if captions:
                    return f"Found {len(bundle.photo_results)} photo(s): " + "; ".join(captions[:3])
            return "No matching photos found."

        return "I could not find a specific answer to your question."

    # ------------------------------------------------------------------
    # Real OpenAI backend
    # ------------------------------------------------------------------

    async def _call_openai(self, context: str) -> str:
        """Call the OpenAI Chat Completions API with the given context."""
        try:
            import openai  # type: ignore

            client = openai.AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful business information assistant. "
                            "Answer questions using ONLY the provided context. "
                            "Never fabricate information."
                        ),
                    },
                    {"role": "user", "content": context},
                ],
                temperature=0.2,
                max_tokens=512,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:  # noqa: BLE001
            return f"LLM unavailable ({exc}). Falling back to structured data."
