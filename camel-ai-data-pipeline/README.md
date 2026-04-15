# 🚀 Intelligent Data Pipeline with Apache Camel + AI

> **Part of [Python AI Course](../README.md)** - A comprehensive learning repository covering AI, algorithms, and real-world applications.  
> See also: [AI Development Project](../ai-development-project/) | [AI Gateway](../ai-gateway/) | [Fintech Tools](../fintech-tools/) | [NASDAQ CSE](../nasdaq-cse/)

A **progressive, end-to-end data engineering system** built using Apache Camel, modern AI models, and streaming technologies. It evolves from basic routing to a fully intelligent, scalable data platform capable of real-time enrichment, classification, and decision-making.

The system simulates real-world use cases such as **market data processing, news sentiment analysis, and anomaly detection**, making it suitable for financial systems, analytics platforms, and enterprise integrations.

---

## 📚 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Levels](#-levels-at-a-glance)
- [Quick Start](#-quick-start)
- [Tech Stack](#-tech-stack)
- [Learning Path](#-learning-path)
- [Load Tests & CI/CD](#-load-tests--cicd)

---

## 🔹 Overview

| Attribute | Details |
|-----------|---------|
| **Primary Language** | Java (Spring Boot) |
| **Integration Framework** | Apache Camel |
| **AI Layer** | OpenAI API / Local LLM (Ollama) |
| **Streaming** | Apache Kafka |
| **Storage** | PostgreSQL / MongoDB / Vector DB |
| **Deployment** | Docker / Kubernetes / Camel K |
| **Difficulty Range** | Zero → Expert (10 levels) |

---

## 🏗 Architecture

```
Sources (API / Files / Kafka)
        ↓
   Apache Camel
   (Routing & Transformation)
        ↓
Data Processing Layer
   (Validation / Enrichment / Schema)
        ↓
AI / ML Layer
   (Classification / Summarization / Embeddings)
        ↓
Streaming / Storage
   (Kafka / PostgreSQL / MongoDB / Vector DB)
        ↓
Visualization / APIs
   (Prometheus / Grafana / REST)
```

See [docs/architecture.md](./docs/architecture.md) for full diagrams and component details.

---

## 🧩 Levels at a Glance

| Level | Name | Focus | Key Tech |
|-------|------|-------|----------|
| [**0**](./level-0-fundamentals/) | Fundamentals | Camel basics, simple routing | Camel Core, Spring Boot |
| [**1**](./level-1-data-engineering/) | Data Engineering Basics | Structured pipelines, DB storage | Camel, REST APIs, PostgreSQL |
| [**2**](./level-2-streaming/) | Streaming & Real-Time | Event-driven, Kafka pipelines | Apache Kafka, Camel Kafka |
| [**3**](./level-3-ai-integration/) | AI Integration | LLM processing, text classification | OpenAI API, Custom Processors |
| [**4**](./level-4-intelligent-routing/) | Intelligent Routing | AI-driven decisions, enrichment | Camel Choice, AI Routing |
| [**5**](./level-5-advanced-engineering/) | Advanced Engineering | Schema evolution, monitoring | Prometheus, Grafana, Schema Registry |
| [**6**](./level-6-vector-semantic/) | Vector & Semantic Layer | Embeddings, RAG pipelines | Pinecone / FAISS, Embedding APIs |
| [**7**](./level-7-domain-finance/) | Domain Intelligence (Finance) | Market data, anomaly detection | FAST/FIX simulation, AI models |
| [**8**](./level-8-distributed-platform/) | Distributed AI Platform | Microservices, cloud-ready | Kubernetes, Docker, Camel K |
| [**9**](./level-9-realtime-ai/) | Real-Time AI Decision System | Autonomous agents, feedback loops | Event-driven AI, Dashboards |

---

## 🚀 Quick Start

### Prerequisites

```bash
Java 17+
Maven 3.8+
Docker & Docker Compose
Apache Kafka (or use Docker Compose)
```

### Run Level 0 (Simplest)

```bash
cd level-0-fundamentals
mvn spring-boot:run
```

### Run with Docker Compose (Level 2+)

```bash
cd level-2-streaming
docker-compose up -d
mvn spring-boot:run
```

### Set AI API Key (Level 3+)

```bash
export OPENAI_API_KEY="your-key-here"
# OR use local Ollama:
ollama pull llama3.1:8b && ollama serve
```

---

## 🛠 Tech Stack

| Category | Technologies |
|----------|-------------|
| **Core** | Java 17, Spring Boot 3.x, Apache Camel 4.x |
| **Messaging** | Apache Kafka, Camel Kafka Component |
| **AI/LLM** | OpenAI API, Ollama (local), LangChain4j |
| **Databases** | PostgreSQL, MongoDB, Redis |
| **Vector DBs** | Pinecone, Weaviate, FAISS |
| **Monitoring** | Prometheus, Grafana, Micrometer |
| **Infrastructure** | Docker, Kubernetes, Camel K |
| **Schema** | Confluent Schema Registry, Avro |

---

## 📖 Learning Path

### 🟢 Beginner (Levels 0–1)
Start here if you are new to Apache Camel or integration frameworks.
- [Level 0 — Fundamentals](./level-0-fundamentals/)
- [Level 1 — Data Engineering Basics](./level-1-data-engineering/)

### 🟡 Intermediate (Levels 2–4)
For developers comfortable with Java/Spring who want streaming and AI.
- [Level 2 — Streaming & Real-Time](./level-2-streaming/)
- [Level 3 — AI Integration](./level-3-ai-integration/)
- [Level 4 — Intelligent Routing](./level-4-intelligent-routing/)

### 🔴 Advanced (Levels 5–7)
Production-grade patterns and domain-specific intelligence.
- [Level 5 — Advanced Data Engineering](./level-5-advanced-engineering/)
- [Level 6 — Vector & Semantic Layer](./level-6-vector-semantic/)
- [Level 7 — Domain Intelligence (Finance)](./level-7-domain-finance/)

### 🏆 Expert (Levels 8–9)
Cloud-scale distributed systems and autonomous AI agents.
- [Level 8 — Distributed AI Platform](./level-8-distributed-platform/)
- [Level 9 — Real-Time AI Decision System](./level-9-realtime-ai/)

---

## 💡 Key Highlights

- End-to-end **data engineering + AI integration**
- Real-time **and** batch processing
- Production-grade architecture patterns
- Domain-focused (finance, trading systems)
- Scalable from beginner to enterprise level
- Combines **integration + AI + streaming** (rare combo)

---

## 🧪 Load Tests & CI/CD

### Load Tests (Locust)

Python-based load test suite targeting each level's REST and Kafka endpoints:

```bash
cd load-tests
pip install -r requirements.txt
locust -f locustfile.py --host http://localhost:8080
```

See [load-tests/README.md](./load-tests/README.md) for full usage, including headless CI mode and the result analysis tool.

### Result Analysis

```bash
python load-tests/analysis/analyze_results.py --csv-prefix results/load_test
```

Generates a console summary, `analysis_report.md`, and `analysis_report.html` with per-endpoint SLO badges (P95 < 2 s, error rate < 1 %).

### CI/CD Pipeline

The [`.github/workflows/camel-pipeline-ci.yml`](../.github/workflows/camel-pipeline-ci.yml) workflow runs automatically on every push or pull request touching `camel-ai-data-pipeline/`:

| Job | Description |
|-----|-------------|
| **build-java** | Builds Level 0 & 1 Maven modules, uploads JARs |
| **test-load-tests** | Lints Python code (`flake8`) and runs 16 unit tests for the analyser |
| **load-test** | Spins up a Flask stub server, runs Locust (10 users, 60 s), analyses results, uploads HTML/CSV artifacts |
| **docs-check** | Verifies all internal README cross-links resolve |

---

## 📄 License

See the [LICENSE](../LICENSE) file for details.
