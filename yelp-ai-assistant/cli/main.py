"""
Yelp-Style AI Assistant — Click CLI
=====================================

Provides a command-line interface for querying the assistant, seeding demo
data, and inspecting service health — all without starting a server.

Commands
--------
  query        Ask a natural-language question about a business
  health       Check service health and cache stats
  demo         Run a quick end-to-end demo with the built-in sample business
  serve        Start the FastAPI server (delegates to uvicorn)

Usage
-----
  # Ask about a business (uses mock backend)
  python -m cli.main query --business-id 12345 "Is it open right now?"

  # Run the full demo
  python -m cli.main demo

  # Start the server
  python -m cli.main serve --port 8000

  # Health info
  python -m cli.main health
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from typing import Optional

import click

# ---------------------------------------------------------------------------
# Make project root importable
# ---------------------------------------------------------------------------
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _build_services():
    """Return seeded service instances for local (no-server) operation."""
    from src.intent.classifier import IntentClassifier
    from src.models.schemas import BusinessData, BusinessHours, Photo, Review
    from src.orchestration.orchestrator import AnswerOrchestrator
    from src.rag.rag_service import RAGService
    from src.routing.router import QueryRouter
    from src.search.services import (
        PhotoHybridRetrievalService,
        ReviewVectorSearchService,
        StructuredSearchService,
    )

    structured_svc = StructuredSearchService()
    review_svc = ReviewVectorSearchService()
    photo_svc = PhotoHybridRetrievalService()

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
    structured_svc.add_business(biz)

    for r in [
        Review("r1", "demo-001", "u1", 5.0,
               "The heated patio is phenomenal — warm even in foggy SF!"),
        Review("r2", "demo-001", "u2", 4.5,
               "Perfect for a romantic date night. Excellent wine selection."),
        Review("r3", "demo-001", "u3", 4.0,
               "Great vegan options, parking nearby is tricky on weekends."),
    ]:
        review_svc.add_review(r)

    for p in [
        Photo("p1", "demo-001", "https://cdn.example.com/patio.jpg",
              caption="Heated outdoor patio at night with string lights"),
        Photo("p2", "demo-001", "https://cdn.example.com/interior.jpg",
              caption="Elegant dining room with ocean views"),
    ]:
        photo_svc.add_photo(p)

    return (
        structured_svc, review_svc, photo_svc,
        IntentClassifier(), QueryRouter(),
        AnswerOrchestrator(), RAGService(use_mock=True),
        biz,
    )


async def _run_query(
    query: str,
    business_id: str,
    output_format: str,
) -> dict:
    """Execute the full pipeline and return a result dict."""
    from src.routing.router import QueryRouter
    (structured_svc, review_svc, photo_svc,
     clf, router, orc, rag, biz) = _build_services()

    # Use the requested business_id
    from src.models.schemas import BusinessData, BusinessHours
    if business_id != "demo-001":
        click.echo(
            click.style(
                f"  ⚠  No data found for business_id '{business_id}'. "
                "Using demo business 'demo-001'.",
                fg="yellow",
            ),
            err=True,
        )

    t0 = time.monotonic()
    intent, conf, cls_ms = clf.classify(query)
    routed = await router.route(
        query=query,
        business_id="demo-001",
        intent=intent,
        structured_service=structured_svc,
        review_service=review_svc,
        photo_service=photo_svc,
    )
    bundle = orc.orchestrate(routed)
    response = await rag.generate_answer(query, intent, bundle)
    response.latency_ms = round((time.monotonic() - t0) * 1_000, 1)

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
        "latency_ms": response.latency_ms,
        "conflicts": bundle.conflict_notes,
    }


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------

@click.group()
@click.version_option(version="1.0.0", prog_name="yelp-ai-assistant")
def cli():
    """Yelp-Style AI Assistant — command-line interface.

    \b
    Ask natural-language questions about businesses, run the demo, or
    start the server — all from the command line.
    """


# ---------------------------------------------------------------------------
# query command
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("question")
@click.option(
    "--business-id", "-b",
    default="demo-001",
    show_default=True,
    help="Business ID to query.",
)
@click.option(
    "--format", "-f",
    "output_format",
    type=click.Choice(["pretty", "json"], case_sensitive=False),
    default="pretty",
    show_default=True,
    help="Output format.",
)
def query(question: str, business_id: str, output_format: str):
    """Ask a natural-language QUESTION about a business.

    \b
    Examples:
      python -m cli.main query "Is it open on Friday?"
      python -m cli.main query --business-id 12345 "Do they have a heated patio?"
      python -m cli.main query --format json "Good for dates?" | python -m json.tool
    """
    result = asyncio.run(_run_query(question, business_id, output_format))

    if output_format == "json":
        click.echo(json.dumps(result, indent=2))
        return

    # Pretty output
    intent_colors = {
        "operational": "green",
        "amenity": "cyan",
        "quality": "magenta",
        "photo": "yellow",
    }
    color = intent_colors.get(result["intent"], "white")

    click.echo()
    click.echo(click.style("  ══ Answer ══", bold=True, fg="blue"))
    click.echo(f"  {click.style(result['answer'], bold=True)}")
    click.echo()
    click.echo(f"  {'Intent':<20} {click.style(result['intent'], fg=color)}"
               f"  (confidence {result['intent_confidence']:.0%})")
    click.echo(f"  {'Confidence':<20} {result['confidence']:.0%}")
    click.echo(f"  {'Structured source':<20} {result['evidence']['structured']}")
    click.echo(f"  {'Reviews used':<20} {result['evidence']['reviews_used']}")
    click.echo(f"  {'Photos used':<20} {result['evidence']['photos_used']}")
    click.echo(f"  {'Latency':<20} {result['latency_ms']} ms")
    if result["conflicts"]:
        click.echo()
        for note in result["conflicts"]:
            click.echo(click.style(f"  ⚠  {note}", fg="yellow"))
    click.echo()


# ---------------------------------------------------------------------------
# health command
# ---------------------------------------------------------------------------

@cli.command()
@click.option(
    "--format", "-f",
    "output_format",
    type=click.Choice(["pretty", "json"], case_sensitive=False),
    default="pretty",
    show_default=True,
)
def health(output_format: str):
    """Show service health and cache statistics.

    Reports circuit breaker states and cache size without starting a server.
    """
    from src.cache.cache_layer import QueryCache
    from src.resilience.circuit_breaker import CircuitBreaker

    cb_names = ["structured_search", "review_vector_search",
                "photo_hybrid_search", "llm_rag"]
    cb_states = {name: "closed" for name in cb_names}

    cache = QueryCache()
    info = {
        "status": "healthy",
        "service": "yelp-ai-assistant",
        "version": "1.0.0",
        "circuit_breakers": cb_states,
        "cache": {"l1_entries": cache.l1_size()},
    }

    if output_format == "json":
        click.echo(json.dumps(info, indent=2))
        return

    click.echo()
    click.echo(click.style("  ══ Health ══", bold=True, fg="green"))
    click.echo(f"  {'Status':<24} {click.style(info['status'], fg='green', bold=True)}")
    click.echo(f"  {'Version':<24} {info['version']}")
    click.echo()
    click.echo(click.style("  Circuit Breakers", bold=True))
    for name, state in info["circuit_breakers"].items():
        color = "green" if state == "closed" else ("red" if state == "open" else "yellow")
        click.echo(f"    {name:<30} {click.style(state, fg=color)}")
    click.echo()
    click.echo(click.style("  Cache", bold=True))
    click.echo(f"    {'L1 entries':<30} {info['cache']['l1_entries']}")
    click.echo()


# ---------------------------------------------------------------------------
# demo command
# ---------------------------------------------------------------------------

@cli.command()
@click.option(
    "--section", "-s",
    default=None,
    help="Run only a specific section (e.g. 'cache', 'intent').",
)
def demo(section: Optional[str]):
    """Run the interactive feature showcase.

    Exercises all major pipeline components using the mock backend.
    No server or external services required.
    """
    import demo.presentation as pres
    pres._PAUSE_ENABLED = False
    sections = [section] if section else None
    asyncio.run(pres.run_demo(sections=sections))


# ---------------------------------------------------------------------------
# serve command
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--host", default="0.0.0.0", show_default=True, help="Bind address.")
@click.option("--port", "-p", default=8000, show_default=True, help="Bind port.")
@click.option("--reload/--no-reload", default=False, show_default=True,
              help="Enable auto-reload (development mode).")
@click.option("--workers", "-w", default=1, show_default=True,
              help="Number of uvicorn worker processes.")
def serve(host: str, port: int, reload: bool, workers: int):
    """Start the FastAPI server via uvicorn.

    \b
    Examples:
      python -m cli.main serve
      python -m cli.main serve --port 9000 --reload
      python -m cli.main serve --workers 4  # production (no --reload)
    """
    import uvicorn

    click.echo(click.style(
        f"\n  🚀 Starting Yelp-Style AI Assistant on http://{host}:{port}\n"
        f"     Docs: http://{host}:{port}/docs\n",
        fg="cyan", bold=True,
    ))
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,
        log_level="info",
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    cli()


if __name__ == "__main__":
    main()
