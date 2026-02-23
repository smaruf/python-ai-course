"""
Yelp-Style AI Assistant — Gradio Web UI
========================================

Provides a browser-based interface for the Yelp-Style AI Assistant.

Layout
------
  - Natural-language question text box
  - Business dropdown (pre-seeded demo businesses)
  - Formatted Markdown answer panel with intent badge
  - Raw JSON accordion for developers
  - 8 clickable example queries

Running
-------
  python -m gui.app           # http://localhost:7860
  python -m gui.app --share   # public Gradio share link

Design
------
  ``build_interface()`` constructs the ``gr.Blocks`` object independently of
  ``launch()`` so it can be tested without starting a server.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from typing import Tuple

# ---------------------------------------------------------------------------
# Make project root importable
# ---------------------------------------------------------------------------
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import gradio as gr

from src.intent.classifier import IntentClassifier
from src.models.schemas import (
    BusinessData,
    BusinessHours,
    Photo,
    QueryIntent,
    Review,
)
from src.orchestration.orchestrator import AnswerOrchestrator
from src.rag.rag_service import RAGService
from src.routing.router import QueryRouter
from src.search.services import (
    PhotoHybridRetrievalService,
    ReviewVectorSearchService,
    StructuredSearchService,
)

# ---------------------------------------------------------------------------
# Demo business data
# ---------------------------------------------------------------------------

_BUSINESSES: dict[str, BusinessData] = {}

_structured_svc = StructuredSearchService()
_review_svc = ReviewVectorSearchService()
_photo_svc = PhotoHybridRetrievalService()
_clf = IntentClassifier()
_router = QueryRouter()
_orc = AnswerOrchestrator()
_rag = RAGService(use_mock=True)


def _seed_businesses() -> None:
    """Populate the two demo businesses used throughout the UI."""
    biz1 = BusinessData(
        business_id="demo-001",
        name="The Golden Fork",
        address="42 Harbour Lane, San Francisco, CA 94105",
        phone="+1-415-555-0199",
        price_range="$$$",
        hours=[
            BusinessHours("monday",    "11:00", "22:00"),
            BusinessHours("tuesday",   "11:00", "22:00"),
            BusinessHours("wednesday", "11:00", "22:00"),
            BusinessHours("thursday",  "11:00", "23:00"),
            BusinessHours("friday",    "11:00", "23:30"),
            BusinessHours("saturday",  "10:00", "23:30"),
            BusinessHours("sunday",    "10:00", "21:00"),
        ],
        amenities={
            "heated_patio": True,
            "parking": False,
            "wifi": True,
            "wheelchair_accessible": True,
            "vegan_options": True,
        },
        categories=["California Cuisine", "Seafood", "Wine Bar"],
        rating=4.6,
        review_count=512,
    )
    _structured_svc.add_business(biz1)
    _BUSINESSES["demo-001"] = biz1

    for r in [
        Review("r1", "demo-001", "u1", 5.0,
               "The heated patio is phenomenal — warm even in foggy SF!"),
        Review("r2", "demo-001", "u2", 4.5,
               "Perfect for a romantic date night. Excellent wine selection."),
        Review("r3", "demo-001", "u3", 4.0,
               "Great vegan options. Parking nearby is tricky on weekends."),
    ]:
        _review_svc.add_review(r)

    for p in [
        Photo("p1", "demo-001", "https://cdn.example.com/patio.jpg",
              caption="Heated outdoor patio at night with string lights"),
        Photo("p2", "demo-001", "https://cdn.example.com/interior.jpg",
              caption="Elegant dining room with ocean views"),
    ]:
        _photo_svc.add_photo(p)

    biz2 = BusinessData(
        business_id="demo-002",
        name="The Rustic Table",
        address="123 Main St, New York, NY 10001",
        phone="+1-212-555-0100",
        price_range="$$",
        hours=[
            BusinessHours("monday",    "09:00", "22:00"),
            BusinessHours("tuesday",   "09:00", "22:00"),
            BusinessHours("wednesday", "09:00", "22:00"),
            BusinessHours("thursday",  "09:00", "22:00"),
            BusinessHours("friday",    "09:00", "23:00"),
            BusinessHours("saturday",  "10:00", "23:00"),
            BusinessHours("sunday",    "10:00", "21:00"),
        ],
        amenities={
            "heated_patio": True,
            "parking": False,
            "wifi": True,
            "wheelchair_accessible": True,
        },
        categories=["American", "Brunch", "Bar"],
        rating=4.3,
        review_count=215,
    )
    _structured_svc.add_business(biz2)
    _BUSINESSES["demo-002"] = biz2

    for r in [
        Review("r4", "demo-002", "u4", 5.0,
               "Amazing heated patio — perfect for winter evenings. Great cocktails!"),
        Review("r5", "demo-002", "u5", 4.0,
               "Lovely atmosphere for a date night. Food was excellent."),
        Review("r6", "demo-002", "u6", 3.5,
               "Good for groups. Parking nearby is tricky on weekends."),
    ]:
        _review_svc.add_review(r)

    for p in [
        Photo("p3", "demo-002", "https://cdn.example.com/rustic-patio.jpg",
              caption="Outdoor heated patio with string lights in winter"),
        Photo("p4", "demo-002", "https://cdn.example.com/rustic-interior.jpg",
              caption="Cozy interior with rustic wooden decor"),
    ]:
        _photo_svc.add_photo(p)


_seed_businesses()


# ---------------------------------------------------------------------------
# Sample queries shown as examples in the UI
# ---------------------------------------------------------------------------

SAMPLE_QUERIES = [
    "Is it open right now?",
    "Do they have a heated patio?",
    "What time do they close on Saturday?",
    "Is it good for a romantic date night?",
    "Show me photos of the outdoor seating",
    "Do they offer vegan options?",
    "Is there wheelchair access?",
    "What is the price range?",
]

# ---------------------------------------------------------------------------
# Intent → emoji badge mapping
# ---------------------------------------------------------------------------

_INTENT_BADGE: dict[str, str] = {
    QueryIntent.OPERATIONAL: "🕐 Operational",
    QueryIntent.AMENITY:     "🏗️ Amenity",
    QueryIntent.QUALITY:     "⭐ Quality",
    QueryIntent.PHOTO:       "📷 Photo",
    QueryIntent.UNKNOWN:     "❓ Unknown",
}


# ---------------------------------------------------------------------------
# Core ask function (sync wrapper around async pipeline)
# ---------------------------------------------------------------------------

def _ask(query: str, business_id: str) -> Tuple[str, str, str]:
    """
    Run the full assistant pipeline for *query* / *business_id*.

    Returns
    -------
    (answer_markdown, intent_markdown, raw_json_str)
    """
    if not query or not query.strip():
        warning = "⚠️ Please enter a question to get started."
        return warning, "", json.dumps({"error": "empty query"})

    try:
        result = asyncio.run(_pipeline(query, business_id))
    except RuntimeError:
        # Already inside an event loop (e.g. during testing)
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(_pipeline(query, business_id))
        finally:
            loop.close()

    intent_val = result["intent"]
    badge = _INTENT_BADGE.get(intent_val, f"❓ {intent_val}")
    conf_pct = int(result["confidence"] * 100)
    conf_bar = "█" * (conf_pct // 10) + "░" * (10 - conf_pct // 10)

    # ── Answer markdown ──────────────────────────────────────────────────────
    answer_md_parts = [
        f"### {result['answer']}",
        "",
        f"**Confidence:** `{conf_bar}` {conf_pct}%",
        "",
        "| Evidence | Value |",
        "|---|---|",
        f"| Structured source | {'✅' if result['evidence']['structured'] else '❌'} |",
        f"| Reviews used | {result['evidence']['reviews_used']} |",
        f"| Photos used  | {result['evidence']['photos_used']} |",
        f"| Latency | {result['latency_ms']} ms |",
    ]
    if result.get("conflicts"):
        answer_md_parts += ["", "---", "**⚠️ Conflict notes:**"]
        for note in result["conflicts"]:
            answer_md_parts.append(f"- {note}")
    answer_md = "\n".join(answer_md_parts)

    # ── Intent markdown ──────────────────────────────────────────────────────
    intent_md = f"**Intent:** {badge}"

    # ── Raw JSON ─────────────────────────────────────────────────────────────
    raw = json.dumps(result, indent=2, default=str)

    return answer_md, intent_md, raw


async def _pipeline(query: str, business_id: str) -> dict:
    """Async pipeline: intent → route → orchestrate → RAG."""
    import time

    t0 = time.monotonic()
    intent, conf, _ = _clf.classify(query)
    routed = await _router.route(
        query=query,
        business_id=business_id,
        intent=intent,
        structured_service=_structured_svc,
        review_service=_review_svc,
        photo_service=_photo_svc,
    )
    bundle = _orc.orchestrate(routed)
    response = await _rag.generate_answer(query, intent, bundle)
    latency_ms = round((time.monotonic() - t0) * 1_000, 1)

    return {
        "query": query,
        "business_id": business_id,
        "intent": intent.value,
        "intent_confidence": round(conf, 4),
        "answer": response.answer,
        "confidence": response.confidence,
        "evidence": {
            "structured": response.evidence.structured,
            "reviews_used": response.evidence.reviews_used,
            "photos_used": response.evidence.photos_used,
        },
        "latency_ms": latency_ms,
        "conflicts": bundle.conflict_notes,
    }


# ---------------------------------------------------------------------------
# Gradio interface builder
# ---------------------------------------------------------------------------

def build_interface() -> gr.Blocks:
    """Construct and return the Gradio Blocks interface (does not launch)."""

    business_choices = [
        (f"demo-001 — The Golden Fork (SF)", "demo-001"),
        (f"demo-002 — The Rustic Table (NYC)", "demo-002"),
    ]

    with gr.Blocks(
        title="Yelp-Style AI Assistant",
        theme=gr.themes.Soft(),
    ) as demo:
        gr.Markdown(
            "# 🍽️ Yelp-Style AI Assistant\n"
            "Ask a natural-language question about a business. "
            "The assistant uses structured data, reviews, and photos to answer."
        )

        with gr.Row():
            with gr.Column(scale=3):
                question_box = gr.Textbox(
                    label="Your question",
                    placeholder="e.g. Is it open right now? Do they have a heated patio?",
                    lines=2,
                )
            with gr.Column(scale=1):
                business_dd = gr.Dropdown(
                    choices=business_choices,
                    value="demo-001",
                    label="Business",
                )

        ask_btn = gr.Button("Ask", variant="primary")

        with gr.Row():
            intent_out = gr.Markdown(label="Intent")

        answer_out = gr.Markdown(label="Answer")

        with gr.Accordion("Raw JSON (developer view)", open=False):
            json_out = gr.Code(language="json", label="Response payload")

        gr.Examples(
            examples=[[q, "demo-001"] for q in SAMPLE_QUERIES],
            inputs=[question_box, business_dd],
            label="Example queries",
        )

        # Wire up the button and Enter key
        ask_btn.click(
            fn=_ask,
            inputs=[question_box, business_dd],
            outputs=[answer_out, intent_out, json_out],
        )
        question_box.submit(
            fn=_ask,
            inputs=[question_box, business_dd],
            outputs=[answer_out, intent_out, json_out],
        )

    return demo


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def launch(share: bool = False, port: int = 7860) -> None:
    """Build and launch the Gradio interface."""
    iface = build_interface()
    iface.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=share,
        show_error=True,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Yelp-Style AI Assistant — Gradio UI")
    parser.add_argument("--share",  action="store_true", help="Create public Gradio link")
    parser.add_argument("--port",   type=int, default=7860, help="Server port (default 7860)")
    args = parser.parse_args()

    launch(share=args.share, port=args.port)
