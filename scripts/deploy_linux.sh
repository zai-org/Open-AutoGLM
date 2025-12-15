#!/usr/bin/env bash
set -euo pipefail

# Automated deploy script for Linux/macOS
# Usage: ./scripts/deploy_linux.sh [vllm|sglang|none]
MODE=${1:-none}
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "== Open-AutoGLM automated deploy (unix) =="

# Check python
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v py >/dev/null 2>&1; then
  PY="py -3"
else
  echo "Python3 not found. Install Python 3.10+ and retry." >&2
  exit 1
fi

$PY --version

# create venv
if [ ! -d .venv ]; then
  echo "Creating virtualenv .venv..."
  $PY -m venv .venv
else
  echo ".venv exists, skipping creation."
fi

# activate venv for this script
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .

# check adb
if command -v adb >/dev/null 2>&1; then
  echo "ADB found in PATH"
else
  echo "ADB not found. Install platform-tools and add to PATH as README suggests." >&2
fi

case "$MODE" in
  vllm)
    echo "Starting vLLM server (foreground)..."
    python -m vllm.entrypoints.openai.api_server \
      --served-model-name autoglm-phone-9b \
      --model zai-org/AutoGLM-Phone-9B \
      --port 8000
    ;;
  sglang)
    echo "Starting SGLang server (foreground)..."
    python -m sglang.launch_server --model-path zai-org/AutoGLM-Phone-9B --served-model-name autoglm-phone-9b --port 8000
    ;;
  none)
    echo "Skipping model start. To run the agent: source .venv/bin/activate && python main.py --base-url http://localhost:8000/v1 --model autoglm-phone-9b"
    ;;
  *)
    echo "Unknown mode: $MODE" && exit 2
    ;;
esac
