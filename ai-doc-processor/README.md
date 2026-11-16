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
├── android-app/                   # Standalone native Kotlin app (no backend)
│   ├── app/                       # Local PDF/text extraction, SQLite, local LLM
│   ├── gradlew                    # Pinned Gradle wrapper
│   └── tools/build.py             # Python build, test and device deployment CLI
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
| **Offline Android** | Native Kotlin + SQLite + MediaPipe | See below; no API server needed |
| **Desktop** | Electron | `cd ui/desktop && npm start` |

---

## Standalone native Android app

`android-app/` is separate from the Expo client: it does **not** call FastAPI,
OpenAI, Redis, PostgreSQL or any other server. It has no `INTERNET` permission.
Android 8.0 (API 26) or newer is required.

- Import UTF-8 text or text-based PDF files through Android's Storage Access
  Framework. The system picker includes device files and installed cloud
  document providers (such as Drive). Cloud providers may need a connection to
  retrieve a file; the app processes its contents locally and retains them in
  its private SQLite database, so subsequent use is offline.
- Extract text, produce a deterministic **extractive** summary, and store
  text chunks on the device. This is not the backend's OpenAI
  generative summary or vector-embedding pipeline.
- Browse, search, open and delete saved documents. Imports and inference run
  off the UI thread. No storage-account credentials or broad storage permission
  are needed.
- Ask a minimal **local LLM assistant** about the selected document after
  importing a compatible model. The assistant has no tools, executes no code,
  and sends no document data to a remote service.

### Local LLM setup

Model weights are not bundled or downloaded automatically. Obtain a trusted,
appropriately licensed **MediaPipe LLM Inference-compatible** `.task` or `.bin`
model, then use the app's model import control. A MediaPipe-converted Gemma
model is an example; generic GGUF files and arbitrary TensorFlow models are
not supported. Compatibility depends on the model, device architecture,
available RAM and inference backend; use a small model supported by MediaPipe
Tasks GenAI 0.10.24 and test it on your target device.

The imported model is copied into app-private storage; later questions work
without connectivity. You can replace or remove it. Without a model, document
import, search, persistence and extractive summaries still work. Questions use
a bounded excerpt of the selected document rather than the entire document.
Answers may be inaccurate: verify them against the original text. Document
instructions are treated as untrusted prompt content, but prompt grounding
cannot guarantee resistance to prompt injection or hallucinations.

### Build and deploy with Python

The requested Python automation is a **host-side Python script**, not
browser-based PyScript or a Python runtime inside the APK. Install Python
3.11+, JDK 17, and the Android SDK (platform 35, build tools and platform-tools).
Set `ANDROID_HOME` to the SDK directory. Gradle and Maven dependencies need a
connection for the first build; `--offline` works once they are cached.

```bash
python /home/runner/work/python-ai-course/python-ai-course/ai-doc-processor/android-app/tools/build.py build
python /home/runner/work/python-ai-course/python-ai-course/ai-doc-processor/android-app/tools/build.py --offline build

# Enable USB debugging and connect a device, or start an Android emulator.
python /home/runner/work/python-ai-course/python-ai-course/ai-doc-processor/android-app/tools/build.py install --serial DEVICE_SERIAL
```

`install` builds, installs and launches the debug APK with `adb`; omit `--serial`
when exactly one device is connected, or set `ANDROID_SERIAL`. Use
`install --no-build` to deploy an existing debug APK. The APK is written to
`android-app/app/build/outputs/apk/debug/app-debug.apk`.

`build --variant release` produces an **unsigned** release APK. Sign it with
your own protected release key (for example, Android Studio's Generate Signed
Bundle / APK workflow) before distribution. Do not commit signing keys,
passwords, models or private documents. This script does not publish to Play
Store or manage release-signing credentials.

### Native app testing

All commands below use the same Python CLI:

```bash
python /home/runner/work/python-ai-course/python-ai-course/ai-doc-processor/android-app/tools/build.py test --suite unit
python /home/runner/work/python-ai-course/python-ai-course/ai-doc-processor/android-app/tools/build.py test --suite lint
python /home/runner/work/python-ai-course/python-ai-course/ai-doc-processor/android-app/tools/build.py test --suite integration --serial DEVICE_SERIAL
python /home/runner/work/python-ai-course/python-ai-course/ai-doc-processor/android-app/tools/build.py test --suite e2e --serial DEVICE_SERIAL
python /home/runner/work/python-ai-course/python-ai-course/ai-doc-processor/android-app/tools/build.py test --suite bdd --serial DEVICE_SERIAL
python /home/runner/work/python-ai-course/python-ai-course/ai-doc-processor/android-app/tools/build.py test --suite load --serial DEVICE_SERIAL
python /home/runner/work/python-ai-course/python-ai-course/ai-doc-processor/android-app/tools/build.py test --suite smoke --serial DEVICE_SERIAL
python /home/runner/work/python-ai-course/python-ai-course/ai-doc-processor/android-app/tools/build.py test --suite all --serial DEVICE_SERIAL

# Python automation tests do not require an Android SDK or device.
python -m unittest discover -s /home/runner/work/python-ai-course/python-ai-course/ai-doc-processor/android-app/tools -p test_build.py -v
```

| Suite | Scope |
|---|---|
| Unit | Deterministic summary/chunking, input limits and assistant prompt/model-file handling |
| Integration | Real Android extraction and SQLite persistence/transactions |
| E2E | Native UI workflow, including file import and saved-document actions |
| BDD | Executable Given/When/Then `.feature` scenarios with isolated state; unknown steps fail |
| Load | Bounded repeated local processing/database workload, not HTTP/server traffic |
| Smoke | Application startup and offline configuration |

Device suites are Android instrumentation tests and need a connected device or
emulator; `all` includes host tests, Android lint and every instrumentation suite.
Use a dedicated test device/emulator: UI and BDD tests clear the app's document
library. Run missing-model scenarios on a fresh installation without a model.
The optional native inference integration test runs only if a compatible model
is already imported; it is skipped otherwise.
Gradle HTML/XML reports are under `android-app/app/build/reports/` and
`android-app/app/build/outputs/androidTest-results/`. BDD is a deliberately small
feature runner, not a complete Cucumber implementation.

Automated assistant tests cover deterministic boundaries and missing-model
behavior; they do not establish the accuracy or hardware compatibility of
third-party model weights. Before deployment, import your chosen model on a
physical device, enable airplane mode, import a local document, restart the
app, ask document-grounded questions, and exercise model replacement/removal.
Cloud import should also be checked against an installed provider with an
uncached file. Review response quality, memory use, latency and battery use on
the actual target device.

Development is split into scoped app and assistant implementation agents,
with host/device tests and an independent review before handoff. This workflow
does not give the in-app LLM autonomous access to storage or deployment tools.

Imports are limited to 10 MiB, 200 PDF pages and 500,000 extracted characters.
Scanned PDFs requiring OCR, encrypted PDFs, unsupported file types and invalid
UTF-8 are rejected rather than sent to a server. Model imports have a separate
2 GiB limit; leave enough space for both the existing and replacement model
during import. PDF scratch storage is capped at 64 MiB, but these limits are
not a total memory sandbox for PDF decoders or native model inference.

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
