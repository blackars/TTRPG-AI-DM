# extraer_frames.py — videos -> fotos sueltas para el dataset (más recursos para YOLO).
# Cada video de 20s da ~40 fotos útiles (1 cada 0.5s). Tus 3 videos = ~120 fotos reales.
# Uso: python extraer_frames.py  (procesa los 3 videos de tests/sesion1/videos)
#      python extraer_frames.py --cada 15  (1 de cada 15 frames = 1.3 fotos/s a 20fps)
import argparse
from pathlib import Path

import cv2

ap = argparse.ArgumentParser()
ap.add_argument("--cada", type=int, default=10, help="1 de cada N frames (10 = 2 fotos/s)")
a = ap.parse_args()

base = Path(__file__).resolve().parents[2]
vids = sorted((base / "tests" / "sesion1" / "videos").glob("*.mp4"))
out = base / "dataset" / "frames_video"
out.mkdir(parents=True, exist_ok=True)
total = 0
for v in vids:
    cap = cv2.VideoCapture(str(v))
    i, n = 0, 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        if i % a.cada == 0:
            p = out / f"{v.stem}_f{n:04d}.jpg"
            cv2.imwrite(str(p), fr)
            n += 1
        i += 1
    cap.release()
    print(f"{v.name}: {n} frames -> {out}")
    total += n
print(f"Total: {total} fotos reales del teléfono para mezclar con sintéticas.")
