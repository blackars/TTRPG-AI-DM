# detect_live.py — YOLO-seg en vivo: siluetas -> celdas del grid (reemplaza al detector por movimiento).
# Usa best.pt del entreno Colab. Sin best.pt avisa y sale (primero entrena).
# Foto quieta:  python detect_live.py --foto ruta.jpg --weights vision/weights/best.pt
# En vivo:      python detect_live.py --url http://192.168.1.14:8080/video --weights vision/weights/best.pt
import argparse
from pathlib import Path

import cv2
import numpy as np


def nombre_cuadro(c, r):
    return f"{chr(65 + c)}{r + 1}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--foto", default=None)
    ap.add_argument("--url", default=None)
    ap.add_argument("--cam", type=int, default=0)
    ap.add_argument("--weights", default="vision/weights/best.pt")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--rows", type=int, default=4)
    ap.add_argument("--conf", type=float, default=0.35)
    a = ap.parse_args()

    try:
        from ultralytics import YOLO
    except ImportError:
        print("Falta ultralytics: pip install ultralytics (o corre esto en Colab).")
        raise SystemExit(1)
    if not Path(a.weights).exists():
        print(f"No existe {a.weights}. Descarga best.pt de Colab a vision/weights/ primero.")
        raise SystemExit(1)
    model = YOLO(a.weights)
    print(f"Modelo: {a.weights} | grid {a.cols}x{a.rows} | conf {a.conf}")

    def procesar(frame):
        h, w = frame.shape[:2]
        cw, rh = w // a.cols, h // a.rows
        res = model.predict(frame, conf=a.conf, verbose=False)[0]
        celdas = []
        if res.masks is not None:
            for poly in res.masks.xy:
                cx, cy = float(poly[:, 0].mean()), float(poly[:, 1].mean())
                col = min(a.cols - 1, max(0, int(cx // cw)))
                fil = min(a.rows - 1, max(0, int(cy // rh)))
                celda = nombre_cuadro(col, fil)
                celdas.append(celda)
                pts = poly.astype(int)
                cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
                cv2.circle(frame, (int(cx), int(cy)), 8, (0, 255, 0), -1)
                cv2.putText(frame, celda, (int(cx) + 10, int(cy)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        for i in range(a.cols + 1):
            cv2.line(frame, (i * cw, 0), (i * cw, h), (255, 255, 255), 1)
        for j in range(a.rows + 1):
            cv2.line(frame, (0, j * rh), (w, j * rh), (255, 255, 255), 1)
        return frame, sorted(set(celdas))

    if a.foto:
        frame = cv2.imread(a.foto)
        assert frame is not None, f"no leo {a.foto}"
        frame, celdas = procesar(frame)
        print("Celdas con mini:", ", ".join(celdas) if celdas else "ninguna")
        cv2.imwrite("deteccion_prueba.jpg", frame)
        print("Anotada en deteccion_prueba.jpg")
        return

    fuente = a.url if a.url else a.cam
    cam = cv2.VideoCapture(fuente)
    assert cam.isOpened(), f"no abre {fuente}"
    print("Q = salir | G = guardar")
    while True:
        ok, frame = cam.read()
        if not ok:
            continue
        frame, celdas = procesar(frame)
        cv2.putText(frame, f"Celdas: {' '.join(celdas) if celdas else '---'}", (12, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
        try:
            cv2.imshow("YOLO-seg en vivo (Q salir, G guardar)", frame)
        except cv2.error:
            print("Sin ventanas. Celdas:", celdas)
            continue
        k = cv2.waitKey(30) & 0xFF
        if k in (ord("q"), ord("Q")):
            break
        if k in (ord("g"), ord("G")):
            import datetime
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            cv2.imwrite(f"tests/capturas/yolo_vivo_{ts}.jpg", frame)
            print("Guardada + celdas:", celdas)
    cam.release()
    try:
        cv2.destroyAllWindows()
    except cv2.error:
        pass


if __name__ == "__main__":
    main()
