# AI Gateway — 3-Tier AI Failover (Copilot → Cloud → Local)

A production-ready AI gateway microservice that routes queries through a **3-tier failover chain**:

| Priority | Tier        | Backend               | When used                            |
|----------|-------------|-----------------------|--------------------------------------|
| 1        | **Primary** | GitHub Copilot        | Default — when Copilot is reachable  |
| 2        | **Secondary** | Cloud LLM (OpenAI) | When Copilot circuit is OPEN         |
| 3        | **Fallback** | Local Ollama          | When both cloud tiers are OPEN / offline |

Each cloud tier (Copilot & OpenAI) has an independent **circuit breaker** that opens after N consecutive failures and re-probes after a configurable timeout.

```
            ┌─────────────────────┐
            │     Your App        │
            └─────────┬───────────┘
                      │ POST /ai/query
              AI Gateway Layer
                      │
        ┌─────────────┼─────────────┐
        │             │             │
  🤖 Copilot    🌐 Cloud LLM   💻 Local LLM
  (Primary)    (Secondary)    (Fallback)
  GitHub       OpenAI, etc.   Ollama
```

## 📁 Project Structure

```
ai-gateway/
├── copilot_client.py   # GitHub Copilot client (primary)
├── cloud_client.py     # Cloud LLM client (secondary — OpenAI)
├── local_client.py     # Local LLM client (tertiary — Ollama)
├── router.py           # 3-tier circuit-breaker router
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

# 2. Set tokens (at minimum one cloud tier is required)
export GITHUB_COPILOT_TOKEN="<your-copilot-token>"  # primary
export OPENAI_API_KEY="sk-..."                        # secondary fallback

# 3. Start local Ollama (tertiary fallback — optional but recommended)
curl -fsSL https://ollama.com/install.sh | sh
ollama run llama3

# 4. Start the gateway
uvicorn ai_gateway:app --reload
```

### Option 2 — Docker Compose (recommended)

```bash
GITHUB_COPILOT_TOKEN=<token> OPENAI_API_KEY=sk-... docker compose up
```

The gateway is then available at `http://localhost:8000`.

### Getting a GitHub Copilot token

```bash
# Option A: GitHub CLI (recommended)
gh auth login --scopes copilot
gh auth token

# Option B: VS Code (token stored automatically after installing Copilot extension)
# Read from: ~/.config/github-copilot/hosts.json  (Linux/macOS)
```

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
  "backend": "copilot",
  "state": "closed"
}
```

| Field     | Description                                              |
|-----------|----------------------------------------------------------|
| `response`| The AI model's answer                                    |
| `backend` | `"copilot"`, `"cloud"`, or `"local"` — which tier replied |
| `state`   | Primary (Copilot) circuit state: `closed / open / half_open` |

### `GET /health`

Returns availability of all three backends and current Copilot circuit state.

```json
{
  "status": "ok",
  "copilot_available": true,
  "cloud_available": true,
  "local_available": false,
  "circuit_state": "closed"
}
```

### `POST /admin/reset`

Manually reset both circuit breakers to `closed` (Copilot-preferred) state.

## ⚙️ Configuration (environment variables)

| Variable               | Default                   | Description                                |
|------------------------|---------------------------|--------------------------------------------|
| `GITHUB_COPILOT_TOKEN` | *(from VS Code config)*   | GitHub Copilot OAuth token (primary)       |
| `COPILOT_MODEL`        | `gpt-4o`                  | Copilot model name                         |
| `CLOUD_PROVIDER`       | `openai`                  | Secondary cloud provider                   |
| `CLOUD_MODEL`          | `gpt-4o-mini`             | Secondary cloud model                      |
| `OPENAI_API_KEY`       | *(required for cloud)*    | OpenAI API key (secondary)                 |
| `LOCAL_MODEL`          | `llama3`                  | Ollama model name (fallback)               |
| `OLLAMA_BASE_URL`      | `http://localhost:11434`  | Ollama service URL                         |
| `FAILURE_THRESHOLD`    | `3`                       | Failures before opening a tier's circuit   |
| `RECOVERY_TIMEOUT`     | `300`                     | Seconds before re-probing a failed tier    |

## 🔄 Circuit Breaker State Machine (per tier)

```
CLOSED ──(N failures)──► OPEN ──(timeout)──► HALF-OPEN
  ▲                                               │
  └───────────────(success)──────────────────────┘
```

| State       | Behaviour                                             |
|-------------|-------------------------------------------------------|
| `closed`    | Tier healthy — requests routed here first             |
| `open`      | Tier down — skipped, next tier tried                  |
| `half_open` | Trial request sent to test recovery                   |

## 💻 VS Code + GitHub Copilot

Open this folder in VS Code:

```bash
code ai-gateway/
```

The `.vscode/settings.json` file pre-configures:
- Python test discovery (pytest)
- Copilot inline suggestions enabled
- Correct Python path for module imports

## 🧪 Running Tests

```bash
cd ai-gateway
pytest tests/ -v
```

## 🏗 Hardware Recommendations for Local (Fallback) Models

| RAM      | Suggested model |
|----------|-----------------|
| 8 GB     | `phi3` (3B)     |
| 16 GB    | `llama3` (7B)   |
| 32 GB    | `llama3:13b`    |
| GPU 8 GB+| Any — much faster |

## ⚖️ Tier Trade-offs

| Feature            | Copilot (Primary) | Cloud (Secondary) | Local (Fallback) |
|--------------------|-------------------|-------------------|------------------|
| Accuracy           | ⭐⭐⭐⭐⭐            | ⭐⭐⭐⭐              | ⭐⭐⭐              |
| IDE integration    | ✅ Native           | ❌                 | ❌                |
| Internet required  | Yes               | Yes               | No               |
| Cost               | Copilot plan      | API-based         | Hardware-based   |
| Privacy            | GitHub            | External          | Fully private    |
