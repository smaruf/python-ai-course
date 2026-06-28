# Complete Setup Guide: Qwen CLI with Cloud-First / Local-Fallback on Windows

This is the full end-to-end procedure for your **Dell Latitude 7490 (i5-8350U, 16GB RAM)** using Scoop as the package manager.

---

## 📋 Overview of What You'll Install

| Component | Purpose | Install Method |
|-----------|---------|----------------|
| Git | Version control (required by Aider) | `scoop` |
| Python | Runtime for CLI tools | `scoop` |
| Ollama | Local LLM engine | `scoop` |
| Aider | CLI code analyzer | `pip` |
| LiteLLM | Smart router (online↔local) | `pip` |
| Qwen 1.5B | Local fallback model | `ollama` |

---

## 🔧 STEP 1: Verify Scoop is Installed

Open **PowerShell** and run:

```powershell
scoop --version
```

If Scoop is not installed, install it first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
```

---

## 📦 STEP 2: Install Core Tools via Scoop

```powershell
# Update Scoop itself
scoop update *

# Add the extras bucket (for Ollama)
scoop bucket add extras

# Install Git (required by Aider for repo analysis)
scoop install git

# Install Python
scoop install python

# Install Ollama (local LLM runner)
scoop install ollama
```

Verify installations:
```powershell
git --version
python --version
ollama --version
```

---

## ⚙️ STEP 3: Configure Ollama Environment Variables

Set these **permanently** so Ollama is optimized for your i5-8350U:

```powershell
# Use all 8 threads of your i5-8350U
[Environment]::SetEnvironmentVariable("OLLAMA_NUM_THREADS", "8", "User")

# Keep model in RAM permanently (avoid reload delays)
[Environment]::SetEnvironmentVariable("OLLAMA_KEEP_ALIVE", "-1", "User")

# Bind to localhost (security)
[Environment]::SetEnvironmentVariable("OLLAMA_HOST", "127.0.0.1:11434", "User")
```

> **Restart PowerShell** for these to take effect.

---

## 🚀 STEP 4: Start Ollama Service & Pull Lightweight Model

Start Ollama in the background:
```powershell
ollama serve
```
*(Open a **new PowerShell window** for the next commands — keep this one running.)*

Pull the ultra-light local model:
```powershell
ollama pull qwen2.5-coder:1.5b
```

Test it works:
```powershell
ollama run qwen2.5-coder:1.5b "Hello, respond with one word"
```
Type `/bye` to exit.

---

## 🐍 STEP 5: Install Python CLI Tools via Pip

```powershell
# Install Aider (code-aware CLI assistant)
pip install aider-chat

# Install LiteLLM with proxy support
pip install "litellm[proxy]"
```

Verify:
```powershell
aider --version
litellm --version
```

---

## 🔑 STEP 6: Get an OpenRouter API Key

1. Go to [https://openrouter.ai/keys](https://openrouter.ai/keys)
2. Sign up / Log in
3. Click **"Create Key"**
4. Copy the key (starts with `sk-or-v1-...`)
5. Top up $5 credit (Qwen3 via OpenRouter is very cheap — ~$0.001 per request)

Save it as a permanent environment variable:
```powershell
# Replace with your actual key
[Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", "sk-or-v1-YOUR_KEY_HERE", "User")
```

---

## 📁 STEP 7: Create LiteLLM Configuration

Create a config folder and file:

```powershell
# Create config directory
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.llm-config"

# Create the config file
notepad "$env:USERPROFILE\.llm-config\litellm_config.yaml"
```

Paste this into the file and save:

```yaml
model_list:
  # PRIMARY: Latest Qwen3 (online, always updated automatically)
  - model_name: qwen-smart
    litellm_params:
      model: openrouter/qwen/qwen3-coder
      api_key: os.environ/OPENROUTER_API_KEY
      
  # FALLBACK: Ultra-light local (offline, minimal resource usage)
  - model_name: qwen-smart
    litellm_params:
      model: ollama_chat/qwen2.5-coder:1.5b

router_settings:
  num_retries: 1
  timeout: 25
  fallbacks:
    - qwen-smart: ["ollama_chat/qwen2.5-coder:1.5b"]
```

---

## 🔄 STEP 8: Start the LiteLLM Proxy

Open a **new PowerShell window** and run:

```powershell
litellm --config "$env:USERPROFILE\.llm-config\litellm_config.yaml" --port 4000
```

You should see:
```
Application startup complete.
Uvicorn running on http://127.0.0.1:4000
```

> **Keep this window open.** This is your smart router.

---

## 💻 STEP 9: Launch Aider on Your Project

Open a **third PowerShell window** and navigate to your project:

```powershell
cd "C:\path\to\your\project"

# Initialize git if not already a repo (Aider requires git)
git init
git add .
git commit -m "Initial commit before AI analysis"

# Launch Aider pointing to your LiteLLM proxy
aider --model openai/qwen-smart `
      --openai-api-base http://localhost:4000/v1 `
      --openai-api-key "sk-dummy"
```

You're now inside Aider's interactive CLI, connected to your smart router.

---

## 🎯 STEP 10: Usage Examples

### When Online (uses Qwen3-Coder from cloud):
```
> /add src/auth.py
> Refactor the login function to use JWT tokens
```
→ Routed to **Qwen3-Coder** (latest, most intelligent)

### When Offline (auto-fallback to local):
```
> /add src/utils.py
> Fix the typo in calculate_total function
```
→ Automatically falls back to **Qwen2.5-Coder 1.5B** (local, fast, lightweight)

### Useful Aider Commands:
| Command | Purpose |
|---------|---------|
| `/add filename.py` | Add file to context |
| `/drop filename.py` | Remove file from context |
| `/ls` | List files in context |
| `/diff` | Show pending changes |
| `/undo` | Revert last change |
| `/run pytest` | Run a shell command |
| `/exit` | Quit Aider |

---

## 🚀 BONUS: Create a One-Click Startup Script

Save this as `start-qwen-cli.ps1` on your Desktop:

```powershell
# Start Ollama in background
Start-Process -WindowStyle Hidden -FilePath "ollama" -ArgumentList "serve"

# Wait for Ollama to start
Start-Sleep -Seconds 3

# Start LiteLLM proxy in background
Start-Process -WindowStyle Hidden -FilePath "litellm" -ArgumentList "--config $env:USERPROFILE\.llm-config\litellm_config.yaml --port 4000"

# Wait for proxy
Start-Sleep -Seconds 5

# Launch Aider in current window
Write-Host "✅ Ollama and LiteLLM proxy running." -ForegroundColor Green
Write-Host "🚀 Starting Aider..." -ForegroundColor Cyan
aider --model openai/qwen-smart --openai-api-base http://localhost:4000/v1 --openai-api-key "sk-dummy"
```

Run it with:
```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\Desktop\start-qwen-cli.ps1"
```

---

## 📊 Summary of Your Setup

```
┌─────────────────────────────────────────────────┐
│  YOU (CLI: Aider)                                │
│         ↓                                        │
│  LiteLLM Proxy (localhost:4000)                  │
│         ↓                                        │
│    ┌──────────────────┐                          │
│    │  Try Online?     │───── YES ──→ Qwen3-Coder│
│    │  (OpenRouter)    │            (Cloud, best) │
│    └──────────────────┘                          │
│         ↓ NO (offline/timeout)                   │
│    Qwen2.5-Coder 1.5B (Local, fast, light)       │
└─────────────────────────────────────────────────┘
```

---

## ✅ Verification Checklist

- [ ] `scoop list` shows: git, python, ollama
- [ ] `ollama list` shows: `qwen2.5-coder:1.5b`
- [ ] `pip list` shows: aider-chat, litellm
- [ ] `$env:OPENROUTER_API_KEY` is set
- [ ] LiteLLM proxy responds at `http://localhost:4000/health`
- [ ] Aider launches and can chat with your project

You now have a production-grade, cloud-first AI coding assistant with automatic offline fallback, all managed through Scoop! 🎉
