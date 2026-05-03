# Load Tests — Camel AI Data Pipeline

Python-based load test suite using **Locust**, with per-level scenarios and an automated result analysis tool.

> **[← Back to Project](../README.md)**

---

## 📁 Structure

```
load-tests/
├── locustfile.py                   # Entry point — imports all scenario users
├── requirements.txt
├── README.md                       # This file
├── scenarios/
│   ├── level0_routes.py            # Level 0: REST echo endpoint
│   ├── level3_ai_enrichment.py     # Level 3: AI enrichment API
│   ├── level6_rag.py               # Level 6: RAG /ask and /embed endpoints
│   └── level7_market_data.py       # Level 7: Market tick ingest + alerts
├── analysis/
│   └── analyze_results.py          # Parse Locust CSV → console + HTML + Markdown report
└── tests/
    └── test_analyze_results.py     # Unit tests for the analyser (no live server needed)
```

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
cd camel-ai-data-pipeline/load-tests
pip install -r requirements.txt
```

### 2. Start the target application

```bash
# Example: Level 0 on port 8080
cd ../level-0-fundamentals
mvn spring-boot:run
```

### 3. Run load tests — interactive web UI

```bash
locust -f locustfile.py --host http://localhost:8080
# Open http://localhost:8089 to configure and start the test
```

### 4. Run load tests — headless (CI mode)

```bash
mkdir -p results
locust -f locustfile.py \
       --host http://localhost:8080 \
       --headless -u 10 -r 2 -t 60s \
       --csv results/load_test \
       --html results/load_test_report.html
```

### 5. Analyse results

```bash
python analysis/analyze_results.py --csv-prefix results/load_test --output-dir results
```

This produces:
- `results/analysis_report.md` — Markdown table with SLO badges
- `results/analysis_report.html` — Styled HTML dashboard

---

## 🧪 Run Unit Tests (no server needed)

```bash
pytest tests/ -v
```

---

## 🎯 Scenario Overview

| File | Level | Endpoints tested | Locust weight |
|------|-------|-----------------|---------------|
| `level0_routes.py` | 0 | `POST /api/message`, `GET /actuator/health` | 3 (high) |
| `level3_ai_enrichment.py` | 3 | `POST /api/enrich/sentiment`, `/batch`, `/status` | 2 |
| `level6_rag.py` | 6 | `POST /api/ask`, `/embed`, `GET /api/search` | 2 |
| `level7_market_data.py` | 7 | `POST /api/ticks`, `GET /api/alerts`, `/api/symbols/{sym}` | 1 (low — heavy AI) |

Use `--tags` to run a single level:

```bash
locust -f locustfile.py --host http://localhost:8080 --headless -u 5 -r 1 -t 30s --tags level0
```

---

## 📊 SLO Thresholds

| Metric | Threshold |
|--------|-----------|
| P95 response time | < 2000 ms |
| Error rate | < 1.0 % |
| Minimum sustained RPS | ≥ 5 |

The analyser exits with code `1` if any SLO is violated — suitable as a CI gate.

---

## 🔧 Configuration

All SLO thresholds are constants at the top of `analysis/analyze_results.py`:

```python
SLO_P95_MS:         float = 2000.0   # 95th-percentile latency ceiling
SLO_ERROR_RATE_PCT: float = 1.0      # maximum acceptable error rate
SLO_RPS_MIN:        float = 5.0      # minimum required throughput
```
