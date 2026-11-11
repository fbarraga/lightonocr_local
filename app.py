import base64
import io
import time
from typing import Optional

import pypdfium2 as pdfium
import requests
import streamlit as st
from PIL import Image

st.set_page_config(page_title="LightOnOCR local", page_icon="📄", layout="wide")

API_URL = "http://127.0.0.1:8010/v1/chat/completions"
MODEL_ID = "lightonai/LightOnOCR-3-1B"
MAX_IMAGE_SIDE = 1540

def pdf_page_to_png(pdf: pdfium.PdfDocument, page_index: int, max_side: int) -> bytes:
    page = pdf[page_index]
    width, height = page.get_size()
    scale = min(2.0, max_side / max(width, height))
    bitmap = page.render(scale=scale)
    pil_image = bitmap.to_pil().convert("RGB")
    if max(pil_image.size) > max_side:
        pil_image.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    output = io.BytesIO()
    pil_image.save(output, format="PNG", optimize=True)
    page.close()
    return output.getvalue()

def call_ocr(image_bytes: bytes, prompt: str, timeout: int) -> str:
    encoded = base64.b64encode(image_bytes).decode("ascii")
    content = [
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{encoded}"},
        }
    ]
    if prompt.strip():
        content.insert(0, {"type": "text", "text": prompt.strip()})

    payload = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": content}],
        "temperature": 0.1,
        "max_tokens": 4096,
    }
    response = requests.post(API_URL, json=payload, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]

def check_server() -> tuple[bool, str]:
    try:
        response = requests.get("http://127.0.0.1:8010/v1/models", timeout=4)
        response.raise_for_status()
        return True, "Servidor local conectado."
    except requests.RequestException as exc:
        return False, f"No se puede conectar con vLLM: {exc}"

st.title("📄 LightOnOCR — OCR local de PDF")
st.caption("El PDF se procesa página por página en tu ordenador. No se envía a ningún servicio externo.")

with st.sidebar:
    st.subheader("Configuración")
    max_side = st.slider("Lado máximo de imagen (px)", 900, 1540, 1540, 50)
    timeout = st.number_input("Tiempo máximo por página (segundos)", 60, 1800, 600, 30)
    prompt_mode = st.radio(
        "Modo de extracción",
        ["Transcripción", "Estructura y bloques (grounding)"],
        help="Transcripción devuelve el contenido en Markdown. Grounding pide bloques con información de posición.",
    )
    prompt = "grounding" if prompt_mode.startswith("Estructura") else ""

server_ok, server_message = check_server()
if server_ok:
    st.success(server_message)
else:
    st.warning(server_message + " Primero ejecuta scripts/iniciar_modelo.sh en otra terminal.")

uploaded = st.file_uploader("Selecciona un documento PDF", type=["pdf"])
if uploaded:
    st.write(f"**Archivo:** {uploaded.name} · **Tamaño:** {uploaded.size / (1024 * 1024):.1f} MB")
    if st.button("Extraer texto", type="primary", disabled=not server_ok):
        try:
            pdf = pdfium.PdfDocument(uploaded.getvalue())
            page_count = len(pdf)
            st.info(f"El documento tiene {page_count} páginas. Se procesarán una a una.")
            progress = st.progress(0)
            status = st.empty()
            results = []
            errors = []

            for index in range(page_count):
                status.write(f"Procesando página {index + 1} de {page_count}…")
                try:
                    png_bytes = pdf_page_to_png(pdf, index, max_side)
                    text = call_ocr(png_bytes, prompt, int(timeout))
                    results.append(f"## Página {index + 1}\n\n{text.strip()}")
                except Exception as exc:
                    errors.append((index + 1, str(exc)))
                    results.append(f"## Página {index + 1}\n\n[ERROR AL PROCESAR ESTA PÁGINA: {exc}]")
                progress.progress((index + 1) / page_count)

            pdf.close()
            final_text = "\n\n---\n\n".join(results)
            status.success("Procesamiento terminado.")
            st.session_state["ocr_text"] = final_text
            st.session_state["ocr_errors"] = errors
            st.session_state["ocr_filename"] = uploaded.name

        except Exception as exc:
            st.error(f"No se pudo abrir o procesar el PDF: {exc}")

if "ocr_text" in st.session_state:
    st.divider()
    st.subheader("Texto extraído")
    if st.session_state.get("ocr_errors"):
        st.warning("Algunas páginas tuvieron errores: " + ", ".join(str(p) for p, _ in st.session_state["ocr_errors"]))
    st.text_area("Resultado Markdown", st.session_state["ocr_text"], height=500)
    stem = st.session_state.get("ocr_filename", "documento").rsplit(".", 1)[0]
    st.download_button(
        "Descargar resultado (.md)",
        data=st.session_state["ocr_text"].encode("utf-8"),
        file_name=f"{stem}_ocr.md",
        mime="text/markdown",
    )
