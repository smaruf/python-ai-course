"""
Yelp-Style AI Assistant — Feature Presentation / Demo Module
=============================================================

Showcases every major capability of the assistant in a self-contained,
infrastructure-free way.  Runs entirely on the mock backend — no OpenAI
key, Redis, or vector DB required.

Sections
--------
  1. Intent classification   — classifies 8 sample queries, shows scores
  2. Query routing           — maps each intent to the correct services
  3. Structured authority    — hours and amenity look-ups from canonical data
  4. Conflict resolution     — structured data overrides contradictory reviews
  5. Cache behaviour         — L1 cache hit vs miss simulation
  6. Circuit breaker states  — CLOSED → OPEN → HALF_OPEN → CLOSED
  7. Full query pipeline     — end-to-end run for each intent type
  8. Ingestion pipelines     — streaming and batch processing demos
  9. Diagram catalogue       — lists all diagram files and their render URLs

Usage
-----
    # Run the full demo
    python -m demo.presentation

    # Run a specific section
    python -m demo.presentation --section intent
    python -m demo.presentation --section pipeline
    python -m demo.presentation --section diagrams

    # Quiet mode (no per-step pauses)
    python -m demo.presentation --no-pause
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Make project root importable regardless of working directory
# ---------------------------------------------------------------------------
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.cache.cache_layer import QueryCache
from src.ingestion.pipelines import (
    BatchIngestionPipeline,
    EventType,
    IngestionEvent,
    StreamingIngestionPipeline,
)
from src.intent.classifier import IntentClassifier
from src.models.schemas import (
    BusinessData,
    BusinessHours,
    EvidenceSummary,
    Photo,
    QueryIntent,
    QueryResponse,
    Review,
)
from src.orchestration.orchestrator import AnswerOrchestrator
from src.rag.rag_service import RAGService
from src.resilience.circuit_breaker import CircuitBreaker, CircuitState, ConcurrencyLimiter
from src.routing.router import QueryRouter
from src.search.services import (
    PhotoHybridRetrievalService,
    ReviewVectorSearchService,
    StructuredSearchService,
)


# ---------------------------------------------------------------------------
# Terminal styling helpers (no external deps)
# ---------------------------------------------------------------------------

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
GREEN  = "\033[32m"
CYAN   = "\033[36m"
YELLOW = "\033[33m"
RED    = "\033[31m"
BLUE   = "\033[34m"
MAGENTA = "\033[35m"

_PAUSE_ENABLED = True


def _h1(title: str) -> None:
    width = 70
    print(f"\n{BOLD}{BLUE}{'═' * width}{RESET}")
    print(f"{BOLD}{BLUE}  {title}{RESET}")
    print(f"{BOLD}{BLUE}{'═' * width}{RESET}")


def _h2(title: str) -> None:
    print(f"\n{BOLD}{CYAN}  ── {title} ──{RESET}")


def _ok(msg: str) -> None:
    print(f"  {GREEN}✔{RESET}  {msg}")


def _info(msg: str) -> None:
    print(f"  {CYAN}ℹ{RESET}  {msg}")


def _warn(msg: str) -> None:
    print(f"  {YELLOW}⚠{RESET}  {msg}")


def _row(label: str, value: Any, color: str = RESET) -> None:
    print(f"     {DIM}{label:<28}{RESET}{color}{value}{RESET}")


def _pause() -> None:
    if _PAUSE_ENABLED:
        input(f"\n  {DIM}Press Enter to continue…{RESET}")


# ---------------------------------------------------------------------------
# Shared fixture: demo business + services
# ---------------------------------------------------------------------------

def _build_demo_services() -> Tuple[
    BusinessData,
    StructuredSearchService,
    ReviewVectorSearchService,
    PhotoHybridRetrievalService,
]:
    """Create a fully populated demo business with services."""
    biz = BusinessData(
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
            "heated_patio":         True,
            "parking":              False,
            "wifi":                 True,
            "wheelchair_accessible": True,
            "vegan_options":        True,
            "dog_friendly":         False,
        },
        categories=["California Cuisine", "Seafood", "Wine Bar"],
        rating=4.6,
        review_count=512,
    )

    structured_svc = StructuredSearchService()
    structured_svc.add_business(biz)

    review_svc = ReviewVectorSearchService()
    for r in [
        Review("r1", "demo-001", "u1", 5.0,
               "The heated patio is phenomenal — warm and cosy even in foggy SF weather!"),
        Review("r2", "demo-001", "u2", 4.5,
               "Perfect for a romantic date night. The wine selection is outstanding."),
        Review("r3", "demo-001", "u3", 4.0,
               "Great vegan options, though parking nearby is a real pain on weekends."),
        Review("r4", "demo-001", "u4", 3.5,
               "Service was slow but the food quality more than made up for it."),
        Review("r5", "demo-001", "u5", 5.0,
               "Hands down the best seafood in the city. Strongly recommend the crab bisque."),
    ]:
        review_svc.add_review(r)

    photo_svc = PhotoHybridRetrievalService()
    for p in [
        Photo("p1", "demo-001", "https://cdn.example.com/golden-fork/patio-night.jpg",
              caption="Heated outdoor patio at night with string lights and heaters"),
        Photo("p2", "demo-001", "https://cdn.example.com/golden-fork/dining-room.jpg",
              caption="Elegant dining room interior with ocean views"),
        Photo("p3", "demo-001", "https://cdn.example.com/golden-fork/crab-bisque.jpg",
              caption="Award-winning dungeness crab bisque with sourdough"),
    ]:
        photo_svc.add_photo(p)

    return biz, structured_svc, review_svc, photo_svc


# ---------------------------------------------------------------------------
# Section 1: Intent Classification
# ---------------------------------------------------------------------------

DEMO_QUERIES: List[Tuple[str, QueryIntent]] = [
    ("Is The Golden Fork open right now?",               QueryIntent.OPERATIONAL),
    ("What time do they close on Friday?",               QueryIntent.OPERATIONAL),
    ("Do they have a heated patio?",                     QueryIntent.AMENITY),
    ("Is there parking available?",                      QueryIntent.AMENITY),
    ("Is it good for a romantic date night?",            QueryIntent.QUALITY),
    ("What do people say about the food quality?",       QueryIntent.QUALITY),
    ("Show me photos of the outdoor seating area",       QueryIntent.PHOTO),
    ("Can I see pictures of the heated patio?",          QueryIntent.PHOTO),
]


def demo_intent_classification() -> None:
    _h1("Section 1 — Intent Classification")
    _info("The IntentClassifier uses lightweight regex patterns (target < 20 ms).")
    _info("Each query is classified into: OPERATIONAL / AMENITY / QUALITY / PHOTO\n")

    clf = IntentClassifier()

    print(f"  {'Query':<52} {'Classified':<14} {'Confidence':>10}  {'Latency':>8}")
    print(f"  {'-'*52} {'-'*14} {'-'*10}  {'-'*8}")

    for query, expected in DEMO_QUERIES:
        intent, conf, ms = clf.classify(query)
        match_sym = GREEN + "✔" + RESET if intent == expected else YELLOW + "~" + RESET
        intent_color = {
            QueryIntent.OPERATIONAL: GREEN,
            QueryIntent.AMENITY:     CYAN,
            QueryIntent.QUALITY:     MAGENTA,
            QueryIntent.PHOTO:       YELLOW,
        }.get(intent, RESET)
        print(
            f"  {match_sym} {query:<50} "
            f"{intent_color}{intent.value:<14}{RESET} "
            f"{conf:>10.2%}  {ms:>6.2f} ms"
        )

    _pause()


# ---------------------------------------------------------------------------
# Section 2: Query Routing
# ---------------------------------------------------------------------------

def demo_query_routing() -> None:
    _h1("Section 2 — Query Routing Logic")
    _info("The QueryRouter maps each intent to the correct set of services.")
    _info("Structured data is authoritative — reviews/photos never override it.\n")

    router = QueryRouter()
    intents = [
        (QueryIntent.OPERATIONAL, "structured index only"),
        (QueryIntent.AMENITY,     "structured → review + photo fallback"),
        (QueryIntent.QUALITY,     "review vector search"),
        (QueryIntent.PHOTO,       "hybrid photo retrieval"),
        (QueryIntent.UNKNOWN,     "broad fallback (all sources)"),
    ]

    print(f"  {'Intent':<14} {'Structured':^12} {'Review Vec':^12} {'Photo Hybrid':^14}  Reason")
    print(f"  {'-'*14} {'-'*12} {'-'*12} {'-'*14}  {'-'*35}")

    for intent, description in intents:
        d = router.decide(intent)
        def _yn(v: bool) -> str:
            return (GREEN + "Yes" + RESET) if v else (DIM + "No " + RESET)
        print(
            f"  {intent.value:<14} {_yn(d.use_structured):^20} "
            f"{_yn(d.use_review_vector):^20} {_yn(d.use_photo_hybrid):^22}  "
            f"{DIM}{description}{RESET}"
        )

    _pause()


# ---------------------------------------------------------------------------
# Section 3: Structured Authority Demo
# ---------------------------------------------------------------------------

async def demo_structured_authority() -> None:
    _h1("Section 3 — Structured Data Authority")
    _info("Canonical fields (hours, amenities, address) always override reviews/photos.")

    biz, structured_svc, _, _ = _build_demo_services()
    orc = AnswerOrchestrator()
    router = QueryRouter()
    rag = RAGService(use_mock=True)

    queries = [
        ("What are the hours on Friday?",    QueryIntent.OPERATIONAL),
        ("Do they have a heated patio?",      QueryIntent.AMENITY),
        ("Is there parking?",                 QueryIntent.AMENITY),
        ("Are they wheelchair accessible?",   QueryIntent.AMENITY),
    ]

    for query, intent in queries:
        _h2(f'"{query}"')
        from src.routing.router import RoutedResults, RoutingDecision
        from src.search.services import StructuredSearchResult

        decision = router.decide(intent)
        results = await structured_svc.search(query, "demo-001")

        routed = RoutedResults(decision=decision, structured_results=results)
        bundle = orc.orchestrate(routed)
        response = await rag.generate_answer(query, intent, bundle)

        _row("Answer",      response.answer)
        _row("Confidence",  f"{response.confidence:.0%}")
        _row("Source",      "Structured (canonical)" if response.evidence.structured else "Reviews")
        _row("Latency",     f"{response.latency_ms:.1f} ms")

    _pause()


# ---------------------------------------------------------------------------
# Section 4: Conflict Resolution
# ---------------------------------------------------------------------------

async def demo_conflict_resolution() -> None:
    _h1("Section 4 — Conflict Resolution (Structured Wins)")
    _info("A review mentions 'dog friendly' — but canonical data says No.")
    _info("The orchestrator flags the conflict and structured data takes priority.\n")

    from src.routing.router import RoutedResults, RoutingDecision
    from src.search.services import ReviewSearchResult, StructuredSearchResult

    biz, structured_svc, review_svc, _ = _build_demo_services()
    # Add a conflicting review
    conflict_review = Review(
        "r_conflict", "demo-001", "u_conflict", 4.0,
        text="Brought my dog and they were totally dog friendly — loved it!"
    )
    review_svc.add_review(conflict_review)

    orc = AnswerOrchestrator()
    rag = RAGService(use_mock=True)

    # Run the amenity search which checks structured first
    structured_results = await structured_svc.search("Is the restaurant dog friendly?", "demo-001")
    review_results = await review_svc.search("dog friendly", "demo-001", top_k=3)

    decision = RoutingDecision(
        intent=QueryIntent.AMENITY, use_structured=True,
        use_review_vector=True, use_photo_hybrid=False
    )
    routed = RoutedResults(
        decision=decision,
        structured_results=structured_results,
        review_results=review_results,
    )
    bundle = orc.orchestrate(routed)

    _h2("Canonical data: dog_friendly = False")
    _row("Conflict notes detected", len(bundle.conflict_notes))
    for note in bundle.conflict_notes:
        _warn(note)

    response = await rag.generate_answer(
        "Is the restaurant dog friendly?", QueryIntent.AMENITY, bundle
    )
    _h2("Final answer (structured authority enforced)")
    _row("Answer",     response.answer)
    _row("Confidence", f"{response.confidence:.0%}")

    _pause()


# ---------------------------------------------------------------------------
# Section 5: Cache Behaviour
# ---------------------------------------------------------------------------

async def demo_cache_behaviour() -> None:
    _h1("Section 5 — Two-Tier Cache (L1 LRU + L2 Redis)")
    _info("Popular queries are cached for 5 minutes (TTL from TDD §10.2).")
    _info("L1 (in-process) serves the same request from memory in < 1 ms.\n")

    cache = QueryCache()  # Redis not connected — L1-only mode

    query   = "Is The Golden Fork open on Friday?"
    biz_id  = "demo-001"
    payload = {
        "answer":     "Open Friday 11:00–23:30.",
        "confidence": 0.95,
        "intent":     "operational",
        "evidence":   {"structured": True, "reviews_used": 0, "photos_used": 0},
    }

    # Miss
    t0 = time.monotonic()
    miss = await cache.get_query_result(biz_id, query)
    miss_ms = (time.monotonic() - t0) * 1_000
    _h2("Cache MISS")
    _row("Result",  repr(miss))
    _row("Latency", f"{miss_ms:.3f} ms")

    # Store
    await cache.set_query_result(biz_id, query, payload)
    _ok(f"Stored result in L1 cache (TTL = 300 s).  L1 size = {cache.l1_size()} entries")

    # Hit
    t0 = time.monotonic()
    hit = await cache.get_query_result(biz_id, query)
    hit_ms = (time.monotonic() - t0) * 1_000
    _h2("Cache HIT (L1)")
    _row("Result",  hit["answer"] if hit else "None")
    _row("Latency", f"{hit_ms:.3f} ms  {GREEN}(<<< miss path){RESET}")

    # Invalidation on data change
    await cache.invalidate_business(biz_id)
    _ok(f"Cache invalidated for business '{biz_id}'.  L1 size = {cache.l1_size()} entries")

    after = await cache.get_query_result(biz_id, query)
    _row("After invalidation", repr(after))

    _pause()


# ---------------------------------------------------------------------------
# Section 6: Circuit Breaker
# ---------------------------------------------------------------------------

async def demo_circuit_breaker() -> None:
    _h1("Section 6 — Circuit Breaker (Resilience)")
    _info("Each downstream service is wrapped in a circuit breaker.")
    _info("After 3 consecutive failures the circuit OPENs; calls short-circuit.\n")

    cb = CircuitBreaker("demo_service", failure_threshold=3, recovery_timeout=0.05)

    _h2("Simulating failures → circuit OPEN")

    async def _failing() -> None:
        raise ConnectionError("service unreachable")

    for attempt in range(1, 5):
        result = await cb.call(_failing, fallback="[fallback]")
        color = RED if cb.state == CircuitState.OPEN else YELLOW
        print(
            f"    Attempt {attempt}: state={color}{cb.state.value}{RESET}  "
            f"result={repr(result)}"
        )

    _h2("Simulating recovery → HALF_OPEN → CLOSED")
    # Wait out the recovery timeout
    await asyncio.sleep(0.06)

    async def _succeeding() -> str:
        return "OK"

    for attempt in range(1, 4):
        result = await cb.call(_succeeding, fallback="[fallback]")
        color = GREEN if cb.state == CircuitState.CLOSED else CYAN
        print(
            f"    Attempt {attempt}: state={color}{cb.state.value}{RESET}  "
            f"result={repr(result)}"
        )

    _h2("Concurrency Limiter")
    limiter = ConcurrencyLimiter("vector_search", max_concurrent=3)
    _info(f"Semaphore slots: {limiter.available} / 3")
    async with limiter:
        _info(f"Inside context: {limiter.available} / 3")
    _info(f"After exit:    {limiter.available} / 3")

    _pause()


# ---------------------------------------------------------------------------
# Section 7: Full End-to-End Pipeline
# ---------------------------------------------------------------------------

async def demo_full_pipeline() -> None:
    _h1("Section 7 — Full Query Pipeline (end-to-end)")
    _info("Runs each query through: Intent → Router → Search → Orchestrate → RAG\n")

    _, structured_svc, review_svc, photo_svc = _build_demo_services()
    router  = QueryRouter()
    clf     = IntentClassifier()
    orc     = AnswerOrchestrator()
    rag     = RAGService(use_mock=True)

    queries = [
        "What time does The Golden Fork close on Saturday?",
        "Do they have a heated patio?",
        "Is it good for a romantic evening?",
        "Show me photos of the outdoor seating",
    ]

    for query in queries:
        _h2(f'"{query}"')
        t_start = time.monotonic()

        intent, conf, cls_ms = clf.classify(query)

        routed = await router.route(
            query=query,
            business_id="demo-001",
            intent=intent,
            structured_service=structured_svc,
            review_service=review_svc,
            photo_service=photo_svc,
        )

        bundle   = orc.orchestrate(routed)
        response = await rag.generate_answer(query, intent, bundle)

        total_ms = (time.monotonic() - t_start) * 1_000
        response.latency_ms = round(total_ms, 1)

        _row("Intent",        f"{intent.value}  (confidence {conf:.0%}, classified in {cls_ms:.1f} ms)")
        _row("Answer",        response.answer)
        _row("Confidence",    f"{response.confidence:.0%}")
        _row("Structured src",str(response.evidence.structured))
        _row("Reviews used",  response.evidence.reviews_used)
        _row("Photos used",   response.evidence.photos_used)
        _row("Total latency", f"{response.latency_ms} ms")
        if bundle.conflict_notes:
            for note in bundle.conflict_notes:
                _warn(f"Conflict: {note}")

    _pause()


# ---------------------------------------------------------------------------
# Section 8: Ingestion Pipelines
# ---------------------------------------------------------------------------

async def demo_ingestion() -> None:
    _h1("Section 8 — Ingestion Pipelines")

    _h2("Streaming Pipeline (Kafka CDC — reviews / hours / photos)")
    pipeline = StreamingIngestionPipeline()
    log: List[str] = []

    async def on_review(event: IngestionEvent) -> None:
        log.append(f"  {GREEN}[STREAM]{RESET} {event.event_type.value} for biz={event.business_id}")

    for et in (EventType.REVIEW_CREATED, EventType.RATING_UPDATED, EventType.HOURS_CHANGED):
        pipeline.register_handler(et, on_review)

    events = [
        IngestionEvent(EventType.REVIEW_CREATED, "demo-001", {"review_id": "r_new", "rating": 5}),
        IngestionEvent(EventType.RATING_UPDATED,  "demo-001", {"new_rating": 4.7}),
        IngestionEvent(EventType.HOURS_CHANGED,   "demo-001", {"day": "monday", "close_time": "23:00"}),
        IngestionEvent(EventType.REVIEW_CREATED, "demo-002", {"review_id": "r_other"}),
    ]
    for e in events:
        await pipeline.publish(e)

    processed = await pipeline.drain()
    for msg in log:
        print(msg)

    _ok(f"Processed {len(processed)} events")
    sla_met = sum(1 for e in processed if pipeline.check_freshness_sla(e))
    _row("SLA met (< review window)",   f"{sla_met} / {len(processed)}")

    _h2("Batch Pipeline (weekly ETL — menus / static content)")
    batch = BatchIngestionPipeline()

    def menu_job(records: list) -> int:
        for r in records:
            _ = r.get("menu_item", "")  # simulate processing
        return len(records)

    batch.register_job(menu_job)
    menu_records = [
        {"menu_item": "Dungeness Crab Bisque", "price": 18.0},
        {"menu_item": "Pan-Seared Halibut",    "price": 42.0},
        {"menu_item": "Vegan Buddha Bowl",     "price": 24.0},
    ]
    summary = await batch.run(menu_records)
    _row("Records in",       summary["records_in"])
    _row("Records processed",summary["records_processed"])
    _row("Errors",           len(summary["errors"]) or "none")

    _pause()


# ---------------------------------------------------------------------------
# Section 9: Diagram Catalogue
# ---------------------------------------------------------------------------

def demo_diagrams() -> None:
    _h1("Section 9 — Diagram Catalogue")

    project_root = Path(_PROJECT_ROOT)
    puml_dir     = project_root / "diagram_sources" / "plantuml"
    pydiag_dir   = project_root / "diagram_sources" / "pydiagram"

    _h2("PlantUML Source Files (.puml)")
    puml_files = sorted(puml_dir.glob("*.puml")) if puml_dir.exists() else []
    if puml_files:
        try:
            from diagram_sources.plantuml_renderer import PlantUMLRenderer
            renderer = PlantUMLRenderer()
            for f in puml_files:
                url = renderer.url_for_file(str(f), fmt="png")
                _row(f.name, f"{CYAN}{url[:80]}…{RESET}" if len(url) > 80 else f"{CYAN}{url}{RESET}")
                _ok(f"  Render at: {url}")
        except Exception as exc:  # noqa: BLE001
            for f in puml_files:
                _row(f.name, str(f))
            _warn(f"URL generation failed: {exc}")
    else:
        _warn("No .puml files found.")

    _h2("PyDiagram Scripts (diagrams library)")
    py_files = sorted(pydiag_dir.glob("*.py")) if pydiag_dir.exists() else []
    for f in py_files:
        if f.name.startswith("_"):
            continue
        _row(f.stem, str(f))
        _info(f"  Run: python -m diagram_sources.pydiagram.{f.stem} [output_dir]")

    _h2("Mermaid Docs")
    doc_dir = project_root / "docs"
    for md in sorted(doc_dir.glob("*.md")) if doc_dir.exists() else []:
        _row(md.name, str(md))


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

SECTIONS: Dict[str, Any] = {
    "intent":    ("Intent Classification",   demo_intent_classification),
    "routing":   ("Query Routing",           demo_query_routing),
    "structured":("Structured Authority",    demo_structured_authority),
    "conflict":  ("Conflict Resolution",     demo_conflict_resolution),
    "cache":     ("Cache Behaviour",         demo_cache_behaviour),
    "breaker":   ("Circuit Breaker",         demo_circuit_breaker),
    "pipeline":  ("Full Query Pipeline",     demo_full_pipeline),
    "ingestion": ("Ingestion Pipelines",     demo_ingestion),
    "diagrams":  ("Diagram Catalogue",       demo_diagrams),
}


async def run_demo(sections: Optional[List[str]] = None) -> None:
    """Run all demo sections (or a subset by key)."""
    _h1("Yelp-Style AI Assistant — Feature Presentation")
    _info("Production-grade AI assistant: RAG + hybrid search + freshness pipelines")
    _info("All sections run on the mock backend — no external services required.\n")

    keys = sections or list(SECTIONS.keys())
    for key in keys:
        if key not in SECTIONS:
            _warn(f"Unknown section '{key}'. Available: {', '.join(SECTIONS)}")
            continue
        _label, func = SECTIONS[key]
        if asyncio.iscoroutinefunction(func):
            await func()
        else:
            func()

    _h1("Demo Complete")
    _ok("All sections finished.  Happy building! 🚀")


def main() -> None:
    global _PAUSE_ENABLED

    parser = argparse.ArgumentParser(
        description="Yelp-Style AI Assistant — Feature Presentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join(
            f"  {k:<12} {v[0]}" for k, v in SECTIONS.items()
        ),
    )
    parser.add_argument(
        "--section", "-s",
        choices=list(SECTIONS.keys()),
        action="append",
        dest="sections",
        metavar="SECTION",
        help="Run only the specified section(s) (repeatable)",
    )
    parser.add_argument(
        "--no-pause",
        action="store_true",
        help="Disable interactive pauses between sections",
    )
    args = parser.parse_args()

    if args.no_pause:
        _PAUSE_ENABLED = False

    asyncio.run(run_demo(sections=args.sections))


if __name__ == "__main__":
    main()
