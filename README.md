# LightOnOCR local: aplicació per extreure text de PDF

Petita aplicació amb Streamlit que converteix les pàgines d'un PDF en imatges i les passa al model LightOnOCR-3-1B, que s'executa al mateix ordinador amb vLLM.

Tot funciona en local: l'aplicació i el model són dos programes que corren a la mateixa màquina i es comuniquen per `127.0.0.1` (l'adreça del propi ordinador). vLLM fa servir el mateix format de peticions que l'API d'OpenAI perquè és un estàndard còmode, però no es connecta a OpenAI ni a cap servei extern.

Projecte desenvolupat per **Francesc Barragan** a l'**Institut Sa Palomera**.

**L'OCR s'executa al teu propi ordinador.** El PDF no es puja a cap API ni a cap servei al núvol. La primera instal·lació sí que necessita Internet per descarregar el codi, les dependències i els pesos del model.

## Requisits

- Linux x86-64.
- GPU NVIDIA compatible amb vLLM i controladors NVIDIA recents.
- Python compatible amb la versió de vLLM instal·lada pel repositori oficial.
- Git, `curl` i Internet durant la instal·lació inicial.
- Espai en disc per a les dependències i els pesos del model.

La RTX A4000 Laptop de 8 GB pot ser un entorn just per a vLLM. L'script comença amb una longitud de context de 8192 i reserva el 85 % de la VRAM per a vLLM. No és una garantia que arrenqui en totes les configuracions: tanca altres processos que facin servir la GPU abans d'iniciar el model.

## 1. Descomprimir

Descomprimeix el ZIP i entra a la carpeta:

```bash
cd lightonocr_local
```

## 2. Preparar l'entorn

```bash
chmod +x scripts/*.sh
./scripts/preparar_entorno.sh
```

Aquest script clona el repositori oficial de LightOnOCR a `vendor/LightOnOCR` i executa la instal·lació recomanada `uv sync --extra vllm`. Després hi afegeix Streamlit i les biblioteques que fa servir aquesta aplicació.

La primera instal·lació pot trigar i descarregar diversos GB.

## 3. Iniciar el model

En un primer terminal:

```bash
./scripts/iniciar_modelo.sh
```

La primera execució descarrega els pesos de `lightonai/LightOnOCR-3-1B` des de Hugging Face. Espera fins que vLLM indiqui que el servidor està a punt. Mantén aquest terminal obert.

## 4. Iniciar l'aplicació

En un segon terminal, des de la carpeta `lightonocr_local`:

```bash
./scripts/iniciar_app.sh
```

Obre al navegador:

http://127.0.0.1:8501

## 5. Fer servir l'aplicació

1. Carrega un PDF.
2. Tria «Transcripción» per obtenir text en Markdown, o «Estructura y bloques» per sol·licitar *grounding*.
3. Prem «Extraer texto».
4. Descarrega el resultat en format `.md`.

Les pàgines es processen de manera seqüencial per limitar l'ús de memòria. Les imatges es limiten a un costat màxim de 1540 píxels.

## Ajustos si vLLM no arrenca per falta de memòria

Primer comprova l'ús de la GPU:

```bash
nvidia-smi
```

Tanca els altres processos de GPU que puguis aturar. Si continua fallant, prova de baixar `--max-model-len` de `8192` a `4096` a `scripts/iniciar_modelo.sh`. Una longitud de context menor pot reduir la memòria de memòria cau KV necessària. No redueixis a cegues `--gpu-memory-utilization`: si queda massa baix, pot impedir que hi càpiguen els pesos del model.

Si apareix un error d'incompatibilitat de versions, torna a executar:

```bash
cd vendor/LightOnOCR
uv sync --extra vllm
```

## Privadesa

- L'aplicació només es connecta a `127.0.0.1:8010`.
- Streamlit escolta a `127.0.0.1:8501`, no a la xarxa local.
- Els PDF i les seves imatges es queden a l'equip durant el processament.
- La descàrrega inicial del model i de les dependències requereix Internet; després, l'OCR es pot fer servir sense enviar documents fora de l'equip.

## Fonts oficials

- Repositori i guia de LightOnOCR: https://github.com/lightonai/LightOnOCR
- Model: https://huggingface.co/lightonai/LightOnOCR-3-1B
- Documentació de vLLM: https://docs.vllm.ai/

## Autoria i crèdits

- **Autor:** Francesc Barragan
- **Centre:** Institut Sa Palomera

Aquesta aplicació és un embolcall local sobre LightOnOCR (de LightOn) i vLLM; els drets del model i de les biblioteques corresponen als seus respectius autors.
