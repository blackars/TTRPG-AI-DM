# 05 — Máquinas, Cámara, Proyector, Red e Instalación

> Empieza con 1 PC. Escala a 2 solo si el LLM te frena la mesa. Todo localhost primero, LAN después.

## 1. Topologías

**A. MVP 1 PC (recomendado inicio):**

```text
[PC gaming] --HDMI extendido--> [Proyector cenital 45°]
    | --USB--> [Webcam cenital 1080p] (trípode o brazo, 60-80cm sobre mesa)
    | --BT/3.5mm--> [Parlante]
    | corre: web:3000 + api:8000 + ollama:11434 + tts + yolo + ws
```

Specs mínimas: GTX 1660 6GB / RTX 3060, 16GB RAM, SSD 100GB libres. Sin GPU dedicada también funciona (YOLO ONNX CPU + `mistral:7b-Q4`), solo más lento (Story 15-25s).

**B. Ideal 2 PCs (cuando quieras fluidez total):**

```text
M1 Mesa (GPU): cámara + proyector + web/table + YOLO + Piper + ws
M2 Servidor (CPU/RAM): FastAPI MiniBase proxy + Ollama grande + Supabase + pgvector
LAN: http://192.168.1.10:8000 (M2), ws://192.168.1.11:3000 (M1). IP fija o hostname.
```

**C. Borde (futuro):** Jetson Nano / Pi5 solo `Roboflow Inference` + cámara, manda detecciones por MQTT/HTTP a M1.

## 2. Compras / montaje físico (orden)

1. Webcam 1080p con foco manual (Logitech C920 o similar) + brazo articulado cenital. Evita gran angular, deforma casillas.
2. Proyector 3000+ lúmenes si hay luz ambiente, 2000 basta a oscuras. Tiro corto ideal para no dar sombra con la cabeza.
3. 4 ArUco impresos mate 5x5cm en esquinas (no brillantes, no proyectados).
4. Mesa mate clara u oscura lisa. Tablero físico o lona impresa con marcas tenues (el grid fino lo pone el proyector).
5. Parlante dedicado, no el del proyector (latencia + calidad).

Distancias: cámara 70cm -> cubre ~90x60cm a 1080p (~12px/mm, suficiente para seg). Proyector 1.5-2m según tiro. Calibrar de noche con misma luz de juego.

## 3. Red y puertos (todo free, sin cloud obligatorio)

| Servicio | Puerto | URL MVP |
|---|---|---|
| web dashboard | 3000 | http://localhost:3000 |
| web proyector kiosco | 3000 | http://localhost:3000/table?encounter=enc03 |
| FastAPI MiniBase + JEV + visión | 8000 | http://localhost:8000/docs |
| Ollama | 11434 | http://localhost:11434/v1 |
| TTS Piper server | 5000 | http://localhost:5000/v1/audio/speech |
| WS mesa | 3000/ws | ws://localhost:3000/ws/table/enc03 |

En 2 PCs: abre firewall solo LAN `8000,11434,3000`, nada a internet. Todo funciona offline tras `ollama pull` + `pip install`.

## 4. Instalación paso a paso (Windows, tu caso)

```powershell
# 1. Base
winget install Python.3.11 Ollama.Ollama Git.Git
ollama pull mistral:7b-instruct; ollama pull nomic-embed-text
pip install ultralytics opencv-python albumentations rembg supabase fastapi uvicorn

# 2. MiniBase (ya lo tienes) + TTRPG-AI-DM
# Desktop/GITHUB REPOS/MINIBASE/MiniBase-Web -> .env con SUPABASE_URL, CLOUDINARY
# Desktop/TTRPG-AI-DM -> python -m venv .venv; pip install -r requirements.txt (crear luego)

# 3. Arrancar MVP (3 terminales)
ollama serve
uvicorn api.main:app --reload --port 8000
npm run dev --prefix "..\G I T H U B R E P O S\MINIBASE\MiniBase-Web\web"
# Chrome kiosco en monitor 2:
# chrome --kiosk --app=http://localhost:3000/table?encounter=enc03
```

Script futuro: `INICIAR_MESA.bat` que levanta ollama + api + web + abre dashboard y kiosco.

## 5. Orden de pruebas (no saltar)

1. `table/state` manual: cambia fase, verifica grid ON/OFF en proyector <200ms.
2. Pacto con 3 minis + tracking A1->A2 sin LLM.
3. Spawn `d20+3` con 23 xenos reales MiniBase + markers.
4. Turno narrativo completo ES + TTS.
5. Partida 30 min con luz real, mide `mAP` + latencia Story.

Si algo falla, es casi siempre: ArUco tapado, IPs cambiadas, o proyector en duplicar en vez de extender. Checklist en `RUNBOOK.md` (siguiente doc).

## 6. Costo $0 / abierto

Todo lo aquí es AGPL/MIT/Apache2. Al publicar repo TTRPG-AI-DM usa `AGPL-3.0` (hereda YOLO) + `LICENSE` + `MODELS.md` con pesos y dataset sintético versionado. Más manos pueden mejorarlo, como pediste.
