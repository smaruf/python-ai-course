# AI Gateway — 3-Tier AI Failover (Copilot → Cloud → Local) + RAG

A production-ready AI gateway microservice that routes queries through a **3-tier failover chain** and supports **RAG (Retrieval-Augmented Generation)** — designed for a single laptop without a GPU.

| Priority | Tier        | Backend               | When used                            |
|----------|-------------|-----------------------|--------------------------------------|
| 1        | **Primary** | GitHub Copilot        | Default — when Copilot is reachable  |
| 2        | **Secondary** | Cloud LLM (OpenAI) | When Copilot circuit is OPEN         |
| 3        | **Fallback** | Local Ollama          | When both cloud tiers are OPEN / offline |

**Design goals**:  💻 Single laptop  ❌ No GPU required  🌐 Cloud-first  🛑 Local only on internet cutoff  ⚡ Lightweight  🧩 Language-agnostic REST API

Each cloud tier (Copilot & OpenAI) has an independent **circuit breaker** that opens after N consecutive failures and re-probes after a configurable timeout.

```
             ┌──────────────────────────┐
             │   Your App (any language)│
             │  Python · Java · C# · Go │
             └────────────┬─────────────┘
                          │ HTTP REST
              ┌───────────▼─────────────┐
              │       AI Gateway        │
              │  POST /ai/query         │
              │  POST /ai/query/rag     │
              │  GET  /health           │
              └───────────┬─────────────┘
                          │ 3-tier failover
          ┌───────────────┼───────────────┐
          │               │               │
    🤖 Copilot      🌐 Cloud LLM    💻 Local LLM
    (Primary)       (Secondary)     (Fallback)
    GitHub          OpenAI, etc.    Ollama (CPU)
```

## 📁 Project Structure

```
ai-gateway/
├── copilot_client.py   # GitHub Copilot client (primary)
├── cloud_client.py     # Cloud LLM client (secondary — OpenAI)
├── local_client.py     # Local LLM client (tertiary — Ollama)
├── router.py           # 3-tier circuit-breaker router
├── ai_gateway.py       # FastAPI REST service (plain + RAG endpoints)
├── Dockerfile          # Container image
├── docker-compose.yml  # Gateway + Ollama stack
├── requirements.txt    # Python dependencies
├── examples/
│   ├── client.py       # Python client example
│   ├── Client.java     # Java client example
│   ├── Client.cs       # C# client example
│   └── client.go       # Go client example
├── .vscode/
│   └── settings.json   # VS Code + Copilot settings
└── tests/
    └── test_gateway.py # Unit & integration tests (36 tests)
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

### `POST /ai/query` — plain query

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

### `POST /ai/query/rag` — RAG-augmented query

Grounded responses without a GPU or vector database.  Pass text chunks as
`documents` and the gateway injects them as context before routing through
the 3-tier chain.

```json
{
  "prompt": "What does the document say about refunds?",
  "documents": [
    "Refund policy: customers may return items within 30 days.",
    "No refunds are issued after 30 days from purchase."
  ],
  "max_context_chars": 4000
}
```

Response:

```json
{
  "response": "According to the policy, refunds are available within 30 days of purchase.",
  "backend": "copilot",
  "state": "closed"
}
```

| Field              | Default | Description                                          |
|--------------------|---------|------------------------------------------------------|
| `prompt`           | —       | The question to answer                               |
| `documents`        | —       | List of text chunks to use as context                |
| `max_context_chars`| `4000`  | Max chars of context injected (fits within model limits) |

**Use cases on a no-GPU laptop**:
- Chat over a local code snippet
- Answer questions about a pasted document
- Ground responses in retrieved database rows
- Summarise meeting notes / tickets

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

## 🧩 Language-Agnostic — Client Examples

The gateway is a plain HTTP REST API — call it from any language.
Ready-to-run examples live in `examples/`:

### Python (stdlib — no extra packages)

```python
import json, urllib.request

def query(prompt):
    payload = json.dumps({"prompt": prompt}).encode()
    req = urllib.request.Request(
        "http://localhost:8000/ai/query",
        data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def query_rag(prompt, documents):
    payload = json.dumps({"prompt": prompt, "documents": documents}).encode()
    req = urllib.request.Request(
        "http://localhost:8000/ai/query/rag",
        data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())
```

### Java (stdlib — Java 11+)

```java
HttpClient http = HttpClient.newHttpClient();
HttpRequest req = HttpRequest.newBuilder()
    .uri(URI.create("http://localhost:8000/ai/query"))
    .header("Content-Type", "application/json")
    .POST(HttpRequest.BodyPublishers.ofString("{\"prompt\":\"Hello\"}"))
    .build();
String body = http.send(req, HttpResponse.BodyHandlers.ofString()).body();
```

### C# (stdlib — .NET 6+)

```csharp
var client = new HttpClient();
var content = new StringContent(
    JsonSerializer.Serialize(new { prompt = "Hello" }),
    Encoding.UTF8, "application/json");
var resp = await client.PostAsync("http://localhost:8000/ai/query", content);
var json = await resp.Content.ReadAsStringAsync();
```

### Go (stdlib)

```go
body, _ := json.Marshal(map[string]string{"prompt": "Hello"})
resp, _ := http.Post("http://localhost:8000/ai/query",
    "application/json", bytes.NewReader(body))
result, _ := io.ReadAll(resp.Body)
```

> See `examples/` for complete working programs in all four languages.

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
