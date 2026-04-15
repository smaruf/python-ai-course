"""
Camel AI Data Pipeline — Locust Load Test Entry Point
=====================================================
Combines all per-level scenario users into a single locustfile so the
full suite can be run with one command.

Usage
-----
# Interactive web UI (default http://localhost:8089)
locust -f locustfile.py --host http://localhost:8080

# Headless / CI mode  (5 users, 1 spawn/sec, 60 s)
locust -f locustfile.py \
       --host http://localhost:8080 \
       --headless -u 5 -r 1 -t 60s \
       --csv results/load_test \
       --html results/load_test_report.html

# Run only a specific level
locust -f locustfile.py \
       --host http://localhost:8080 \
       --headless -u 5 -r 1 -t 30s \
       --tags level0

Scenario weights
----------------
| Class                | Level | Relative weight |
|----------------------|-------|----------------|
| Level0User           | 0     | 3 (high — cheapest endpoint) |
| Level3AiEnrichUser   | 3     | 2 |
| Level6RagUser        | 6     | 2 |
| Level7MarketDataUser | 7     | 1 (lower — heavy AI calls) |
"""

from scenarios.level0_routes import Level0User
from scenarios.level3_ai_enrichment import Level3AiEnrichUser
from scenarios.level6_rag import Level6RagUser
from scenarios.level7_market_data import Level7MarketDataUser

__all__ = [
    "Level0User",
    "Level3AiEnrichUser",
    "Level6RagUser",
    "Level7MarketDataUser",
]
