# tenir.py — genera variantes de color/luz desde fotos reales (sin retomar).
# Simula aro RGB y cálidas: azul, rojo, verde, calido, penumbra.
# Uso: python tenir.py --foto ruta.jpg --color azul
#      python tenir.py --carpeta dataset/frames_phone --color azul --out dataset/variantes_color
import argparse
from pathlib import Path

import cv2
import numpy as np

RECETAS = {
    # (matiz_hsv, saturación_extra, brillo_mult)
    "azul": (105, 80, 0.55),
    "rojo": (0, 80, 0.6),
    "verde": (60, 70, 0.6),
    "calido": (15, 40, 1.0),
    "penumbra": (0, 0, 0.45),
    "frio": (100, 25, 0.95),
}


def tenir(frame, color):
    h_, s_, m = RECETAS[color]
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
    if s_:
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] + s_, 0, 255)
    if color in ("azul", "rojo", "verde", "frio", "calido"):
        hsv[:, :, 0] = hsv[:, :, 0] * 0.35 + h_ * 0.65
    out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32) * m
    return np.clip(out, 0, 255).astype(np.uint8)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--foto", default=None)
    ap.add_argument("--carpeta", default=None)
    ap.add_argument("--color", required=True, choices=list(RECETAS))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.foto:
        fr = cv2.imread(a.foto)
        assert fr is not None, f"no leo {a.foto}"
        dst = a.out or str(Path(a.foto).with_name(Path(a.foto).stem + f"_{a.color}.jpg"))
        cv2.imwrite(dst, tenir(fr, a.color))
        print("OK", dst)
    elif a.carpeta:
        src = Path(a.carpeta)
        dst = Path(a.out or (str(src) + "_" + a.color))
        dst.mkdir(parents=True, exist_ok=True)
        n = 0
        for f in sorted(src.glob("*.jpg")):
            fr = cv2.imread(str(f))
            if fr is None:
                continue
            cv2.imwrite(str(dst / f"{f.stem}_{a.color}.jpg"), tenir(fr, a.color))
            n += 1
        print(f"OK {n} variantes {a.color} en {dst}")
