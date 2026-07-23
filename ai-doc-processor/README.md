# AI Document Processor

An AI-powered Micro-SaaS that processes documents through an ETL pipeline and streams LLM-generated summaries. Built with **FastAPI**, **LangChain**, **PGVector**, **Redis/Celery**, and a **multi-platform UI** targeting web, mobile, and desktop.

---

## Project Structure

```
ai-doc-processor/
├── .github/workflows/deploy.yml   # CI/CD: lint, test, build, push Docker image
├── app/                           # Backend — FastAPI
│   ├── main.py                    # App entry point + CORS
│   ├── api/
│   │   ├── documents.py           # Upload & SSE streaming endpoints
│   │   └── webhooks.py            # Lemon Squeezy payment webhooks
│   ├── core/config.py             # Pydantic settings (env vars)
│   ├── etl/
│   │   ├── extract.py             # PDF / text parsing (pypdf)
│   │   ├── transform.py           # LangChain chunking + OpenAI embeddings/streaming
│   │   └── load.py                # PGVector insertion
│   ├── workers/celery_app.py      # Celery task — async ETL queue (Redis)
│   └── db/models.py               # SQLAlchemy models (User, Document, DocumentChunk)
├── ui/
│   ├── streamlit/dashboard.py     # 🟢 MVP dashboard — zero JS, streaming SSE
│   ├── web/                       # 🌐 Next.js 14 web app (TypeScript)
│   │   ├── pages/index.tsx
│   │   └── components/DocumentUploader.tsx
│   ├── mobile/                    # 📱 React Native (Expo) — iOS + Android + Web
│   │   ├── App.tsx
│   │   └── screens/HomeScreen.tsx
│   └── desktop/                   # 🖥️  Electron — wraps the Next.js web UI
│       └── main.js
├── tests/
│   ├── test_etl.py
│   └── test_api.py
├── infra/
│   ├── docker-compose.yml         # Local dev: Postgres+PGVector, Redis, API, Worker, Streamlit
│   └── terraform/main.tf          # AWS S3 + RDS + ElastiCache (IaC)
├── qa_dashboard/index.html        # PyScript in-browser QA tool
├── locustfile.py                  # Load testing (Locust)
├── pyproject.toml                 # Python deps (hatch / uv / pip)
└── Dockerfile                     # Multi-stage production build
```

---

## UI Platforms

| Platform | Tech | Start command |
|---|---|---|
| **MVP Dashboard** | Streamlit | `streamlit run ui/streamlit/dashboard.py` |
| **Web** | Next.js 14 + TypeScript | `cd ui/web && npm run dev` |
| **Mobile** | React Native (Expo) | `cd ui/mobile && npx expo start` |
| **Desktop** | Electron | `cd ui/desktop && npm start` |

---

## Quick Start (Local)

### 1. Start infrastructure
```bash
cd infra && docker compose up -d
```

### 2. Configure environment
```bash
cp .env.example .env
# Fill in: OPENAI_API_KEY, DATABASE_URL, REDIS_URL, etc.
```

### 3. Run the API
```bash
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

### 4. Run the Celery worker
```bash
celery -A app.workers.celery_app worker --loglevel=info
```

### 5. Choose your UI

```bash
# Streamlit MVP
streamlit run ui/streamlit/dashboard.py

# Next.js web
cd ui/web && npm install && npm run dev

# React Native (Expo)
cd ui/mobile && npm install && npx expo start

# Electron desktop (requires web running on :3000)
cd ui/desktop && npm install && npm start
```

---

## Testing

```bash
pytest                        # Unit + integration tests
ruff check app/ tests/        # Lint
locust -f locustfile.py --host=http://localhost:8000   # Load test
```

---

## Deployment

See `infra/terraform/` for AWS resources and `.github/workflows/deploy.yml` for the GitHub Actions CI/CD pipeline that builds and pushes to GitHub Container Registry on every merge to `main`.
