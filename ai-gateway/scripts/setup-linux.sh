#!/usr/bin/env bash
# =============================================================================
# AI Gateway — Linux / Debian / Ubuntu setup script
# =============================================================================
# Tested on: Ubuntu 22.04 LTS, Ubuntu 24.04 LTS, Debian 12 Bookworm
#
# Usage:
#   chmod +x scripts/setup-linux.sh
#   ./scripts/setup-linux.sh
#
# What this script does:
#   1. Installs system packages (Python 3.11+, pip, venv, curl)
#   2. Creates a virtual environment and installs Python dependencies
#   3. Installs Ollama (CPU-only local fallback, registered as a systemd service)
#   4. Creates a .env file template
#   5. Prints the command to start the gateway
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATEWAY_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "==> AI Gateway — Linux/Debian Setup"
echo "    Gateway directory: $GATEWAY_DIR"
echo ""

# ---------------------------------------------------------------------------
# 1. System packages
# ---------------------------------------------------------------------------
echo "==> Updating apt and installing system packages..."
sudo apt-get update -qq
sudo apt-get install -y -qq python3 python3-pip python3-venv curl git

# Prefer python3.11 if available; fall back to whatever python3 is present
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

echo "==> Activating virtual environment and installing dependencies..."
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "==> Dependencies installed."

# ---------------------------------------------------------------------------
# 3. Ollama (local fallback — CPU-only, no GPU needed)
#    Official install script registers a systemd service automatically.
# ---------------------------------------------------------------------------
if ! command -v ollama &>/dev/null; then
  echo "==> Installing Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "==> Ollama already installed: $(ollama --version 2>/dev/null || echo 'unknown version')"
fi

# Ensure the systemd service is running (or start manually if systemd unavailable)
if command -v systemctl &>/dev/null && systemctl is-system-running &>/dev/null; then
  sudo systemctl enable --now ollama || true
else
  # Containers / minimal environments without systemd
  if ! pgrep -x ollama &>/dev/null; then
    nohup ollama serve &>/dev/null &
    sleep 2
    echo "    Ollama started in background (PID $!)"
  fi
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

# Tier 3 — Local Ollama (fallback — set automatically to localhost)
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
ollama pull phi3 || echo "    (Skipped — you can run 'ollama pull phi3' manually later)"

echo ""
echo "==> Setup complete! Start the gateway with:"
echo ""
echo "    cd $GATEWAY_DIR"
echo "    source .venv/bin/activate"
echo "    set -a && source .env && set +a   # load tokens"
echo "    uvicorn ai_gateway:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "    Then test:"
echo "    curl http://localhost:8000/health"
