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
├── scripts/
│   ├── setup-mac.sh        # macOS one-command setup
│   ├── setup-linux.sh      # Linux / Debian / Ubuntu one-command setup
│   ├── setup-wsl.sh        # WSL 2 one-command setup
│   └── setup-windows.ps1   # Windows PowerShell one-command setup
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

## 🚀 Local Deployment (no Docker)

One-command setup scripts are provided for every major local environment.
Each script: installs Python, creates a virtual environment, installs dependencies,
installs Ollama (CPU-only local fallback), and generates a `.env` template.

### Prerequisites (all platforms)

| Requirement | Minimum version | Notes |
|---|---|---|
| Python | 3.11 | Installed by the script if missing |
| pip | latest | Upgraded automatically |
| Ollama | latest | Installed by the script; runs CPU-only |
| GitHub Copilot token | — | `gh auth login --scopes copilot && gh auth token` |
| OpenAI API key | — | Optional; enables cloud secondary tier |

---

### 🍎 macOS (Intel & Apple Silicon)

```bash
cd ai-gateway
chmod +x scripts/setup-mac.sh
./scripts/setup-mac.sh
```

Then start the gateway:

```bash
source .venv/bin/activate
set -a && source .env && set +a        # load tokens from .env
uvicorn ai_gateway:app --host 0.0.0.0 --port 8000 --reload
```

> Requires [Homebrew](https://brew.sh). The script installs it automatically if absent.

---

### 🐧 Linux / Debian / Ubuntu

```bash
cd ai-gateway
chmod +x scripts/setup-linux.sh
./scripts/setup-linux.sh
```

Then start the gateway:

```bash
source .venv/bin/activate
set -a && source .env && set +a
uvicorn ai_gateway:app --host 0.0.0.0 --port 8000 --reload
```

> Requires `sudo` (for `apt-get`). The Ollama installer registers a **systemd** service
> so Ollama restarts automatically on reboot.

---

### 🪟 WSL 2 (Windows Subsystem for Linux)

Open a **WSL terminal** (Ubuntu 22.04 or 24.04 recommended):

```bash
cd ai-gateway
chmod +x scripts/setup-wsl.sh
./scripts/setup-wsl.sh
```

Then start the gateway inside WSL:

```bash
source .venv/bin/activate
set -a && source .env && set +a
uvicorn ai_gateway:app --host 0.0.0.0 --port 8000 --reload
```

Access from Windows browser / `curl`: **`http://localhost:8000`**
(WSL 2 auto-forwards ports to Windows on Windows 11 / WSL 2.0+).

> **Tip — if ports are not auto-forwarded on Windows 10:**
> ```powershell
> # Run once in an elevated PowerShell on the Windows host
> netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 `
>       connectport=8000 connectaddress=$(wsl hostname -I).Split()[0]
> ```

---

### 🪟 Windows (native PowerShell)

Open **PowerShell** (no admin required) and run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
cd ai-gateway
.\scripts\setup-windows.ps1
```

Then start the gateway:

```powershell
.venv\Scripts\Activate.ps1

# Load tokens from .env
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]*)=(.+)') {
        [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), 'Process')
    }
}

uvicorn ai_gateway:app --host 0.0.0.0 --port 8000 --reload
```

> The script installs Python 3.11 and Ollama via **winget** (built into Windows 10 21H2+ and Windows 11).
> If winget is unavailable, download them manually:
> [python.org/downloads](https://www.python.org/downloads/) · [ollama.com/download/windows](https://ollama.com/download/windows)

---

### 🐳 Docker Compose (all platforms)

```bash
GITHUB_COPILOT_TOKEN=<token> OPENAI_API_KEY=sk-... docker compose up
```

The gateway is then available at `http://localhost:8000`.

---

### 🔑 Getting a GitHub Copilot token

```bash
# Option A: GitHub CLI (recommended — works on all platforms)
gh auth login --scopes copilot
gh auth token           # copy this value into GITHUB_COPILOT_TOKEN

# Option B: VS Code extension (token stored automatically)
# Linux/macOS: ~/.config/github-copilot/hosts.json
# Windows:     %APPDATA%\GitHub Copilot\hosts.json
# WSL:         /mnt/c/Users/<you>/AppData/Roaming/GitHub Copilot/hosts.json
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
