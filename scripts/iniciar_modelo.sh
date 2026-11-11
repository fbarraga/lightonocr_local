#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/vendor/LightOnOCR/.venv"

if [ ! -x "$VENV/bin/python" ]; then
  echo "No encuentro el entorno. Ejecuta primero ./scripts/preparar_entorno.sh"
  exit 1
fi

cd "$ROOT"
source "$VENV/bin/activate"

# Configuración inicial prudente para una GPU de 8 GB.
# Si vLLM informa de falta de memoria, revisa que no haya otros procesos usando la GPU.
exec vllm serve lightonai/LightOnOCR-3-1B \
  --limit-mm-per-prompt '{"image": 1}' \
  --max-model-len 8192 \
  --mm-processor-cache-gb 0 \
  --no-enable-prefix-caching \
  --gpu-memory-utilization 0.85 \
  --port 8010
