# =============================================================================
# AI Gateway — Windows setup script (PowerShell 5.1+ / PowerShell 7+)
# =============================================================================
# Tested on: Windows 10 21H2+, Windows 11
#
# Usage — open PowerShell as a regular user and run:
#   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
#   .\scripts\setup-windows.ps1
#
# What this script does:
#   1. Installs Python 3.11 via winget (if not already present)
#   2. Creates a virtual environment and installs Python dependencies
#   3. Installs Ollama for Windows (CPU-only local fallback)
#   4. Creates a .env file template
#   5. Prints the commands to start the gateway
# =============================================================================

#Requires -Version 5.1

$ErrorActionPreference = "Stop"

$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$GatewayDir = Split-Path -Parent $ScriptDir

Write-Host "==> AI Gateway — Windows Setup"
Write-Host "    Gateway directory: $GatewayDir"
Write-Host ""

# ---------------------------------------------------------------------------
# Helper: test whether a command exists on PATH
# ---------------------------------------------------------------------------
function Test-Command($cmd) {
    $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue)
}

# ---------------------------------------------------------------------------
# 1. Python 3.11+
# ---------------------------------------------------------------------------
$pythonOk = $false
if (Test-Command "python") {
    $ver = & python --version 2>&1
    if ($ver -match "Python 3\.(1[1-9]|[2-9]\d)") {
        $pythonOk = $true
        Write-Host "==> Python already installed: $ver"
    }
}

if (-not $pythonOk) {
    Write-Host "==> Installing Python 3.11 via winget..."
    if (Test-Command "winget") {
        winget install --id Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
        # Refresh PATH so python is found immediately
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
                    [System.Environment]::GetEnvironmentVariable("Path","User")
    } else {
        Write-Host ""
        Write-Host "ERROR: winget is not available. Please install Python 3.11+ manually from:"
        Write-Host "       https://www.python.org/downloads/"
        Write-Host "       Then re-run this script."
        exit 1
    }
}

$PythonExe = "python"

# ---------------------------------------------------------------------------
# 2. Virtual environment + dependencies
# ---------------------------------------------------------------------------
Set-Location $GatewayDir

if (-not (Test-Path ".venv")) {
    Write-Host "==> Creating virtual environment (.venv)..."
    & $PythonExe -m venv .venv
}

Write-Host "==> Installing Python dependencies..."
& ".venv\Scripts\python.exe" -m pip install --upgrade pip -q
& ".venv\Scripts\pip.exe"    install -r requirements.txt -q
Write-Host "==> Dependencies installed."

# ---------------------------------------------------------------------------
# 3. Ollama for Windows (CPU-only — no GPU required)
# ---------------------------------------------------------------------------
if (-not (Test-Command "ollama")) {
    Write-Host "==> Installing Ollama for Windows via winget..."
    if (Test-Command "winget") {
        winget install --id Ollama.Ollama --silent --accept-package-agreements --accept-source-agreements
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
                    [System.Environment]::GetEnvironmentVariable("Path","User")
    } else {
        Write-Host ""
        Write-Host "  winget not available. Download Ollama manually from:"
        Write-Host "  https://ollama.com/download/windows"
        Write-Host "  Then re-run this script."
    }
} else {
    $ollamaVer = & ollama --version 2>&1
    Write-Host "==> Ollama already installed: $ollamaVer"
}

# Start Ollama app (it runs in the system tray on Windows)
if (Test-Command "ollama") {
    Write-Host "==> Starting Ollama service..."
    Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2

    Write-Host "==> Pulling Ollama model (phi3 — smallest, runs on 8 GB RAM)..."
    try {
        & ollama pull phi3
    } catch {
        Write-Host "    (Skipped — run 'ollama pull phi3' manually after Ollama starts)"
    }
}

# ---------------------------------------------------------------------------
# 4. .env template
# ---------------------------------------------------------------------------
$EnvFile = Join-Path $GatewayDir ".env"
if (-not (Test-Path $EnvFile)) {
    Write-Host "==> Creating .env template..."
    @"
# AI Gateway — environment variables
# Fill in the values below, then re-run the gateway.

# Tier 1 — GitHub Copilot (primary)
# Get your token: gh auth login --scopes copilot  (then: gh auth token)
GITHUB_COPILOT_TOKEN=

# Tier 2 — Cloud LLM (secondary, e.g. OpenAI)
OPENAI_API_KEY=

# Tier 3 — Local Ollama (fallback)
OLLAMA_BASE_URL=http://localhost:11434
LOCAL_MODEL=llama3

# Circuit-breaker tuning (optional)
FAILURE_THRESHOLD=3
RECOVERY_TIMEOUT=300
"@ | Set-Content $EnvFile -Encoding UTF8
    Write-Host "    Edit $EnvFile and add your tokens before starting."
} else {
    Write-Host "==> .env already exists — skipping."
}

# ---------------------------------------------------------------------------
# 5. Completion message
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "==> Setup complete! Start the gateway with:"
Write-Host ""
Write-Host "    cd `"$GatewayDir`""
Write-Host "    .venv\Scripts\Activate.ps1"
Write-Host "    Get-Content .env | ForEach-Object {"
Write-Host "        if (`$_ -match '^\s*([^#=\s][^=]*)=(.+)') {"
Write-Host "            [System.Environment]::SetEnvironmentVariable(`$matches[1].Trim(), `$matches[2].Trim(), 'Process')"
Write-Host "        }"
Write-Host "    }"
Write-Host "    uvicorn ai_gateway:app --host 0.0.0.0 --port 8000 --reload"
Write-Host ""
Write-Host "    Then test:"
Write-Host "    Invoke-RestMethod http://localhost:8000/health"
