#!/usr/bin/env bash
# =============================================================================
# AI Gateway — macOS setup script
# =============================================================================
# Tested on: macOS 13 Ventura, macOS 14 Sonoma (Intel & Apple Silicon)
#
# Usage:
#   chmod +x scripts/setup-mac.sh
#   ./scripts/setup-mac.sh
#
# What this script does:
#   1. Ensures Homebrew is installed
#   2. Installs Python 3.11+ and creates a virtual environment
#   3. Installs Python dependencies
#   4. Installs Ollama (CPU-only local fallback)
#   5. Creates a .env file template
#   6. Starts the gateway
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATEWAY_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "==> AI Gateway — macOS Setup"
echo "    Gateway directory: $GATEWAY_DIR"
echo ""

# ---------------------------------------------------------------------------
# 1. Homebrew
# ---------------------------------------------------------------------------
if ! command -v brew &>/dev/null; then
  echo "==> Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  # Add brew to PATH for Apple Silicon Macs
  if [[ -f /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  fi
else
  echo "==> Homebrew already installed: $(brew --version | head -1)"
fi

# ---------------------------------------------------------------------------
# 2. Python 3.11+
# ---------------------------------------------------------------------------
if ! command -v python3 &>/dev/null || ! python3 -c "import sys; exit(0 if sys.version_info >= (3,11) else 1)" 2>/dev/null; then
  echo "==> Installing Python 3.11 via Homebrew..."
  brew install python@3.11
  PYTHON=python3.11
else
  PYTHON=python3
  echo "==> Python already installed: $($PYTHON --version)"
fi

# ---------------------------------------------------------------------------
# 3. Virtual environment + dependencies
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
# 4. Ollama (local fallback — CPU-only, no GPU needed)
# ---------------------------------------------------------------------------
if ! command -v ollama &>/dev/null; then
  echo "==> Installing Ollama via Homebrew..."
  brew install ollama
else
  echo "==> Ollama already installed: $(ollama --version 2>/dev/null || echo 'unknown version')"
fi

# ---------------------------------------------------------------------------
# 5. .env template
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
# 6. Pull a small Ollama model and start the gateway
# ---------------------------------------------------------------------------
echo ""
echo "==> Starting Ollama service in the background..."
brew services start ollama 2>/dev/null || ollama serve &>/dev/null &
sleep 2

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
