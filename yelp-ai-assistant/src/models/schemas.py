"""
Data models for the Yelp-Style AI Assistant.

Covers:
- Business (structured, authoritative data)
- Review (unstructured data)
- Photo (multimodal data)
- Query / Response API contracts
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class QueryIntent(str, Enum):
    """Classified intent of an incoming user query."""

    OPERATIONAL = "operational"   # "Is it open right now?"
    AMENITY = "amenity"           # "Do they have a heated patio?"
    QUALITY = "quality"           # "Is it good for dates?"
    PHOTO = "photo"               # "Show me photos of the outdoor seating"
    UNKNOWN = "unknown"


class DataVelocity(str, Enum):
    """Ingestion velocity classification per data type."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ---------------------------------------------------------------------------
# Structured / Authoritative Business Data
# ---------------------------------------------------------------------------

@dataclass
class BusinessHours:
    """Operating hours for a single day."""

    day: str                  # e.g. "monday"
    open_time: str            # e.g. "09:00"
    close_time: str           # e.g. "22:00"
    is_closed: bool = False


@dataclass
class BusinessData:
    """
    Authoritative structured data for a business.

    This is the single source of truth for operational fields such as
    hours, address, amenities, and price range.  Reviews and photos must
    NEVER overwrite these fields.
    """

    business_id: str
    name: str
    address: str
    phone: str
    price_range: str          # "$", "$$", "$$$", "$$$$"
    hours: List[BusinessHours] = field(default_factory=list)
    amenities: Dict[str, bool] = field(default_factory=dict)
    # e.g. {"heated_patio": True, "parking": False, "wifi": True}
    categories: List[str] = field(default_factory=list)
    rating: float = 0.0
    review_count: int = 0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def is_open_at(self, dt: datetime) -> Optional[bool]:
        """Return True/False if business is open at *dt*, None if unknown."""
        day_name = dt.strftime("%A").lower()
        for entry in self.hours:
            if entry.day.lower() == day_name:
                if entry.is_closed:
                    return False
                try:
                    open_h, open_m = map(int, entry.open_time.split(":"))
                    close_h, close_m = map(int, entry.close_time.split(":"))
                    check = dt.hour * 60 + dt.minute
                    return (open_h * 60 + open_m) <= check <= (close_h * 60 + close_m)
                except ValueError:
                    return None
        return None


# ---------------------------------------------------------------------------
# Unstructured Data
# ---------------------------------------------------------------------------

@dataclass
class Review:
    """A user-submitted review (unstructured data)."""

    review_id: str
    business_id: str
    user_id: str
    rating: float
    text: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    embedding: Optional[List[float]] = None   # populated by ingestion pipeline


@dataclass
class Photo:
    """A business photo with caption and embedding."""

    photo_id: str
    business_id: str
    url: str
    caption: str = ""
    image_embedding: Optional[List[float]] = None   # CLIP embedding
    caption_embedding: Optional[List[float]] = None
    uploaded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# Search / Retrieval Results
# ---------------------------------------------------------------------------

@dataclass
class StructuredSearchResult:
    """Result from the structured (PostgreSQL / ES) search service."""

    business: BusinessData
    matched_fields: List[str] = field(default_factory=list)
    score: float = 1.0


@dataclass
class ReviewSearchResult:
    """Result from the review vector search service."""

    review: Review
    similarity_score: float = 0.0


@dataclass
class PhotoSearchResult:
    """Result from the photo hybrid retrieval service."""

    photo: Photo
    caption_score: float = 0.0
    image_similarity: float = 0.0

    @property
    def combined_score(self) -> float:
        """Hybrid score: 50 % caption + 50 % image similarity."""
        return 0.5 * self.caption_score + 0.5 * self.image_similarity


# ---------------------------------------------------------------------------
# API Request / Response
# ---------------------------------------------------------------------------

class UserContext(BaseModel):
    """Optional context provided by the client."""

    location: Optional[str] = None
    time: Optional[datetime] = None


class QueryRequest(BaseModel):
    """POST /assistant/query — request payload."""

    query: str = Field(..., min_length=1, max_length=1000)
    business_id: str = Field(..., min_length=1)
    user_context: Optional[UserContext] = None


class EvidenceSummary(BaseModel):
    """Evidence used to build the answer."""

    structured: bool = False
    reviews_used: int = 0
    photos_used: int = 0


class QueryResponse(BaseModel):
    """POST /assistant/query — response payload."""

    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    intent: QueryIntent
    evidence: EvidenceSummary
    latency_ms: Optional[float] = None
