# grabar_video.py — graba videos cortos con webcam o con el TELÉFONO.
# Webcam:  python grabar_video.py --nombre mover_A1_C3 --seg 20
# Teléfono: python grabar_video.py --url http://192.168.1.14:8080/video --nombre mover_phone --seg 20
# Controles: se graba solo, Q = terminar antes. Guarda en tests/sesion1/videos/
import argparse
from pathlib import Path

import cv2

ap = argparse.ArgumentParser()
ap.add_argument("--nombre", default="video_prueba")
ap.add_argument("--seg", type=int, default=20)
ap.add_argument("--cam", type=int, default=0)
ap.add_argument("--url", default=None, help="URL MJPEG del teléfono, ej http://192.168.1.14:8080/video")
ap.add_argument("--no-ver", action="store_true", help="graba a ciegas sin ventana (si OpenCV no tiene GUI)")
a = ap.parse_args()

out_dir = Path(__file__).resolve().parents[2] / "tests" / "sesion1" / "videos"
out_dir.mkdir(parents=True, exist_ok=True)
ruta = out_dir / f"{a.nombre}.mp4"

fuente = a.url if a.url else a.cam
cam = cv2.VideoCapture(fuente)
if not cam.isOpened():
    print(f"ERROR: no abre {fuente}. Webcam: --cam 1. Teléfono: revisa IP + mismo WiFi.")
    raise SystemExit(1)

w = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
h = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
vw = cv2.VideoWriter(str(ruta), cv2.VideoWriter_fourcc(*"mp4v"), 20.0, (w, h))
print(f"Grabando {a.seg}s en {ruta}. Q = terminar antes.")
ver = not a.no_ver
import time
t0 = time.time()
nframes = 0
while True:
    ok, frame = cam.read()
    if not ok:
        # reintenta 1 vez (red WiFi inestable)
        ok, frame = cam.read()
        if not ok:
            print("AVISO: frame perdido, sigo...")
            continue
    vw.write(frame)
    nframes += 1
    if ver:
        try:
            cv2.imshow("Grabando - Q para terminar", frame)
        except cv2.error:
            print("AVISO: sin ventanas, sigo grabando a ciegas.")
            ver = False
    if ver and (cv2.waitKey(30) & 0xFF) in (ord("q"), ord("Q")):
        break
    if time.time() - t0 > a.seg:
        break
cam.release()
vw.release()
try:
    cv2.destroyAllWindows()
except cv2.error:
    pass
print(f"Listo: {ruta} ({nframes} frames)")
