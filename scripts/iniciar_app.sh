#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="$ROOT/vendor/LightOnOCR/.venv/bin/python"

if [ ! -x "$PYTHON" ]; then
  echo "No encuentro el entorno. Ejecuta primero ./scripts/preparar_entorno.sh"
  exit 1
fi

cd "$ROOT"
exec "$ROOT/vendor/LightOnOCR/.venv/bin/streamlit" run "$ROOT/app.py" \
  --server.address 127.0.0.1 \
  --server.port 8501
