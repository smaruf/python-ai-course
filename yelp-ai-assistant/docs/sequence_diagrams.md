# Sequence Diagrams

All major data flows in the Yelp-Style AI Assistant, annotated with
latency budgets from TDD §8.2.

---

## 1. Query Flow — Cache Hit (happy path, < 10 ms)

When the same query has been answered recently, the result is served
directly from Redis L1 cache with no downstream calls.

```mermaid
sequenceDiagram
    autonumber
    actor       User
    participant GW  as API Gateway
    participant QS  as Query Service (FastAPI)
    participant Cache as Redis Cache
    participant OBS as Observability

    User->>GW: POST /assistant/query
    GW->>QS: forward request + X-Correlation-ID
    QS->>Cache: GET qr:{business_id}:{query_hash}
    Cache-->>QS: HIT — cached QueryResponse (JSON)
    QS->>OBS: log(cache_hit, latency)
    QS-->>GW: 200 QueryResponse
    GW-->>User: 200 QueryResponse (< 10 ms)
```

---

## 2. Query Flow — Full Pipeline (cache miss, < 1.2 s)

The standard end-to-end path on a cache miss, with parallel search calls
and graceful fallback if the vector DB times out.

```mermaid
sequenceDiagram
    autonumber
    actor       User
    participant GW   as API Gateway
    participant QS   as Query Service (FastAPI)
    participant Cache as Redis Cache
    participant IC   as Intent Classifier
    participant QR   as Query Router
    participant SS   as Structured Search (PG/ES)
    participant RVS  as Review Vector Search (FAISS)
    participant PHS  as Photo Hybrid Search
    participant AO   as Answer Orchestrator
    participant LLM  as LLM / RAG Service
    participant OBS  as Observability

    User->>GW: POST /assistant/query
    GW->>QS: forward request + X-Correlation-ID

    QS->>Cache: GET qr:{business_id}:{query_hash}
    Cache-->>QS: MISS

    Note over IC: target < 20 ms
    QS->>IC: classify(query)
    IC-->>QS: (intent, confidence)

    QS->>QR: decide(intent)
    QR-->>QS: RoutingDecision

    Note over SS,PHS: parallel calls (asyncio.gather)
    par Structured search (≤ 40 ms)
        QS->>SS: search(query, business_id)
        SS-->>QS: StructuredSearchResult[]
    and Review vector search (≤ 80 ms)
        QS->>RVS: search(query, business_id)
        RVS-->>QS: ReviewSearchResult[]
    and Photo hybrid search (≤ 80 ms)
        QS->>PHS: search(query, business_id)
        PHS-->>QS: PhotoSearchResult[]
    end

    Note over AO: target ≤ 30 ms
    QS->>AO: orchestrate(RoutedResults)
    AO-->>QS: EvidenceBundle (conflict-resolved)

    Note over LLM: target 300–800 ms
    QS->>LLM: generate_answer(query, intent, bundle)
    LLM-->>QS: QueryResponse

    QS->>Cache: SET qr:{business_id}:{query_hash} TTL=300s
    QS->>OBS: log(intent, latency, evidence_sources)
    QS-->>GW: 200 QueryResponse
    GW-->>User: 200 QueryResponse (P95 < 1.2 s)
```

---

## 3. Query Flow — Vector DB Timeout Fallback

When the vector/LLM service exceeds its timeout, the system degrades
gracefully to a structured-data-only answer rather than returning an error.

```mermaid
sequenceDiagram
    autonumber
    actor       User
    participant QS   as Query Service
    participant CB   as Circuit Breaker
    participant SS   as Structured Search
    participant RVS  as Review Vector Search
    participant LLM  as LLM / RAG Service
    participant AO   as Answer Orchestrator

    User->>QS: POST /assistant/query
    QS->>SS: search(query, business_id)
    SS-->>QS: StructuredSearchResult[]

    QS->>CB: call(review_vector_search)
    CB->>RVS: search(query, business_id)
    Note over CB,RVS: timeout after 80 ms
    RVS--xCB: TimeoutError
    CB-->>QS: [] (empty — circuit OPEN)
    Note over CB: failure_count++; enter OPEN state

    QS->>AO: orchestrate(structured_only)
    AO-->>QS: EvidenceBundle (structured only)

    QS->>CB: call(llm_service)
    CB->>LLM: generate_answer(...)
    Note over CB,LLM: timeout after 1000 ms
    LLM--xCB: TimeoutError
    CB-->>QS: fallback answer

    Note over QS: return structured-only answer
    QS-->>User: 200 QueryResponse (structured fallback, low confidence)
```

---

## 4. Streaming Ingestion — Review CDC Pipeline

A new or updated review flows from the operational DB through Kafka into the
hot search indices within the 10-minute SLA.

```mermaid
sequenceDiagram
    autonumber
    participant ODB  as Operational DB (PostgreSQL)
    participant CDC  as CDC Connector (Debezium)
    participant KB   as Kafka (reviews topic)
    participant SP   as Stream Processor
    participant ES   as Elasticsearch (hot index)
    participant VDB  as Vector DB (FAISS/Pinecone)
    participant Cache as Redis Cache

    ODB->>CDC: WAL change event (INSERT/UPDATE reviews)
    CDC->>KB: publish IngestionEvent{review.created}
    Note over KB: partition by business_id

    KB->>SP: consume event (< 1 s delivery)
    SP->>SP: validate & enrich payload
    SP->>SP: compute review embedding (sentence-transformer)

    par Index review text
        SP->>ES: upsert review doc (reviews_text index)
    and Store embedding
        SP->>VDB: upsert vector(review_id, embedding)
    end

    SP->>Cache: DEL qr:{business_id}:*  (invalidate stale cached answers)

    Note over SP: SLA target < 10 min end-to-end
```

---

## 5. Streaming Ingestion — Business Hours Change

An hours update must propagate to the hot index within 5 minutes.

```mermaid
sequenceDiagram
    autonumber
    participant BO   as Business Owner Portal
    participant ODB  as PostgreSQL (businesses / business_hours)
    participant CDC  as CDC Connector
    participant KB   as Kafka (business-changes topic)
    participant SP   as Stream Processor
    participant ES   as Elasticsearch (businesses_structured)
    participant Cache as Redis Cache

    BO->>ODB: UPDATE business_hours SET open_time=...
    ODB->>CDC: WAL change event
    CDC->>KB: publish IngestionEvent{hours.changed}

    KB->>SP: consume event
    SP->>ES: update nested hours[] field in business doc
    SP->>Cache: DEL hours:{business_id}
    SP->>Cache: DEL qr:{business_id}:*

    Note over SP: SLA target < 5 min end-to-end
```

---

## 6. Batch Ingestion — Weekly Menu ETL

Low-velocity static content processed on a weekly schedule.

```mermaid
sequenceDiagram
    autonumber
    participant SCH  as Scheduler (cron)
    participant ETL  as Batch ETL Job
    participant S3   as Object Storage (S3)
    participant ES   as Elasticsearch (cold index)
    participant VDB  as Vector DB

    SCH->>ETL: trigger weekly run
    ETL->>S3: list new/updated menu PDFs
    S3-->>ETL: object keys[]

    loop for each menu object
        ETL->>S3: download PDF
        ETL->>ETL: extract text (PDF parser)
        ETL->>ETL: chunk text into passages
        ETL->>ETL: compute passage embeddings
        ETL->>ES: bulk index passages
        ETL->>VDB: upsert passage embeddings
    end

    ETL->>ETL: log batch summary (records_in, records_processed, errors)
```

---

## 7. Photo Upload — Multimodal Indexing Pipeline

A photo upload triggers caption extraction, CLIP encoding, and dual indexing.

```mermaid
sequenceDiagram
    autonumber
    participant Client as Client (mobile/web)
    participant API  as Upload API
    participant S3   as Object Storage
    participant CE   as Caption Extractor (LLM)
    participant CLIP as Vision Encoder (CLIP)
    participant ES   as Elasticsearch (caption index)
    participant VDB  as Vector DB (image embeddings)

    Client->>API: POST /photos/upload {file, business_id}
    API->>S3: store raw image → photo_id
    S3-->>API: object_key

    API->>CE: extract_caption(image_url)
    CE-->>API: caption_text

    par Encode text
        API->>CE: embed(caption_text) → caption_embedding
    and Encode image
        API->>CLIP: encode(image) → image_embedding (512-d)
    end

    par Index caption
        API->>ES: index{photo_id, business_id, caption_text, caption_embedding}
    and Index image
        API->>VDB: upsert{photo_id, image_embedding}
    end

    API-->>Client: 201 {photo_id, url}
```

---

## 8. Cache Warm-up on Service Start

At startup (or after a deploy), the service pre-warms caches for the most
popular businesses to absorb the initial request spike.

```mermaid
sequenceDiagram
    autonumber
    participant SVC  as Query Service (startup)
    participant PG   as PostgreSQL
    participant ES   as Elasticsearch
    participant Cache as Redis Cache

    Note over SVC: lifespan startup hook
    SVC->>PG: SELECT business_id FROM businesses ORDER BY review_count DESC LIMIT 500
    PG-->>SVC: top_500_business_ids[]

    loop for each popular business
        SVC->>PG: fetch structured data + hours
        SVC->>Cache: SET hours:{business_id} TTL=300s
    end

    Note over SVC: cache warm-up complete; ready to serve
```
