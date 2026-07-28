#!/usr/bin/env bash
# Serve a merged Qwen3-VL-4B MobileForge LoRA model through vLLM.
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 /path/to/merged-model" >&2
  exit 2
fi

MODEL_DIR="$1"
SERVED_NAME="${SERVED_NAME:-qwen3-vl-4b-mobileforge-sft}"
PORT="${PORT:-8000}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-24576}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.85}"
MAX_PIXELS="${MAX_PIXELS:-1258291}"

if [[ ! -d "$MODEL_DIR" ]]; then
  echo "Model directory not found: $MODEL_DIR" >&2
  exit 2
fi

exec python -m vllm.entrypoints.openai.api_server \
  --model "$MODEL_DIR" \
  --served-model-name "$SERVED_NAME" \
  --port "$PORT" \
  --max-model-len "$MAX_MODEL_LEN" \
  --limit-mm-per-prompt '{"image":10}' \
  --mm-processor-kwargs "{\"max_pixels\":$MAX_PIXELS}" \
  --chat-template-content-format string \
  --gpu-memory-utilization "$GPU_MEMORY_UTILIZATION"
