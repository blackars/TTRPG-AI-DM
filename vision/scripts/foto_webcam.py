# foto_webcam.py — tomar fotos con webcam o con el TELÉFONO como webcam.
# Webcam vieja:  python foto_webcam.py
# Teléfono (app IP Webcam / DroidCam con URL):  python foto_webcam.py --url http://192.168.1.50:8080/video
# Guarda en: tests/capturas/webcam_foto_01.jpg, _02, etc. ESPACIO guarda, Q sale.
import argparse
import cv2
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("cam_pos", nargs="?", default=None)
ap.add_argument("--cam", type=int, default=0)
ap.add_argument("--url", default=None, help="URL MJPEG del teléfono, ej http://192.168.1.50:8080/video")
a = ap.parse_args()
if a.cam_pos is not None and a.cam_pos.isdigit():
    a.cam = int(a.cam_pos)

salida = Path(__file__).resolve().parents[2] / "tests" / "capturas"
salida.mkdir(parents=True, exist_ok=True)

fuente = a.url if a.url else a.cam
cam = cv2.VideoCapture(fuente)
if not cam.isOpened():
    print(f"ERROR: no se pudo abrir {fuente}.")
    print("Webcam: prueba --cam 1. Teléfono: revisa que estén en el mismo WiFi y la URL /video.")
    raise SystemExit(1)

print("=== DÍA 1 ===")
print("Mira la ventana. Pulsa ESPACIO para guardar foto, Q para salir.")
print(f"Se guardan en: {salida}")
n = 0
while True:
    ok, frame = cam.read()
    if not ok:
        print("ERROR: la cámara no entrega imagen.")
        break
    cv2.imshow("DIA 1 - pulsa ESPACIO para foto, Q para salir", frame)
    k = cv2.waitKey(30) & 0xFF
    if k == 32:  # espacio
        n += 1
        ruta = salida / f"webcam_foto_{n:02d}.jpg"
        cv2.imwrite(str(ruta), frame)
        print(f"Guardada {ruta} ({n}/10)")
        if n >= 10:
            print("Listo: ya tienes 10. Pulsa Q para salir.")
    if k in (ord("q"), ord("Q")):
        break
cam.release()
cv2.destroyAllWindows()
print(f"Total fotos: {n}")
