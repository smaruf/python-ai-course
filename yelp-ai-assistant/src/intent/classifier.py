"""
Intent Classifier
=================

Classifies incoming queries into one of four intent categories:
  - operational  (hours, open/closed)
  - amenity      (features like heated patio, parking)
  - quality      (reviews, sentiment — "is it good for dates?")
  - photo        (image retrieval)

The classifier uses keyword/pattern matching as a lightweight, low-latency
approach (< 20 ms target from the TDD).  It is designed to be easily replaced
with a fine-tuned transformer model when one becomes available.
"""

from __future__ import annotations

import re
import time
from typing import Dict, List, Tuple

from src.models.schemas import QueryIntent


# ---------------------------------------------------------------------------
# Keyword signal tables
# ---------------------------------------------------------------------------

_OPERATIONAL_SIGNALS: List[str] = [
    r"\bopen\b",
    r"\bclosed?\b",
    r"\bhours?\b",
    r"\bclose[sd]?\b",
    r"\bclose\s+at\b",
    r"\bopen\s+until\b",
    r"\bwhat\s+time\b",
    r"\btodayv?\b",
    r"\bright\s+now\b",
    r"\bcurrently\b",
    r"\btonight\b",
    r"\bmorning\b",
    r"\bevening\b",
    r"\bsunday\b",
    r"\bmonday\b",
    r"\btuesday\b",
    r"\bwednesday\b",
    r"\bthursday\b",
    r"\bfriday\b",
    r"\bsaturday\b",
]

_AMENITY_SIGNALS: List[str] = [
    r"\bpatio\b",
    r"\bheater[sd]?\b",
    r"\bheated\b",
    r"\bparking\b",
    r"\bwifi\b",
    r"\bwi-fi\b",
    r"\bwheelchair\b",
    r"\baccessible\b",
    r"\bvegan\b",
    r"\bgluten.free\b",
    r"\boutdoor\b",
    r"\bindoor\b",
    r"\bseating\b",
    r"\breservation[sd]?\b",
    r"\btake.?out\b",
    r"\bdelivery\b",
    r"\bkid.?friend\b",
    r"\bdog.?friend\b",
    r"\bpet.?friend\b",
    r"\bhappy\s+hour\b",
    r"\bhave\b",
    r"\bdo\s+they\b",
    r"\bdoes\s+it\b",
    r"\bamenitie[sd]?\b",
    r"\bfeature[sd]?\b",
]

_QUALITY_SIGNALS: List[str] = [
    r"\bgood\b",
    r"\bbad\b",
    r"\bgreat\b",
    r"\bworth\b",
    r"\bworth\s+it\b",
    r"\breview[sd]?\b",
    r"\brating[sd]?\b",
    r"\bdate\b",
    r"\bromantic\b",
    r"\bfamily\b",
    r"\bkids?\b",
    r"\brecommend\b",
    r"\bopinion[sd]?\b",
    r"\bexperience\b",
    r"\bfood\b",
    r"\bservice\b",
    r"\batmosphere\b",
    r"\bambiance\b",
    r"\bnoise\b",
    r"\bwait\b",
    r"\bworth\b",
    r"\bsatisf\w+\b",
    r"\bcomplaints?\b",
    r"\bpraise[sd]?\b",
    r"\bpeople\s+say\b",
    r"\bcustomers?\s+think\b",
]

_PHOTO_SIGNALS: List[str] = [
    r"\bphoto[sd]?\b",
    r"\bpicture[sd]?\b",
    r"\bimage[sd]?\b",
    r"\bshow\s+me\b",
    r"\blook[sd]?\s+like\b",
    r"\bsee\b",
    r"\bvisual[sd]?\b",
    r"\bsnapshot[sd]?\b",
    r"\bgallery\b",
    r"\bview[sd]?\b",
]


def _compile(signals: List[str]) -> List[re.Pattern]:
    return [re.compile(s, re.IGNORECASE) for s in signals]


_COMPILED: Dict[QueryIntent, List[re.Pattern]] = {
    QueryIntent.OPERATIONAL: _compile(_OPERATIONAL_SIGNALS),
    QueryIntent.AMENITY: _compile(_AMENITY_SIGNALS),
    QueryIntent.QUALITY: _compile(_QUALITY_SIGNALS),
    QueryIntent.PHOTO: _compile(_PHOTO_SIGNALS),
}


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

class IntentClassifier:
    """
    Lightweight rule-based intent classifier.

    Counts pattern matches per intent category and returns the winner.
    Tie-breaking order: OPERATIONAL > AMENITY > PHOTO > QUALITY.
    """

    # Tie-breaking priority (lower index = higher priority)
    _TIE_PRIORITY: List[QueryIntent] = [
        QueryIntent.OPERATIONAL,
        QueryIntent.AMENITY,
        QueryIntent.PHOTO,
        QueryIntent.QUALITY,
    ]

    def classify(self, query: str) -> Tuple[QueryIntent, float, float]:
        """
        Classify *query* and return (intent, confidence, latency_ms).

        Confidence is the fraction of total matches attributed to the
        winning intent (0.0 – 1.0).
        """
        start = time.monotonic()
        scores = self._score(query)
        total = sum(scores.values())
        if total == 0:
            intent = QueryIntent.UNKNOWN
            confidence = 0.0
        else:
            intent = self._pick_winner(scores)
            confidence = round(scores[intent] / total, 4)
        latency_ms = (time.monotonic() - start) * 1000
        return intent, confidence, latency_ms

    # ------------------------------------------------------------------
    def _score(self, query: str) -> Dict[QueryIntent, int]:
        scores: Dict[QueryIntent, int] = {i: 0 for i in QueryIntent if i != QueryIntent.UNKNOWN}
        for intent, patterns in _COMPILED.items():
            for pattern in patterns:
                if pattern.search(query):
                    scores[intent] += 1
        return scores

    def _pick_winner(self, scores: Dict[QueryIntent, int]) -> QueryIntent:
        max_score = max(scores.values())
        # Among tied intents keep the one with highest tie-priority
        for intent in self._TIE_PRIORITY:
            if scores.get(intent, 0) == max_score:
                return intent
        return QueryIntent.UNKNOWN
