Here is a **detailed, actionable implementation plan** for your first project: the **AI Document Processor**. 

This plan integrates **ETL pipelines** and **streaming** while maintaining the "low effort, high value" Micro-SaaS philosophy. It leverages your Python skills, Redis/PubSub interests, and clean code principles, designed for gradual implementation.

---

### **Phase 1: Architecture & Tech Stack (ETL + Streaming)**

To keep DevOps low but architecture robust, we will use a **decoupled ETL pipeline** with **real-time streaming** for the user experience.

| Component | Technology Choice | Why? |
| :--- | :--- | :--- |
| **Frontend (MVP)** | Streamlit or Gradio | Zero UI coding, native support for file uploads and streaming text. |
| **API Gateway** | Python + FastAPI | High performance, native `StreamingResponse` for SSE (Server-Sent Events). |
| **ETL Queue** | **Redis Streams** or Celery + Redis | Decouples heavy document parsing from the API. Simpler than Kafka for V1, but uses the Redis skill you want to apply. |
| **Extract** | `unstructured` or `pypdf` | Reliable open-source PDF/text extraction. |
| **Transform** | LangChain + OpenAI API | Chunking, embedding, and LLM summarization/extraction. |
| **Load** | PostgreSQL + **PGVector** | Single database for user metadata, billing, *and* vector embeddings (simplifies DevOps vs. managing a separate Pinecone/Milvus). |
| **Payments** | Lemon Squeezy | Merchant of Record (handles global VAT/taxes for Bangladesh/Poland automatically). |

---

### **Phase 2: Clean Code Project Structure**

Initialize this structure in your WSL environment. It enforces separation of concerns.

```text
ai-doc-processor/
├── .github/workflows/       # CI/CD (lint, test, build)
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── api/                 # Route handlers
│   │   ├── documents.py     # Upload & streaming endpoints
│   │   └── webhooks.py      # Lemon Squeezy payment webhooks
│   ├── core/                # Config, security, logging
│   │   └── config.py        # Pydantic settings (env vars)
│   ├── etl/                 # ETL Pipeline Logic
│   │   ├── extract.py       # PDF parsing
│   │   ├── transform.py     # LangChain RAG/LLM logic
│   │   └── load.py          # PGVector insertion
│   ├── workers/             # Background tasks
│   │   └── celery_app.py    # Redis queue consumer
│   └── db/                  # Database models & sessions
│       └── models.py        # SQLAlchemy models
├── tests/                   # Pytest suite
│   ├── test_etl.py
│   └── test_api.py
├── infra/                   # IaC
│   ├── terraform/           # AWS S3 + RDS provisioning
│   └── docker-compose.yml   # Local WSL dev environment
├── qa_dashboard/            # PyScript Testing UI
│   └── index.html
├── locustfile.py            # Load testing script
├── pyproject.toml           # Modern Python dependency management
└── Dockerfile               # Multi-stage production build
```

---

### **Phase 3: Step-by-Step Implementation Guide**

#### **Step 3.1: Local Development Setup (WSL + Docker)**
1. Create `infra/docker-compose.yml` with PostgreSQL (with `pgvector` extension) and Redis.
2. Run `docker compose up -d` in WSL.
3. Use `pyproject.toml` with `uv` or `poetry` to manage dependencies (`fastapi`, `uvicorn`, `langchain`, `openai`, `celery`, `redis`, `sqlalchemy`, `psycopg2`).

#### **Step 3.2: Build the ETL Pipeline (`app/etl/`)**
*   **Extract**: Read uploaded file. Handle errors (corrupt PDFs).
*   **Transform**: Split text into chunks (e.g., 500 tokens). Call OpenAI API to extract specific fields or summarize.
*   **Load**: Save metadata (user_id, filename, status) to PostgreSQL. Save embeddings to the `pgvector` column.
*   *Implementation Tip*: Wrap this in a Celery task (`@celery_app.task`) so the API can return a `task_id` immediately, preventing HTTP timeouts on large files.

#### **Step 3.3: Implement Streaming API (`app/api/documents.py`)**
Instead of making the user wait for the whole ETL process, stream the LLM's output token-by-token using FastAPI's `StreamingResponse` and Server-Sent Events (SSE).

```python
# Simplified conceptual example
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.post("/process-stream")
async def process_document_stream(file: UploadFile, prompt: str):
    async def event_generator():
        yield "data: {\"status\": \"extracting\"}\n\n"
        # ... trigger ETL task ...
        yield "data: {\"status\": \"transforming\"}\n\n"
        # ... stream LLM tokens here ...
        for token in llm_stream:
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: {\"status\": \"complete\"}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```
*Note: Streamlit has native `st.write_stream()` which consumes this SSE endpoint perfectly.*

#### **Step 3.4: Payment Integration**
1. Create a Lemon Squeezy product (e.g., "Pro Plan - $29/mo").
2. In `app/api/webhooks.py`, create an endpoint to verify Lemon Squeezy signatures.
3. On `subscription_created` event, update the user's `subscription_status = 'active'` in PostgreSQL.

---

### **Phase 4: Testing Strategy (Locust + PyScript)**

#### **1. Load Testing with Locust (`locustfile.py`)**
Simulate concurrent users uploading documents and hitting the streaming endpoint to ensure Redis/DB don't bottleneck.
```python
from locust import HttpUser, task, between

class DocumentUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def upload_and_stream(self):
        files = {'file': ('test.pdf', open('test.pdf', 'rb'), 'application/pdf')}
        with self.client.post("/process-stream", files=files, catch_response=True) as response:
            if response.status_code == 200:
                # Verify SSE stream starts correctly
                if "text/event-stream" in response.headers.get("content-type", ""):
                    response.success()
                else:
                    response.failure("Not an SSE stream")
```
Run via: `locust -f locustfile.py --host=http://localhost:8000`

#### **2. PyScript QA Dashboard (`qa_dashboard/index.html`)**
Create a zero-install browser tool for you or your QA to test the API without Postman.
```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://pyscript.net/releases/2023.11.1/core.css" />
    <script type="module" src="https://pyscript.net/releases/2023.11.1/core.js"></script>
</head>
<body>
    <h2>Micro-SaaS API QA Dashboard</h2>
    <button id="test-health">Test Health</button>
    <pre id="output"></pre>

    <py-script>
        import asyncio
        from pyscript import document

        async def test_health(event):
            document.getElementById("output").innerText = "Testing..."
            # Simulate API call
            res = await pyfetch("http://localhost:8000/health")
            data = await res.json()
            document.getElementById("output").innerText = str(data)

        Element("test-health").element.addEventListener("click", asyncio.create_task(test_health))
    </py-script>
</body>
</html>
```
*Open this HTML file directly in Chrome/Edge. It runs Python in the browser to hit your local FastAPI backend.*

---

### **Phase 5: Deployment & IaC**

#### **1. Infrastructure as Code (Terraform)**
Keep it minimal. Use Terraform only for stateful resources (Database, Storage). Let the app host handle the compute.
*   **Provider**: AWS (or GCP).
*   **Resources**: 
    *   `aws_s3_bucket` (for raw document storage before processing).
    *   `aws_db_instance` (PostgreSQL with `pgvector` support, or use AWS Aurora Serverless v2).
    *   `aws_elasticache_cluster` (Redis for Celery queue).

#### **2. CI/CD Pipeline (GitHub Actions)**
Create `.github/workflows/deploy.yml`:
1. **Lint & Test**: Run `ruff check` and `pytest`.
2. **Build**: `docker build -t ghcr.io/smaruf/ai-doc-processor:${{ github.sha }} .`
3. **Push**: Push to GitHub Container Registry.
4. **Deploy**: Trigger a webhook to **Render** or **Fly.io** to pull the new image and restart the service with zero downtime.

#### **3. App Deployment (Render/Fly.io)**
*   **Fly.io**: Excellent for global low-latency. Use `fly launch` to generate a `fly.toml`. It natively supports attaching a PostgreSQL volume and a Redis instance.
*   **Render**: Simpler UI. Connect GitHub repo, set build command (`pip install -r requirements.txt`), and start command (`uvicorn app.main:app --host 0.0.0.0 --port 8000`).

---

### **Phase 6: Marketing & Monetization Execution**

Since you prefer "less coding, more direction/consulting," your marketing should position you as an expert, not just a tool seller.

1. **The "Build in Public" Hook (LinkedIn)**:
   * *Post Idea*: "I built an AI document processor that cuts compliance review time by 70%. Instead of a massive enterprise suite, I used FastAPI + LangChain + PGVector. Here’s the 3-step ETL architecture I used (thread) 🧵"
   * This attracts both potential B2B buyers and consulting leads.
2. **Niche Targeting (Leverage Fintech)**:
   * Don't market to "everyone." Market to: *Freelance Accountants, Small Law Firms, or Fintech Startups*.
   * Offer a "Done-For-You" setup: "Buy the $99/mo SaaS, or pay me $1,500 to deploy a custom, private version of this on your AWS account." (This fulfills your consulting goal).
3. **Product Hunt Launch**:
   * Prepare a 45-second Loom video showing: Upload PDF → Watch streaming extraction → Download clean JSON/Summary.
   * Offer an exclusive "Founder's Deal": Lifetime 50% off for the first 50 buyers.

---

### **Your Immediate Next Actions (Week 1)**

1. **Initialize Repo**: Create the folder structure above in your WSL environment.
2. **Dockerize Dev**: Get `docker-compose.yml` running with Postgres+PGVector and Redis.
3. **Build the ETL Core**: Write `app/etl/extract.py` and `transform.py` to successfully read a sample PDF and print an LLM summary to your console.
4. **Reply to me** with: *"I have the local Docker env running. Let's write the FastAPI streaming endpoint and the Celery worker code."* (Or ask for the Terraform snippet first, depending on your preference).
