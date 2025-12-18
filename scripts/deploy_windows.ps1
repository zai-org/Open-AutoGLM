<#
Windows automated deployment script for Open-AutoGLM
Usage (PowerShell as user):
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
  .\scripts\deploy_windows.ps1 [-ModelService vllm|sglang|none]
#>
param(
    [ValidateSet('vllm','sglang','none')]
    [string]$ModelService = 'none'
)

$ErrorActionPreference = 'Stop'

Write-Host "== Open-AutoGLM automated deploy (Windows) =="
Write-Host "Working dir: $(Get-Location)"

# Check Python
try {
    & py -3 --version
} catch {
    try { python --version } catch { Write-Error "Python (py or python) not found. Install Python 3.10+ and re-run."; exit 1 }
}

# Create virtualenv
if (-Not (Test-Path -Path ".venv")) {
    Write-Host "Creating virtual environment .venv..."
    & py -3 -m venv .venv
} else {
    Write-Host ".venv already exists, skipping creation."
}

# Activate and install requirements
Write-Host "Installing dependencies into .venv..."
$activate = "$PWD\.venv\Scripts\Activate.ps1"
if (-Not (Test-Path $activate)) { Write-Error "Could not find venv activation script: $activate"; exit 1 }

# Use pip via venv python
$venvPython = "$PWD\\.venv\\Scripts\\python.exe"
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt
& $venvPython -m pip install -e .

# Check adb
try {
    & adb version | Out-Null
    Write-Host "ADB found in PATH."
} catch {
    Write-Warning "ADB not found. Please install platform-tools and add to PATH as described in README."
}

# Model service options
switch ($ModelService) {
    'vllm' {
        Write-Host "Starting vLLM model server (foreground)..."
        Write-Host "Make sure vllm is installed and model is available per README."
        & $venvPython -m vllm.entrypoints.openai.api_server --served-model-name autoglm-phone-9b --model zai-org/AutoGLM-Phone-9B --port 8000
        break
    }
    'sglang' {
        Write-Host "Starting SGLang server (foreground)..."
        Write-Host "Make sure sglang is installed and model path is available."
        & $venvPython -m sglang.launch_server --model-path zai-org/AutoGLM-Phone-9B --served-model-name autoglm-phone-9b --port 8000
        break
    }
    'none' {
        Write-Host "Skipping model server start. To start model service, run vLLM or SGLang per README."
    }
}

Write-Host "Setup complete. To run agent interactively:"
Write-Host "  .\.venv\\Scripts\\Activate.ps1"
Write-Host "  python main.py --base-url http://localhost:8000/v1 --model autoglm-phone-9b"
