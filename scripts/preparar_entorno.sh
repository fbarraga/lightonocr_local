#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! command -v git >/dev/null 2>&1; then
  echo "Falta git. Instálalo con el gestor de paquetes de tu distribución."
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "Instalando uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

if [ ! -d vendor/LightOnOCR/.git ]; then
  mkdir -p vendor
  git clone --depth 1 https://github.com/lightonai/LightOnOCR.git vendor/LightOnOCR
fi

cd vendor/LightOnOCR
echo "Instalando el entorno oficial de LightOnOCR con el extra vLLM..."
uv sync --extra vllm

echo "Instalando dependencias de la aplicación..."
uv pip install --python .venv/bin/python streamlit pypdfium2 pillow requests

echo
echo "Entorno preparado."
echo "Desde la carpeta raíz del proyecto, ejecuta:"
echo "  ./scripts/iniciar_modelo.sh"
echo "Y en otra terminal:"
echo "  ./scripts/iniciar_app.sh"
