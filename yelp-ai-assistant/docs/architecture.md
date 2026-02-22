# Yelp-Style AI Assistant — Architecture

## Overview

This document supplements the Technical Design Document (TDD v1.0) with
implementation-level details.

---

## Component Map

```
src/models/schemas.py
  └── BusinessData, Review, Photo          ← structured + unstructured data models
  └── QueryRequest, QueryResponse           ← API contracts
  └── QueryIntent enum                      ← OPERATIONAL / AMENITY / QUALITY / PHOTO

src/intent/classifier.py
  └── IntentClassifier                      ← keyword pattern classifier (< 20 ms)

src/routing/router.py
  └── QueryRouter                           ← intent → service selection
  └── RoutingDecision                       ← which services to call
  └── RoutedResults                         ← aggregated raw search results

src/search/services.py
  └── StructuredSearchService               ← PostgreSQL / Elasticsearch structured index
  └── ReviewVectorSearchService             ← FAISS / Pinecone review embeddings
  └── PhotoHybridRetrievalService           ← caption keyword + image embedding hybrid

src/orchestration/orchestrator.py
  └── AnswerOrchestrator                    ← merge, conflict resolution, scoring
  └── EvidenceBundle                        ← ranked evidence for LLM

src/rag/rag_service.py
  └── RAGService                            ← LLM prompt construction + answer generation

src/ingestion/pipelines.py
  └── StreamingIngestionPipeline            ← Kafka CDC consumer (reviews, hours, photos)
  └── BatchIngestionPipeline                ← weekly ETL for static content (menus)
```

---

## Data Authority Rules

1. **Structured data is authoritative.**  
   PostgreSQL / Elasticsearch structured index fields (hours, address, amenities,
   price range, phone) override all other signals.

2. **Reviews are anecdotal.**  
   Reviews enrich quality and amenity answers but never overwrite canonical fields.

3. **Photos provide visual evidence.**  
   Retrieved via hybrid caption + image-embedding search; ranked by:
   `score = 0.5 * caption_score + 0.5 * image_similarity`

4. **Conflict rule.**  
   If structured data explicitly says `heated_patio: false` and a review
   mentions heated patio, the answer acknowledges both:
   > "Officially listed as no heated patio. Some reviews mention outdoor heaters."

---

## Scoring Formulas

### Photo hybrid score (TDD §6.2)
```
photo_score = 0.5 * caption_score + 0.5 * image_similarity
```

### Final evidence score (TDD §7)
```
final_score = 0.4 * structured_match + 0.3 * review_similarity + 0.3 * photo_similarity
```

---

## Freshness SLA

| Event Type     | SLA         |
|----------------|-------------|
| review.created | < 10 min    |
| review.updated | < 10 min    |
| rating.updated | < 10 min    |
| hours.changed  | < 5 min     |
| photo.uploaded | < 5 min     |
| menu.updated   | Weekly      |

---

## Failure Modes & Mitigations

| Failure               | Mitigation                          |
|-----------------------|-------------------------------------|
| Stale hours           | Real-time CDC → hot index           |
| Vector DB timeout     | Fallback to structured-only answer  |
| LLM timeout           | Return structured-only answer       |
| Conflicting evidence  | Structured data takes priority      |
| Missing business      | Return 404 / empty results message  |
