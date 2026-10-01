# etiquetar_real.py — el nano v1 propone máscaras en fotos REALES, tú aceptas/borras.
# Las aceptadas entran al lote 3 (70% synth + 30% real). Así tus cientos de fotos reales
# consiguen etiquetas casi gratis: el modelo hace el 90%, tú solo quitas las malas.
# Uso: python etiquetar_real.py --carpeta dataset/frames_phone --conf 0.5
# Salida: dataset/reales_label/<foto>.txt (formato YOLO-seg) + preview <foto>_prev.jpg
# Revisa los _prev: borra el .txt de los que estén mal. Lo que quede es dataset.
import argparse
from pathlib import Path

import cv2
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--carpeta", required=True)
ap.add_argument("--weights", default="vision/weights/best.pt")
ap.add_argument("--conf", type=float, default=0.5)
ap.add_argument("--out", default="dataset/reales_label")
a = ap.parse_args()

from ultralytics import YOLO
model = YOLO(a.weights)
out = Path(a.out)
(out / "labels").mkdir(parents=True, exist_ok=True)
(out / "preview").mkdir(parents=True, exist_ok=True)
src = sorted(Path(a.carpeta).glob("*.jpg"))
ok = 0
for f in src:
    res = model.predict(str(f), conf=a.conf, verbose=False)[0]
    h, w = res.orig_shape
    lines = []
    vis = cv2.imread(str(f))
    if res.masks is not None:
        for poly in res.masks.xy:
            xs = np.clip(poly[:, 0] / w, 0, 1)
            ys = np.clip(poly[:, 1] / h, 0, 1)
            pts = " ".join(f"{x:.4f} {y:.4f}" for x, y in zip(xs, ys))
            lines.append(f"0 {pts}")
            cv2.polylines(vis, [poly.astype(int)], True, (0, 255, 0), 3)
    (out / "labels" / (f.stem + ".txt")).write_text("\n".join(lines), encoding="utf-8")
    cv2.imwrite(str(out / "preview" / (f.stem + "_prev.jpg")), vis)
    if lines:
        ok += 1
print(f"{ok}/{len(src)} fotos con propuestas en {out}/labels. Revisa preview y borra los .txt malos.")
