# gen_manifest.py — genera tests/sesion1/manifest.csv (una fila por foto).
# Uso: python gen_manifest.py
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from probar_foto import nitidez
import cv2

base = Path(__file__).resolve().parents[2] / "tests" / "sesion1"
rows = []

for f in sorted((base / "studio_celu").glob("*.*")):
    if f.suffix.lower() not in (".jpg", ".jpeg", ".png"):
        continue
    img = cv2.imread(str(f))
    n = round(float(nitidez(img)), 1) if img is not None else -1
    # Estudio: el medidor miente con fondos lisos (blanco/negro) y plástico liso.
    # Solo se marca REPETIR si ni siquiera se puede leer. Veredicto visual manda.
    sirve, nota = ("SI", "estudio celu, recorte/entrenar") if img is not None else ("REPETIR", "no se lee el archivo")
    rows.append([str(f.relative_to(base)), f.name, "estudio", "studio",
                 "n/a", "SI", n, sirve, "recorte/entrenar", nota])

for f in sorted((base / "tablero_webcam").glob("*.jpg")):
    name = f.name.lower()
    tiene = "SI" if ("conminito" in name or "depie" in name or "caido" in name or "caida" in name) else "NO"
    if name.startswith("vacia") or name.startswith("vacio"):
        tiene = "NO"
    # Luz = PRIMER token del nombre (vacia_X, blanca_..., conminito_calida_...).
    # Así los colores de minis (azul_roja_...) no se confunden con luz RGB.
    toks = name.replace(".jpg", "").split("_")
    luz = "blanca"
    primero = toks[0]
    if primero in ("azul", "rojo", "verde", "calida", "calido", "blanca", "vacia", "vacio"):
        luz = primero
    elif primero == "conminito" and len(toks) > 1 and toks[1] in ("azul", "rojo", "verde", "calida", "calido", "blanca"):
        luz = toks[1]
    elif primero == "photo":
        luz = "blanca"
    pos = "centro"
    for cand in ["izquierda", "derecha", "arriba", "abajo", "centro", "esquina"]:
        if cand in name:
            pos = cand
            break
    estado = "caido" if "caido" in name else ("depie" if tiene == "SI" else "vacio")
    img = cv2.imread(str(f))
    n = round(float(nitidez(img)), 1) if img is not None else -1
    if tiene == "NO":
        uso, sirve, nota = "fondo", "SI", "fondo tablero vacio"
        if "azul" in name and n < 8:
            sirve, nota = "PARCIAL", "azul casi negro, solo ejemplo de luz mala"
    else:
        if luz in ("azul", "rojo", "verde"):
            uso, sirve = "test-luz", "PARCIAL"
            nota = "mini casi invisible con RGB, caso dificil a futuro"
        else:
            uso, sirve = "entrenar/test", "SI"
            nota = "ejemplo real webcam aunque borrosa, YOLO la necesita"
    canon = "sesion1_" + luz + "_" + pos + "_" + estado + ".jpg"
    rows.append([str(f.relative_to(base)), f.name, "tablero", luz,
                 pos, tiene, n, sirve, uso, nota + " | canon:" + canon])

out = base / "manifest.csv"
with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["ruta", "original", "set", "luz", "posicion",
                "tiene_mini", "nitidez", "sirve", "uso", "nota"])
    w.writerows(rows)

from collections import Counter
print("filas:", len(rows))
print(Counter([r[7] for r in rows]))
print("OK", out)
