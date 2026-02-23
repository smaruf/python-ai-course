# Yelp-Style AI Assistant 🍽️

> **Part of [Python AI Course](../README.md)** - A comprehensive learning repository covering AI, algorithms, and real-world applications.  
> See also: [AI Development Project](../ai-development-project/) | [LangChain + LangGraph](../projects/langchain-langgraph-standalone/) | [Oracle AI Prep](../oracle-job-prep/)

A production-grade AI assistant for answering real-time business-related queries using hybrid freshness data ingestion, structured + unstructured data separation, hybrid photo retrieval, and Retrieval-Augmented Generation (RAG).

## Architecture

```
User
  ↓
POST /assistant/query
  ↓
Intent Classifier  (< 20 ms)
  ↓
Query Router
  ↓
┌────────────────────────────────────┐
│ StructuredSearchService            │
│ ReviewVectorSearchService          │
│ PhotoHybridRetrievalService        │
└────────────────────────────────────┘
  ↓
AnswerOrchestrator
  ↓
RAGService (LLM)
  ↓
QueryResponse
```

## Project Structure

```
yelp-ai-assistant/
├── main.py                      # FastAPI application entry point
├── requirements.txt
├── README.md
├── src/
│   ├── models/
│   │   └── schemas.py           # Data models (BusinessData, Review, Photo, API contracts)
│   ├── intent/
│   │   └── classifier.py        # Lightweight intent classifier (< 20 ms)
│   ├── routing/
│   │   └── router.py            # Query routing logic
│   ├── search/
│   │   └── services.py          # Structured, review vector, photo hybrid search
│   ├── orchestration/
│   │   └── orchestrator.py      # Evidence merging, conflict resolution, LLM context
│   ├── rag/
│   │   └── rag_service.py       # LLM integration (OpenAI + mock backend)
│   └── ingestion/
│       └── pipelines.py         # Streaming (Kafka) + batch ETL pipelines
├── tests/
│   └── test_yelp_assistant.py   # Full test suite
└── docs/
    └── architecture.md          # Detailed architecture documentation
```

## Query Intents

| Intent      | Example Query                    | Data Sources Used               |
|-------------|----------------------------------|---------------------------------|
| OPERATIONAL | "Is it open right now?"          | Structured only                 |
| AMENITY     | "Do they have a heated patio?"   | Structured → Review + Photo     |
| QUALITY     | "Is it good for a date?"         | Review vector search            |
| PHOTO       | "Show me the outdoor seating"    | Hybrid photo retrieval          |

## Hybrid Freshness Strategy

| Data Type      | Velocity | Pipeline          | SLA        |
|----------------|----------|-------------------|------------|
| Reviews        | High     | Streaming (Kafka) | < 10 min   |
| Ratings        | High     | Streaming         | < 10 min   |
| Business hours | Medium   | Event-driven      | < 5 min    |
| Photos         | Medium   | Event-driven      | < 5 min    |
| Menus          | Low      | Weekly batch      | Weekly     |

## API

### `POST /assistant/query`

**Request:**
```json
{
  "query": "Does this place have a heated patio?",
  "business_id": "12345",
  "user_context": {
    "location": "NYC",
    "time": "2026-02-20T20:00:00"
  }
}
```

**Response:**
```json
{
  "answer": "Test Bistro — heated patio: Yes (canonical).",
  "confidence": 0.4,
  "intent": "amenity",
  "evidence": {
    "structured": true,
    "reviews_used": 0,
    "photos_used": 0
  },
  "latency_ms": 5.2
}
```

### `GET /health`

Returns service health status.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API server
python main.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The interactive API docs are available at http://localhost:8000/docs.

## Running Tests

```bash
cd yelp-ai-assistant
pytest tests/ -v
```

## Latency Budget (TDD §8.2)

| Component             | Target     |
|-----------------------|------------|
| Intent classification | < 20 ms    |
| Structured search     | < 40 ms    |
| Vector search         | < 80 ms    |
| Orchestration         | < 30 ms    |
| LLM                   | 300–800 ms |
| **Total**             | **< 1.2 s**|

## Conflict Resolution

When structured canonical data and reviews/photos disagree:

> "Officially listed as no heated patio. Some reviews mention outdoor heaters."

Structured data **always** wins. Reviews and photos provide supporting anecdotal evidence only.

## Rollout Phases

| Phase | Description                                         |
|-------|-----------------------------------------------------|
| 1     | Structured + Review RAG, basic intents              |
| 2     | Streaming freshness via CDC + Kafka                 |
| 3     | Multimodal retrieval with CLIP image embeddings     |
| 4     | Autoscaling, SLA dashboards, real-time monitoring   |

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is part of the python-ai-course repository and follows the same [LICENSE](../LICENSE).
