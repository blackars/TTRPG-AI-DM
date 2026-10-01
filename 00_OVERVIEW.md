# TTRPG-AI-DM — Overview Inicial

> Dungeon Master con IA + mesa aumentada. Dashboard central + proyector + sonido + cámara cenital.
> Proveedor de verdad: MiniBase-Web vía API. Decisión: **YOLO abierto (AGPL-3.0)**. Si debe ser abierto, que lo sea.

## 1. Contexto que ya existe

* **Sistemas de rol (`Downloads/principales sistemas de rol de mesa.pdf`):** d20 (D&D/Pathfinder), d100/BRP (CoC/RuneQuest), PbtA 2d6, FATE, GURPS 3d6.
* **Reglas RPG-AI (`Downloads/requerimientos actuales.pdf`):** grupo de máquinas de estado orquestadas por modelo que delega. Spawn con cálculo `dX+Y` (ej. 23 xenos = `d20+3`, 7 facebugs = `d8-1` o `d6+1`), Mythic GM Emulator con tiradas internas, guion interior secreto con assets reales, etiquetas genero/lore/nombre para filtrar, plantillas historia + input opcional usuario, modos one-shot / campaña capitulada / wargame 1vs1 y 1vsMachine + slot creativo futuro, dados MVP random, filtros lenguaje natural, TTS ES/EN + caja texto siempre, doble pantalla: web stats + proyector escenarios.
* **MiniBase-Web (`Desktop/G I T H U B R E P O S/MINIBASE/MiniBase-Web`):** `Next.js 14 + TS + Tailwind` + `FastAPI + SQLAlchemy + Pandas` + `Supabase Postgres + Auth Google + RLS + pgvector` + `Cloudinary primario + R2/Drive backup`. Contratos clave: `GET /api/minis`, `GET /api/agent/search`, `GET/POST /api/table/state {phase, grid_visible, tokens}`. El DM nunca inventa minis, las pide aquí.

## 2. Arquitectura en 4 bloques

```
[1. MiniBase API] --> [2. DM Core] --> [3. Presentación] + [4. CV/Audio]
  inventario real      máquinas estado   dashboard / proyector / sonido
                       + 3 cerebros      cámara solo lee
```

**DM Core = orquestador, no un solo LLM:**

1. **Determinista rápido (JEV):** Python puro <5ms. Spawn `dX+Y`, reglas d20/d100/2d6/FATE/3d6, Mythic, economía. Sin GPU.
2. **Narrativo lento:** Ollama local `mistral:7b` / `llama3.1:8b` / `qwen2.5:7b`. Narración, NPCs, guion secreto. 5-15s ok para rol.
3. **Utilitario + embeddings:** `MiniLM / nomic-embed` + `pgvector` + `CLIP ViT-B/32` para `search_semantic / get_dataset`, y extractor de deltas (stats, inventario, relaciones).

Máquina de estados: `Game > Chapter > Encounter > Turn > Phase (narrativa / movement / combate / loot)`. Solo `phase=movement` pone `grid_visible=true`.

## 3. Enfoque Eficiente Elegido: YOLO Segmentación Agnóstica + Lógica

No entrenar "Orco con hacha vs Guerrero con espada". Entrenar solo 2 cosas abstractas.

### Paso 1 — Segmentación ciega

* 5-8 fotos fondo negro por mini -> PNG sin fondo con `rembg`.
* Aumento sintético con `Albumentations` o Roboflow: pegar PNGs sobre fotos del tablero real **con y sin proyección encendida**, varias posiciones/luces/escalas.
* Entrenar `yolo11n-seg` o `yolov8n-seg` con 1-2 clases: `pieza_juego`, `escenografia/muro`. 100-200 imágenes bastan porque solo aprende "plástico/resina vs tablero".
* Modelo no clasifica identidad, solo recorta siluetas + polígonos.

### Paso 2 — Pacto inicial (inicialización)

El DM ya sabe qué IDs están activos por MiniBase. Flujo:

1. DM dice: "Coloca tu Mago en A1".
2. Jugador la coloca. YOLO detecta silueta nueva en A1.
3. Software vincula: `ID_Mago = silueta_en_A1`. Listo, sin clasificación visual.

### Paso 3 — Tracking lógico

* `ByteTrack` o proximidad OpenCV: si silueta de A1 desaparece y aparece una igual en A2 -> el Mago se movió a A2.
* Estado caído/muerto sin reentrenar: medir `bounding-box ratio` del polígono. De pie = alto/estrecho, caído = alargado/bajo.

```text
[Usuario selecciona minis] -> [Cámara captura] -> [YOLO siluetas+muros]
  -> [Homografía a casillas A1,B4] -> [Lógica cruza: A1 era Orco, ahora en A2, a 1 de muro A3]
```

Beneficios: entrenamiento mínimo, escalable (10 minis nuevas = cero reentren), física precisa en código, no en adivinación neuronal.

## 4. Grid como Requerimiento de Primera Clase

No es decoración, es el sistema de coordenadas. Triple:

* **Grid Lógico:** matriz `A1..HxW`, tamaño casilla en mm, rangos `movement/range` de `rpg_profile`. Aquí se calculan distancias ataque y spawn estratégico.
* **Grid Proyectado:** Canvas SVG fullscreen oscuro en monitor 2. Solo visible si `phase=movement`. Dibuja: grid, puntos spawn por clase `npc/jugador/enemigo/criatura`, círculos/flechas/símbolos para explicar movimientos.
* **Grid Detectado:** homografía cámara <-> lógica con 4 ArUco en esquinas. Traduce centros de siluetas a casillas exactas.

Calibración inicial obligatoria antes de cada partida.

## 5. Punto Crítico: la IA también proyecta (loop proyector->cámara)

La luz proyectada contamina la detección. Como controlamos el `frame_conocido`, lo resolvemos así:

* Dataset incluye tablero con grid proyectado encendido/apagado.
* En runtime: `frame_cámara - frame_conocido_proyectado` o captura diferencial de 2 frames (tenue para tracking / full para jugador).
* Nunca proyectar ArUco virtuales, siempre físicos impresos.

## 6. Máquinas y Conexión

Licencia abierta = sin miedo a red local / SaaS interno, solo obliga a publicar código (ya previsto).

* **MVP 1 PC:** laptop GTX 1660 / RTX 3060 + 16GB. Corre `web :3000 + api :8000 + Ollama + Piper + yolo11n-seg + OBS`. Webcam cenital 1080p USB + proyector HDMI extendido + parlante. Todo `localhost`, WebSocket para `table/state`.
* **Ideal 2:** M1 Mesa (cámara+proyector+YOLO+TTS) + M2 Servidor (MiniBase API + Ollama grande). LAN `http://192.168.1.X:8000`.
* **Borde 3 (futuro):** Jetson / Pi5 solo CV con Roboflow Inference.

## 7. Inputs por Modelo

* **YOLO-seg:** PNGs sin fondo + fotos tablero vacío con/sin luz + video 30s moviendo 3 minis para test. Runtime: frame 1280x720 + `tokens` esperados para re-ID.
* **CLIP/pgvector:** `query + filtros tag/type/genre/lore` -> candidatos spawn.
* **LLM narrativo:** plantilla JSON historia + inventario real `{slug: cantidad}` + lore/stats + fase + tirada Mythic + output JEV `dX+Y`.
* **TTS:** texto + `lang es|en + speaker narrador/NPC`. `Piper (MIT, CPU)` base + `XTTS-v2/Chatterbox` para clonación.
* **Audio ambiente:** `freesound.org + Web Audio API`, no generar todo con IA.

## 8. Salidas

* **Dashboard (monitor 1):** stats, dados, caja texto siempre, respuestas, `agent/search`.
* **Proyector (monitor 2):** solo escenarios, grid solo en movement, spawn markers, overlays.
* **Sonido:** TTS + ambiente por capas, cola pause/resume.
* **Cámara:** `POST /vision/match -> top-5 + x,y,theta,track_id`. No guardar video, guardar eventos.

## 9. Stack 100% Free / Abierto

| Uso | Elección |
|---|---|
| Inventario | MiniBase actual: Vercel Hobby + Supabase 500MB + Cloudinary free + R2 10GB |
| CV seg | `Ultralytics yolo11n-seg (AGPL-3.0)` + `Albumentations (MIT)` + `OpenCV (Apache2)` + `ByteTrack (MIT)` |
| LLM local | `Ollama + mistral:7b / llama3.1:8b` + `nomic-embed-text` |
| Proyección | `React Canvas + WebSocket table/state` |
| TTS ES/EN | `Piper es_MX/en_US` |
| Dados MVP | `Math.random`, v2 `react-three-fiber + cannon` |

## 10. Roadmap

1. P1-P3 MiniBase real + importar `template.xlsx` + `miniatures.db` (fix `name[0]`).
2. P4 dataset visión `rembg + Albumentations + phash + CLIP`.
3. P5 `table/state` + proyector dual + ArUco.
4. P6 JEV `rules.py` + Mythic + spawn `dX+Y`.
5. P7 DM Ollama + Piper ES/EN.
6. P8 `yolo11n-seg + ByteTrack` en tablero real.

---
*Inicio v0.1 — siguiente: detallar `01_RULES_JEV.md` y `02_VISION_DATASET.md`.*
