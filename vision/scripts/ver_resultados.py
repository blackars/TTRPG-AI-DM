# ver_resultados.py — abre en ventanas lo que el modelo ve (anotadas + muestras).
# Uso: python ver_resultados.py
# Teclas: N siguiente, P anterior, Q salir. Rueda/ventana redimensionable.
import cv2
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
FOTOS = [
    ("LO QUE VE EL V2 (solo 2 azules 0.20)", BASE / "tests/sesion1/v2_conf005.jpg"),
    ("V2 a 1280px (igual, no es resolucion)", BASE / "tests/sesion1/v2_1280_conf01.jpg"),
    ("V1 en 6 minis (inunda el fondo)", BASE / "tests/sesion1/v2_6minis_anotada.jpg"),
    ("Lote 2b: caos verificado", BASE / "data/synth_lote2/images/syn_1400.jpg"),
    ("Foto real dorada 6 minis", BASE / "dataset/frames_phone/cenital_batalla_f0020.jpg"),
]

imgs = [(t, cv2.imread(str(p))) for t, p in FOTOS if p.exists()]
faltan = [str(p) for _, p in FOTOS if not p.exists()]
for f in faltan:
    print("Falta:", f)
if not imgs:
    print("No hay imágenes. Revisa las rutas de arriba.")
    raise SystemExit(1)

try:
    cv2.namedWindow("RESULTADOS", cv2.WINDOW_NORMAL)
except cv2.error:
    print("Sin ventanas en este OpenCV. Abre a mano:")
    for t, p in FOTOS:
        print(" ", p)
    raise SystemExit(1)

i = 0
while True:
    titulo, img = imgs[i]
    h, w = img.shape[:2]
    k = min(1.0, 1000 / max(h, w))
    if k < 1.0:
        img = cv2.resize(img, (int(w * k), int(h * k)))
    cv2.setWindowTitle("RESULTADOS", f"[{i + 1}/{len(imgs)}] {titulo}  (N sig, P ant, Q salir)")
    cv2.imshow("RESULTADOS", img)
    c = cv2.waitKey(0) & 0xFF
    if c in (ord("q"), ord("Q"), 27):
        break
    if c in (ord("n"), ord("N"), 83):
        i = (i + 1) % len(imgs)
    else:
        i = (i - 1) % len(imgs)
cv2.destroyAllWindows()
