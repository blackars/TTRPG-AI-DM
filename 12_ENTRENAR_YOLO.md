# 12 — Entrenar YOLO (Colab recomendado, tu RTX 3050 4GB para jugar)

Tu GPU real: **RTX 3050 Laptop 4GB** (no 3060, pero sirve). 4GB alcanza para JUGAR (detectar en vivo),
pero entrenar ahí es lento y justo. Plan: **entrena en Colab gratis (T4 15GB), juega en tu RTX**.

## Decisión de diseño (tuya, queda fija)

- **Caído por visión: NO se hace.** Una mini caída por narrativa = mini fuera de escena o la decide el DM
  (TinyJev/modelo), no la cámara. YOLO solo aprende 1 clase: `pieza_juego`. Sin clase caído.
- Sensibilidad del grid en vivo ya no importa tanto: era solo el previo. El estado de pie/caído
  lo manda el juego, no el detector.

## Lote listo para subir

- `data/synth_lote1_colab.zip` (20MB): 200 sintéticas + labels + `data.yaml`, clase 0.
- `dataset/frames_video/` 69 fotos reales del teléfono (tus 3 videos): mézclalas al lote 2 después.

## Entrenar en Colab (30 min, gratis)

1. Ve a colab.research.google.com, nuevo cuaderno, cambia a GPU: Entorno > Cambiar tipo > T4.
2. Sube `synth_lote1_colab.zip` al panel archivos y corre estas celdas en orden:

```python
# Celda 1: instala
!pip install ultralytics -q
# Celda 2: descomprime
!unzip -q synth_lote1_colab.zip -d synth_lote1
# Celda 3: entrena nano segmentación (rápido, ~20-40 min en T4)
from ultralytics import YOLO
m = YOLO("yolo11n-seg.pt")
m.train(data="synth_lote1/data_colab.yaml", epochs=60, imgsz=640, batch=16, name="mesa_nano")
# Celda 4: mide
m.val()
# Celda 5: prueba con 1 foto real tuya (súbela al colab)
m.predict("tu_foto_real.jpg", save=True)
```

3. Objetivo MVP: `mAP50_mask > 0.80` y que en tu foto real encierre la verde. Descarga
   `runs/segment/mesa_nano/weights/best.pt` y guárdalo en `TTRPG-AI-DM/vision/weights/`.

## Alternativa local en tu RTX 3050 4GB (lento, solo si Colab falla)

```powershell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install ultralytics
python -c "import torch; print(torch.cuda.is_available())"  # debe decir True
yolo segment train model=yolo11n-seg.pt data=data/synth_lote1/data.yaml epochs=60 imgsz=640 batch=4 workers=2 name=mesa_nano
```
Con 4GB usa `batch=4` sí o sí. Si da error de memoria, baja a `imgsz=512`.

## Qué sigue después del best.pt (orden)

1. `yolo export model=best.pt format=onnx` para inferencia rápida en tu RTX/CPU.
2. Puente visión→DM: cada detección `pieza_juego (x,y)` → celda 4x4 → evento a TinyJev
   (`decide_tinyjev.py`: ¿ataca? ¿spawnea?) → `table/state` → narración. Ese puente es lo que
   le da inteligencia al DM de fondo, no más fotos.
3. Lote 2: suma tus 69 frames reales + 2-3 minis nuevas + 1 fondo distinto. Nunca RGB todavía.
