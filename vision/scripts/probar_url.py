# probar_url.py — encuentra la URL real de tu teléfono (IP Webcam / DroidCam).
# Uso: python probar_url.py --ip 192.168.1.34
# Prueba los caminos /video /videofeed /shot.jpg y te dice cuál abre en OpenCV.
import argparse
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("--ip", required=True, help="la IP que muestra la app en tu teléfono, ej 192.168.1.34")
ap.add_argument("--puerto", default="8080")
a = ap.parse_args()

candidatas = [
    f"http://{a.ip}:{a.puerto}/video",
    f"http://{a.ip}:{a.puerto}/videofeed",
    f"http://{a.ip}:{a.puerto}/shot.jpg",
    f"http://{a.ip}:{a.puerto}:4747/video",  # DroidCam por defecto usa 4747
]
for url in candidatas:
    cap = cv2.VideoCapture(url)
    ok, frame = cap.read() if cap.isOpened() else (False, None)
    print(("ABRE  " if ok and frame is not None else "falla") + f"  {url}")
    cap.release()
print("Si alguna dice ABRE, úsala así:")
print('python vision/scripts/grid_cam.py --url "URL_QUE_ABRE" --cols 4 --rows 4')
