"""
Search Services
===============

Three independent search services as described in TDD §2 / §6:

1. StructuredSearchService   — queries PostgreSQL / Elasticsearch structured index
2. ReviewVectorSearchService — queries the FAISS / Pinecone review vector DB
3. PhotoHybridRetrievalService — hybrid caption + image embedding retrieval

All services accept an optional backend that can be dependency-injected for
testing without real infrastructure.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from src.models.schemas import (
    BusinessData,
    Photo,
    PhotoSearchResult,
    Review,
    ReviewSearchResult,
    StructuredSearchResult,
)


# ---------------------------------------------------------------------------
# Structured Search Service
# ---------------------------------------------------------------------------

class StructuredSearchService:
    """
    Searches authoritative structured business data.

    In production this queries a PostgreSQL table *and* an Elasticsearch
    structured index.  An in-memory dict backend is used here to keep the
    implementation infrastructure-free and fully testable.
    """

    def __init__(self, backend: Optional[Dict[str, BusinessData]] = None):
        self._store: Dict[str, BusinessData] = backend or {}

    def add_business(self, business: BusinessData) -> None:
        """Register a business in the in-memory store."""
        self._store[business.business_id] = business

    async def search(
        self, query: str, business_id: str, top_k: int = 1
    ) -> List[StructuredSearchResult]:
        """
        Return structured results for *business_id*.

        The query string is used to identify which fields are relevant
        (e.g. "hours" → match hours field, "patio" → match amenities).
        """
        business = self._store.get(business_id)
        if business is None:
            return []

        matched_fields: List[str] = []
        query_lower = query.lower()

        # Hours relevance
        if any(kw in query_lower for kw in ("open", "close", "hour", "time")):
            matched_fields.append("hours")

        # Amenity relevance
        for amenity_key in business.amenities:
            if amenity_key.replace("_", " ") in query_lower or amenity_key in query_lower:
                matched_fields.append(f"amenities.{amenity_key}")

        # Address / phone
        if any(kw in query_lower for kw in ("address", "location", "where", "phone", "number")):
            matched_fields.append("address")

        score = 1.0 if matched_fields else 0.5
        return [
            StructuredSearchResult(
                business=business,
                matched_fields=matched_fields,
                score=score,
            )
        ]


# ---------------------------------------------------------------------------
# Review Vector Search Service
# ---------------------------------------------------------------------------

def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two equal-length vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class ReviewVectorSearchService:
    """
    Searches review embeddings using cosine similarity.

    In production this wraps FAISS or Pinecone.  An in-memory list is
    used here so the service works without external dependencies.
    """

    def __init__(self, reviews: Optional[List[Review]] = None):
        self._reviews: List[Review] = reviews or []

    def add_review(self, review: Review) -> None:
        """Add a review to the in-memory store."""
        self._reviews.append(review)

    def _query_embedding(self, query: str) -> List[float]:
        """
        Create a simple bag-of-words embedding for *query*.

        This is a deterministic stand-in; replace with a real encoder in
        production (e.g. sentence-transformers).
        """
        tokens = query.lower().split()
        dim = 16
        vec = [0.0] * dim
        for token in tokens:
            for i, ch in enumerate(token):
                vec[i % dim] += ord(ch) / 1000.0
        return vec

    async def search(
        self, query: str, business_id: str, top_k: int = 5
    ) -> List[ReviewSearchResult]:
        """Return the top-k most similar reviews for *business_id*."""
        candidates = [r for r in self._reviews if r.business_id == business_id]
        if not candidates:
            return []

        query_vec = self._query_embedding(query)
        scored: List[ReviewSearchResult] = []
        for review in candidates:
            if review.embedding:
                sim = _cosine_similarity(query_vec, review.embedding)
            else:
                # Fallback: embed on-the-fly
                review_vec = self._query_embedding(review.text)
                sim = _cosine_similarity(query_vec, review_vec)
            scored.append(ReviewSearchResult(review=review, similarity_score=round(sim, 4)))

        scored.sort(key=lambda r: r.similarity_score, reverse=True)
        return scored[:top_k]


# ---------------------------------------------------------------------------
# Photo Hybrid Retrieval Service
# ---------------------------------------------------------------------------

class PhotoHybridRetrievalService:
    """
    Hybrid photo retrieval combining caption keyword search and image
    embedding vector search (TDD §6).

    Scoring formula:
        score = 0.5 * caption_score + 0.5 * image_similarity
    """

    def __init__(self, photos: Optional[List[Photo]] = None):
        self._photos: List[Photo] = photos or []

    def add_photo(self, photo: Photo) -> None:
        """Add a photo to the in-memory store."""
        self._photos.append(photo)

    def _caption_score(self, query: str, caption: str) -> float:
        """BM25-inspired keyword overlap score (simplified)."""
        if not caption:
            return 0.0
        query_tokens = set(query.lower().split())
        caption_tokens = set(caption.lower().split())
        if not query_tokens:
            return 0.0
        overlap = len(query_tokens & caption_tokens)
        return round(overlap / len(query_tokens), 4)

    def _image_sim(self, query: str, photo: Photo) -> float:
        """
        Cosine similarity between a query embedding and the photo's image
        embedding.  Falls back to a caption-based proxy if no image
        embedding is stored.
        """
        if photo.image_embedding:
            query_vec = [ord(c) / 1000.0 for c in query[:len(photo.image_embedding)]]
            # Pad or truncate to match dimensions
            dim = len(photo.image_embedding)
            query_vec = (query_vec + [0.0] * dim)[:dim]
            return round(_cosine_similarity(query_vec, photo.image_embedding), 4)
        # Fallback: use caption similarity as proxy
        return self._caption_score(query, photo.caption)

    async def search(
        self, query: str, business_id: str, top_k: int = 5
    ) -> List[PhotoSearchResult]:
        """Return the top-k photos for *business_id* matching *query*."""
        candidates = [p for p in self._photos if p.business_id == business_id]
        if not candidates:
            return []

        results: List[PhotoSearchResult] = []
        for photo in candidates:
            cap_score = self._caption_score(query, photo.caption)
            img_sim = self._image_sim(query, photo)
            results.append(
                PhotoSearchResult(
                    photo=photo,
                    caption_score=cap_score,
                    image_similarity=img_sim,
                )
            )

        results.sort(key=lambda r: r.combined_score, reverse=True)
        return results[:top_k]
