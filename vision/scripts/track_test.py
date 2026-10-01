"""track_test.py: video -> casillas con H.npy (sin YOLO aun, usa movimiento).
Paso 1 valida homografia + grid antes de entrenar. Paso 2 conecta YOLO.
Uso: python track_test.py --video tests/capturas/S02_mov.mp4 --grid square --H H.npy
"""
import argparse
import sys

try:
    import cv2
    import numpy as np
except ImportError:
    raise SystemExit("pip install opencv-python numpy")


def apply_H(H, x, y):
    p = H @ np.array([x, y, 1.0])
    return (p[0] / p[2], p[1] / p[2])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--H", required=True)
    ap.add_argument("--grid", choices=["square", "hex"], default="square")
    a = ap.parse_args()
    H = np.load(a.H)
    cap = cv2.VideoCapture(a.video)
    bg = cv2.createBackgroundSubtractorMOG2()
    fid = 0
    print("frame, blobs, casillas(col,row)")
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        fid += 1
        if fid % 5:  # procesa 1 de cada 5 para ir rapido
            continue
        mask = bg.apply(fr)
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cells = []
        for c in cnts:
            if cv2.contourArea(c) < 800:
                continue
            x, y, w, h = cv2.boundingRect(c)
            gx, gy = apply_H(H, x + w / 2, y + h / 2)
            cells.append((int(gx), int(gy), "caido" if w / max(h, 1) > 1.2 else "de_pie"))
        if cells:
            print(fid, len(cells), cells)


if __name__ == "__main__":
    main()
