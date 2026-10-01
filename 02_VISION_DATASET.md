# 02 — Visión + Dataset + Grid + Tracking (YOLO agnóstico)

> YOLO no identifica quién es quién. Solo recorta siluetas. La identidad la da el pacto + tracking + MiniBase.
> Decisión licencia: **Ultralytics YOLO abierto AGPL-3.0** (`yolo11n-seg` default, fallback `yolov8n-seg`).

Referencia: `00_OVERVIEW.md §3-§5`, `01_RULES_JEV.md §2` (fases).

## 1. Por qué agnóstico funciona aquí

Tú proyectas y controlas la imagen. Sabes qué grid/PNGs hay en cada frame, así que puedes ignorarlos en detección. MiniBase ya sabe qué minis existen. Solo falta: ¿dónde hay una pieza y en qué casilla?

Clases: solo 2.

* `0: pieza_juego` — cualquier mini/token, de pie o caída.
* `1: escenografia` — muros, puertas, props que bloquean movimiento/visión.

Cero reentrenamiento al comprar minis nuevas.

## 2. Pipeline completo

```text
Calibración (1 vez por mesa)
  ArUco 4 esquinas -> homografía H_camara->grid + H_proyector->grid (OpenCV)

Dataset sintético (PC, sin mesa)
  PNGs sin fondo + fondos tablero -> Albumentations -> 150-300 imgs -> Roboflow -> train seg

Runtime por turno
  [frame_conocido proyector] + [foto cámara 1280x720]
   -> resta/atenuación luz proyectada
   -> yolo11n-seg -> máscaras + boxes
   -> centro máscara * H -> casilla A1..HxW
   -> ByteTrack asocia track_id (pacto inicial en turno 0)
   -> ratio aspecto = caído/de pie, colisión con escenografia
   -> PATCH /api/table/state {tokens:[{track_id, mini_id, x, y, estado}]}
```

## 3. Dataset paso a paso (100% free)

**3.1. Captura base (30 min):**

* 5-8 fotos por mini activa, fondo negro mate, luz blanca difusa, 3 ángulos (frontal, 45°, cenital). Móvil basta.
* 10 fotos tablero vacío: 5 con proyector apagado, 5 con grid típico encendido (blanco tenue + colores spawn). Misma cámara cenital final, 1280x720 o más.
* 1 video 30s moviendo 3 minis para test tracking.

**3.2. Recorte a PNG:**

```bash
pip install rembg onnxruntime pillow
rembg i foto_fondo_negro.jpg mago.png
# o batch: python scripts/cutout.py --in raw/ --out pngs/
```

Revisar bordes: dilatar 1px si hay halo negro, guardar `pngs/{slug}.png` con mismo slug MiniBase.

**3.3. Sintético con Albumentations (local, MIT):**

```python
# scripts/synth.py — idea mínima
# por imagen: elige fondo tablero, pega 2-6 PNGs aleatorios con escala 0.6-1.3,
# rotación, blur leve, cambio HSV para simular luz proyector, sombras.
# exporta YOLO-seg: box + polígono (del alpha del PNG).
import albumentations as A, cv2, random
```

Generar 150-300 imágenes `640x640`. 70% con grid proyectado de fondo, 30% sin. Incluir oclusiones parciales y minis caídas (rotar PNG 90°).

**3.4. Roboflow (free tier) o local:**

* Subir a Roboflow -> Annotate auto (ya tienes polígonos del script, solo verificar) -> Augment extra (brightness ±20%, blur).
* Export `YOLOv11-seg`. Entrenar:

```bash
pip install ultralytics opencv-python
yolo segment train model=yolo11n-seg.pt data=data.yaml epochs=80 imgsz=640 batch=8
# PC sin GPU: epochs=30, imgsz=512, paciencia. O usa Colab free GPU.
yolo segment val model=runs/segment/train/weights/best.pt
yolo export model=best.pt format=onnx  # para inference CPU rápida
```

Métrica objetivo MVP: `mAP50_mask >0.85` en clase pieza, `recall >0.9` (preferimos falsos positivos que perder pieza, la lógica filtra).

## 4. Grid triple + homografía (requerimiento)

* **Lógico:** `grid.json {cols:12, rows:9, cell_mm:50, origen:"A1 arriba-izq"}`. Distancias en casillas, no píxeles.
* **Proyectado:** Canvas SVG en monitor 2. Endpoints: `POST /api/table/project {grid, spawns[], overlays[]}`. Spawns por clase con color: jugador verde, enemigo rojo, npc azul, criatura morado.
* **Detectado:** 4 ArUco `DICT_4X4_50 id 10-13` impresos en esquinas físicas (nunca proyectados).

```python
import cv2
aruco = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
corners, ids, _ = cv2.aruco.detectMarkers(frame, aruco)
H, _ = cv2.findHomography(src_pixeles, dst_casillas)  # src: centros ArUco, dst: (0,0),(W,0),(W,H),(0,H)
gx, gy = cv2.perspectiveTransform(punto_centro_mascara, H)  # -> casilla float -> int
```

Recalibrar si mueves cámara/proyector. Guardar `H.npy` por mesa.

## 5. Tracking + pacto + estados

Turno 0 pacto: DM pide colocar en casillas salida. YOLO detecta N siluetas nuevas -> asigna `track_id -> mini_id` por cercanía a casilla pedida.

Turnos siguientes: `ByteTrack` (o `supervision` free) mantiene `track_id` aunque se ocluya 1-2 frames. Si se pierde >5 frames, marca `perdido` y pide recolocar, no adivina.

Estado caído:

```python
x,y,w,h = cv2.boundingRect(mascara)
ratio = w / max(h,1)
estado = "caido" if ratio > 1.2 else "de_pie"  # calibrar por escala cenital
# cenital pura: usar área vs área esperada por slug + elongación polígono
```

Colisión muro: si casilla destino intersecta máscara `escenografia`, JEV rechaza movimiento.

## 6. Loop proyector->cámara (no omitir)

* Siempre guarda `frame_conocido` que acabas de proyectar (PNG grid + overlays).
* Pre-proceso: `frame_cam - 0.4*frame_conocido_warped` o baja brillo proyector a 60% durante 200ms de captura (parpadeo imperceptible).
* Dataset ya incluye luz proyectada, así que el modelo la tolera. Sin esto, el grid blanco se detecta como pieza.

## 7. Contratos API visión

```
POST /api/vision/detect {image_b64, encounter_id}
 -> {detecciones:[{track_id, x, y, casilla:"B4", clase:"pieza_juego", conf:0.93, estado:"de_pie"}]}
POST /api/vision/pacto {encounter_id, esperado:[{mini_id, casilla}]} -> {asignado:[{mini_id, track_id}]}
GET  /api/table/state?encounter_id= -> {phase, grid_visible, tokens}
```

Cámara nunca guarda video, solo eventos JSONL. Fotos solo para reentrenar con consentimiento mesa.

## 8. Estructura archivos

```
TTRPG-AI-DM/vision/
  scripts/cutout.py, synth.py, calibrate.py, detect.py, track.py
  data/raw/, data/pngs/, data/synth/, data.yaml
  weights/best.pt, weights/best.onnx
  grid.json, H.npy
```

Test aceptación: 5 minis en tablero con grid encendido -> 5 detecciones, casillas correctas ±0, track estable al mover A1->A2, caído detectado al tumbar una.
