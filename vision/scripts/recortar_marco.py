# recortar_marco.py — quita bordes (marco Samsung, cursor, sticker, mesa) de fotos a pantalla.
# Las fotos a monitor traen marco negro + cursor + reflejos en los bordes. Esto los recorta.
# Uso: python recortar_marco.py --carpeta dataset/fondos_biomas --borde 0.07
#      (--borde 0.07 = quita 7% por cada lado; sube a 0.10 si queda marco)
import argparse
from pathlib import Path

import cv2

ap = argparse.ArgumentParser()
ap.add_argument("--carpeta", required=True)
ap.add_argument("--borde", type=float, default=0.07)
ap.add_argument("--out", default=None)
a = ap.parse_args()

src = Path(a.carpeta)
dst = Path(a.out or (str(src) + "_crop"))
dst.mkdir(parents=True, exist_ok=True)
n = 0
for f in sorted(src.glob("*.jpg")):
    img = cv2.imread(str(f))
    if img is None:
        continue
    h, w = img.shape[:2]
    dx, dy = int(w * a.borde), int(h * a.borde)
    cv2.imwrite(str(dst / f.name), img[dy:h - dy, dx:w - dx])
    n += 1
print(f"OK {n} recortadas en {dst} (borde {a.borde * 100:.0f}%)")
