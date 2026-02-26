# AI Gateway — Cloud/Local LLM Failover

A production-ready AI gateway microservice that:

- **Prefers cloud LLMs** (OpenAI by default) when internet is available
- **Automatically falls back** to a local [Ollama](https://ollama.com) model when the cloud is unreachable
- Implements a **circuit-breaker pattern** — after N consecutive cloud failures the gateway
  routes all traffic to the local model and re-probes the cloud after a configurable timeout

```
            ┌─────────────────────┐
            │     Your App        │
            └─────────┬───────────┘
                      │ POST /ai/query
              AI Gateway Layer
                      │
        ┌─────────────┴─────────────┐
        │                           │
   🌐 Cloud LLM                💻 Local LLM
 (Primary)                     (Fallback)
 OpenAI, etc.                  Ollama llama3
```

## 📁 Project Structure

```
ai-gateway/
├── cloud_client.py     # Cloud LLM client (OpenAI)
├── local_client.py     # Local LLM client (Ollama)
├── router.py           # Circuit-breaker router
├── ai_gateway.py       # FastAPI REST service
├── Dockerfile          # Container image
├── docker-compose.yml  # Gateway + Ollama stack
├── requirements.txt    # Python dependencies
├── .vscode/
│   └── settings.json   # VS Code + Copilot settings
└── tests/
    └── test_gateway.py # Unit & integration tests
```

## 🚀 Quick Start

### Option 1 — Run locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your OpenAI key (optional — gateway falls back to local if missing)
export OPENAI_API_KEY="sk-..."

# 3. Start local Ollama (in another terminal)
curl -fsSL https://ollama.com/install.sh | sh
ollama run llama3

# 4. Start the gateway
uvicorn ai_gateway:app --reload
```

### Option 2 — Docker Compose (recommended)

```bash
# Starts both Ollama and the gateway
OPENAI_API_KEY=sk-... docker compose up
```

The gateway is then available at `http://localhost:8000`.

## 🔌 API Reference

### `POST /ai/query`

```json
{
  "prompt": "What is the capital of France?"
}
```

Response:

```json
{
  "response": "The capital of France is Paris.",
  "backend": "cloud",
  "state": "closed"
}
```

| Field     | Description                                    |
|-----------|------------------------------------------------|
| `response`| The AI model's answer                          |
| `backend` | `"cloud"` or `"local"` — which backend replied |
| `state`   | Circuit-breaker state: `closed / open / half_open` |

### `GET /health`

Returns availability of each backend and current circuit state.

### `POST /admin/reset`

Manually reset the circuit breaker to `closed` (cloud-preferred) state.

## ⚙️ Configuration (environment variables)

| Variable            | Default                   | Description                              |
|---------------------|---------------------------|------------------------------------------|
| `CLOUD_PROVIDER`    | `openai`                  | Cloud LLM provider                       |
| `CLOUD_MODEL`       | `gpt-4o-mini`             | Cloud model name                         |
| `OPENAI_API_KEY`    | *(required for cloud)*    | OpenAI API key                           |
| `LOCAL_MODEL`       | `llama3`                  | Ollama model name                        |
| `OLLAMA_BASE_URL`   | `http://localhost:11434`  | Ollama service URL                       |
| `FAILURE_THRESHOLD` | `3`                       | Cloud failures before opening circuit    |
| `RECOVERY_TIMEOUT`  | `300`                     | Seconds before re-probing cloud          |

## 🔄 Circuit Breaker State Machine

```
CLOSED ──(3 failures)──► OPEN ──(5 min)──► HALF-OPEN
  ▲                                              │
  └──────────────(success)──────────────────────┘
```

| State       | Behaviour                                     |
|-------------|-----------------------------------------------|
| `closed`    | Normal — cloud is used, failures are counted  |
| `open`      | Cloud down — all requests go to local LLM     |
| `half_open` | Trial request sent to cloud to test recovery  |

## 💻 VS Code + GitHub Copilot

Open this folder in VS Code:

```bash
code ai-gateway/
```

The `.vscode/settings.json` file pre-configures:
- Python test discovery (pytest)
- Copilot inline suggestions enabled
- Correct Python path for module imports

Copilot will auto-complete based on the patterns in `router.py` and `ai_gateway.py`.

## 🧪 Running Tests

```bash
cd ai-gateway
pytest tests/ -v
```

## 🏗 Hardware Recommendations for Local Models

| RAM      | Suggested model |
|----------|-----------------|
| 8 GB     | `phi3` (3B)     |
| 16 GB    | `llama3` (7B)   |
| 32 GB    | `llama3:13b`    |
| GPU 8 GB+| Any — much faster |

## ⚖️ Cloud vs Local Trade-offs

| Feature            | Cloud          | Local            |
|--------------------|----------------|------------------|
| Accuracy           | ⭐⭐⭐⭐⭐          | ⭐⭐⭐              |
| Internet required  | Yes            | No               |
| Cost               | API-based      | Hardware-based   |
| Latency            | Network RTT    | < 1 s (local)    |
| Privacy            | External       | Fully private    |
