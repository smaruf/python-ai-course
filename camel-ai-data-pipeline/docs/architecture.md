# Architecture — Intelligent Data Pipeline with Apache Camel + AI

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                             │
│  REST APIs │ CSV/Files │ Kafka Topics │ Market Feeds (FIX/ITCH) │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     APACHE CAMEL LAYER                          │
│                                                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐               │
│  │  Routing   │  │ Transform  │  │  Filter    │               │
│  │  (Choice)  │  │(JSON/Avro) │  │ (Predicate)│               │
│  └────────────┘  └────────────┘  └────────────┘               │
│                                                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐               │
│  │  Splitter  │  │ Aggregator │  │ Dead-Letter│               │
│  │  (EIP)     │  │  (EIP)     │  │  Queue     │               │
│  └────────────┘  └────────────┘  └────────────┘               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  DATA PROCESSING LAYER                          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Validation  │  │  Schema      │  │  Idempotent  │         │
│  │  (Bean)      │  │  Evolution   │  │  Consumer    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI / ML LAYER                              │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  LLM         │  │  Embedding   │  │  Anomaly     │         │
│  │  Processor   │  │  Generator   │  │  Detector    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │  Sentiment   │  │  RAG Engine  │                            │
│  │  Classifier  │  │  (Vector DB) │                            │
│  └──────────────┘  └──────────────┘                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  STREAMING / STORAGE LAYER                      │
│                                                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │   Kafka    │  │ PostgreSQL │  │  MongoDB   │  │ VectorDB │ │
│  │  (Topics)  │  │ (Relational│  │ (Document) │  │(Pinecone)│ │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘ │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                VISUALIZATION / APIS LAYER                       │
│                                                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐               │
│  │ Prometheus │  │  Grafana   │  │ REST APIs  │               │
│  │ (Metrics)  │  │(Dashboards)│  │(Spring MVC)│               │
│  └────────────┘  └────────────┘  └────────────┘               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Descriptions

### Apache Camel Layer
Apache Camel is the integration backbone. It provides:
- **Routes**: Define the flow of messages from source to destination
- **Enterprise Integration Patterns (EIPs)**: Splitter, Aggregator, Filter, Choice
- **Components**: 300+ connectors (Kafka, HTTP, File, DB, etc.)
- **Dead-Letter Channel**: Error handling with retry policies

### Data Processing Layer
- **Validation**: Schema and business rule validation using Camel Beans
- **Schema Evolution**: Avro with Schema Registry for backward/forward compatibility
- **Idempotent Consumer**: Prevent duplicate processing using message IDs

### AI / ML Layer
- **LLM Processor**: Calls OpenAI or local Ollama for text processing
- **Embedding Generator**: Converts text to vector representations
- **Sentiment Classifier**: Classifies market news as bullish/bearish/neutral
- **Anomaly Detector**: Identifies outliers in financial data streams
- **RAG Engine**: Retrieval-Augmented Generation for context-aware responses

### Streaming / Storage Layer
- **Kafka**: Event streaming backbone with partitioned topics
- **PostgreSQL**: Structured data persistence
- **MongoDB**: Document storage for enriched records
- **Vector DB**: Semantic search and similarity queries

---

## Message Flow Example (Level 4)

```
Market News API
    │
    ▼ (Camel HTTP Consumer)
Raw News Message
    │
    ▼ (JSON Transformer)
Structured NewsEvent { title, body, source, timestamp }
    │
    ▼ (AI Sentiment Processor)
Enriched NewsEvent { ..., sentiment: "positive", confidence: 0.87, tags: ["earnings", "growth"] }
    │
    ▼ (Camel Choice Router)
    ├── sentiment == "positive" ──► Kafka topic: market.news.bullish
    ├── sentiment == "negative" ──► Kafka topic: market.news.bearish
    └── sentiment == "neutral"  ──► Kafka topic: market.news.neutral
```

---

## Deployment Architecture (Level 8+)

```
┌──────────────────────────────────────────────────────┐
│                   Kubernetes Cluster                  │
│                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  Camel K    │  │  Camel K    │  │  Camel K    │ │
│  │  Route Pod  │  │  Route Pod  │  │  Route Pod  │ │
│  │ (Ingestor)  │  │(AI Enricher)│  │ (Publisher) │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
│         │                │                │         │
│         └────────────────┼────────────────┘         │
│                          │                          │
│                   ┌──────▼──────┐                   │
│                   │Apache Kafka │                   │
│                   │  (Strimzi)  │                   │
│                   └─────────────┘                   │
└──────────────────────────────────────────────────────┘
```

---

## Key Design Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Integration Framework | Apache Camel | 300+ connectors, EIP patterns, battle-tested |
| AI Provider | OpenAI + Ollama fallback | Cloud power with local fallback |
| Streaming | Apache Kafka | Industry standard, scalable, durable |
| Schema Management | Avro + Schema Registry | Type safety, backward compatibility |
| Deployment | Camel K on Kubernetes | Cloud-native, serverless Camel routes |
| Monitoring | Prometheus + Grafana | Industry standard observability stack |
