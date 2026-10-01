"""Calibracion ArUco 4 esquinas -> H.npy (camara -> grid logico)."""
import argparse
import sys

try:
    import cv2
    import numpy as np
except ImportError:
    print("Falta opencv-python + numpy: pip install opencv-python numpy")
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--foto", required=True, help="foto con 4 ArUco id 10-13 en esquinas")
    ap.add_argument("--cols", type=int, default=12)
    ap.add_argument("--rows", type=int, default=9)
    ap.add_argument("--out", default="H.npy")
    a = ap.parse_args()

    img = cv2.imread(a.foto)
    if img is None:
        print(f"No se pudo leer {a.foto}")
        sys.exit(1)
    aruco = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    corners, ids, _ = cv2.aruco.detectMarkers(img, aruco)
    if ids is None or len(ids) < 4:
        print(f"Solo {0 if ids is None else len(ids)} ArUco detectados, necesitas 4 (id 10-13).")
        sys.exit(1)
    # ordena por id y toma centro de cada marcador
    pts = {}
    for c, i in zip(corners, ids.flatten()):
        pts[int(i)] = c[0].mean(axis=0)
    for need in (10, 11, 12, 13):
        if need not in pts:
            print(f"Falta ArUco id {need}. IDs vistos: {sorted(pts)}")
            sys.exit(1)
    src = np.float32([pts[10], pts[11], pts[12], pts[13]])  # TL,TR,BR,BL
    dst = np.float32([[0, 0], [a.cols, 0], [a.cols, a.rows], [0, a.rows]])
    H, _ = cv2.findHomography(src, dst)
    np.save(a.out, H)
    print(f"OK {a.out} ids={sorted(pts)}")


if __name__ == "__main__":
    main()
