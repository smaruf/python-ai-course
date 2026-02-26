#!/usr/bin/env bash
# =============================================================================
# AI Gateway — WSL (Windows Subsystem for Linux) setup script
# =============================================================================
# Tested on: WSL 2 with Ubuntu 22.04 LTS, Ubuntu 24.04 LTS
#
# Usage (run inside a WSL terminal):
#   chmod +x scripts/setup-wsl.sh
#   ./scripts/setup-wsl.sh
#
# WSL-specific notes:
#   • The gateway listens on 0.0.0.0:8000 inside WSL.
#     Windows can reach it at http://localhost:8000 thanks to WSL 2 port
#     forwarding (automatic since Windows 11 / WSL 2.0).
#   • Ollama runs inside WSL; its API is available at
#     http://localhost:11434 from both WSL and Windows.
#   • If you already have Ollama for Windows installed, you can skip the
#     Ollama install step and set OLLAMA_BASE_URL=http://localhost:11434.
#   • For GPU acceleration inside WSL 2, install the NVIDIA CUDA driver on
#     the Windows host (no separate Linux GPU driver needed).
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATEWAY_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "==> AI Gateway — WSL Setup"
echo "    Gateway directory: $GATEWAY_DIR"

# Verify we are running inside WSL
if ! grep -qiE "(microsoft|wsl)" /proc/version 2>/dev/null; then
  echo "WARNING: /proc/version does not mention WSL. Continuing anyway..."
fi
echo ""

# ---------------------------------------------------------------------------
# 1. System packages (same as Linux)
# ---------------------------------------------------------------------------
echo "==> Updating apt and installing system packages..."
sudo apt-get update -qq
sudo apt-get install -y -qq python3 python3-pip python3-venv curl git

if command -v python3.11 &>/dev/null; then
  PYTHON=python3.11
else
  PYTHON=python3
fi
echo "==> Using Python: $($PYTHON --version)"

# ---------------------------------------------------------------------------
# 2. Virtual environment + dependencies
# ---------------------------------------------------------------------------
cd "$GATEWAY_DIR"

if [[ ! -d .venv ]]; then
  echo "==> Creating virtual environment (.venv)..."
  $PYTHON -m venv .venv
fi

echo "==> Installing Python dependencies..."
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "==> Dependencies installed."

# ---------------------------------------------------------------------------
# 3. Ollama inside WSL
#    WSL 2 does not run systemd by default; we start ollama serve manually.
#    If your WSL distro has systemd enabled (Ubuntu 22.04+ with
#    /etc/wsl.conf [boot] systemd=true), the service will auto-start.
# ---------------------------------------------------------------------------
if ! command -v ollama &>/dev/null; then
  echo "==> Installing Ollama inside WSL..."
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "==> Ollama already installed: $(ollama --version 2>/dev/null || echo 'unknown version')"
fi

# Start ollama serve if not already running
if ! pgrep -x ollama &>/dev/null; then
  echo "==> Starting Ollama in the background..."
  nohup ollama serve > /tmp/ollama.log 2>&1 &
  OLLAMA_PID=$!
  sleep 2
  echo "    Ollama PID: $OLLAMA_PID (log: /tmp/ollama.log)"
else
  echo "==> Ollama already running."
fi

# ---------------------------------------------------------------------------
# 4. .env template
# ---------------------------------------------------------------------------
ENV_FILE="$GATEWAY_DIR/.env"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "==> Creating .env template..."
  cat > "$ENV_FILE" <<'EOF'
# AI Gateway — environment variables
# Fill in the values below, then re-run the gateway.

# Tier 1 — GitHub Copilot (primary)
# Get your token: gh auth login --scopes copilot && gh auth token
GITHUB_COPILOT_TOKEN=

# Tier 2 — Cloud LLM (secondary, e.g. OpenAI)
OPENAI_API_KEY=

# Tier 3 — Local Ollama running inside WSL
OLLAMA_BASE_URL=http://localhost:11434
LOCAL_MODEL=llama3

# Circuit-breaker tuning (optional)
FAILURE_THRESHOLD=3
RECOVERY_TIMEOUT=300
EOF
  echo "    Edit $ENV_FILE and add your tokens before starting."
else
  echo "==> .env already exists — skipping."
fi

# ---------------------------------------------------------------------------
# 5. Pull a small Ollama model
# ---------------------------------------------------------------------------
echo "==> Pulling Ollama model (phi3 — smallest, runs well on 8 GB RAM)..."
ollama pull phi3 || echo "    (Skipped — run 'ollama pull phi3' manually after Ollama starts)"

# ---------------------------------------------------------------------------
# 6. Windows-side access note
# ---------------------------------------------------------------------------
echo ""
echo "==> WSL 2 port forwarding:"
WSL_IP=$(ip -4 addr show eth0 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}' || echo "unknown")
echo "    WSL IP : $WSL_IP"
echo "    Windows can reach the gateway at http://localhost:8000"
echo "    (WSL 2 auto-forwards localhost on Windows 11 / WSL 2.0+)"
echo ""
echo "==> Setup complete! Start the gateway with:"
echo ""
echo "    cd $GATEWAY_DIR"
echo "    source .venv/bin/activate"
echo "    set -a && source .env && set +a"
echo "    uvicorn ai_gateway:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "    Then test from WSL:     curl http://localhost:8000/health"
echo "    Or from Windows:        curl http://localhost:8000/health"
