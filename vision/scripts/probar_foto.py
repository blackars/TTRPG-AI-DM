# probar_foto.py — prueba una FOTO quieta (tus fotos de estudio) con grid 4x4.
# A diferencia de grid_cam.py (que solo ve MOVIMIENTO), este busca la mini por CONTRASTE,
# así no se borra al segundo. Ideal para tus fotos de estudio con mini de color.
# Uso: python probar_foto.py "C:\ruta\a\tu_foto.jpg"
#      python probar_foto.py --todas  (prueba todas las de tests/capturas y te dice nitidez)
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np


def nombre_cuadro(c, r):
    return f"{chr(65 + c)}{r + 1}"


def nitidez(img):
    return cv2.Laplacian(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()


def detectar_por_contraste(frame, max_minis=3, area_min=800):
    """Busca hasta max_minis manchas distintas del fondo (sirve en foto quieta)."""
    blur = cv2.GaussianBlur(frame, (7, 7), 0)
    # fondo negro/verde: la mini (gris o color) se separa por brillo+contraste
    _, th = cv2.threshold(cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY), 0, 255,
                          cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return []
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    h, w = frame.shape[:2]
    out = []
    for c in cnts:
        a = cv2.contourArea(c)
        if a > 0.9 * w * h or a < area_min:
            continue
        out.append(c)
        if len(out) >= max_minis:
            break
    return out


def procesar(ruta, cols=4, rows=4, mostrar=True, max_minis=3):
    frame = cv2.imread(str(ruta))
    if frame is None:
        print(f"No pude leer {ruta}")
        return None
    h, w = frame.shape[:2]
    cw, rh = w // cols, h // rows
    n = nitidez(frame)
    detecciones = detectar_por_contraste(frame, max_minis=max_minis)
    resultados = []
    for c in detecciones:
        x, y, bw, bh = cv2.boundingRect(c)
        cx, cy = x + bw // 2, y + bh // 2
        celda = nombre_cuadro(min(cols - 1, max(0, cx // cw)), min(rows - 1, max(0, cy // rh)))
        estado = "caido" if bw / max(bh, 1) > 1.2 else "de_pie"
        color = (0, 0, 255) if estado == "caido" else (0, 255, 0)
        cv2.drawContours(frame, [c], -1, color, 3)
        cv2.circle(frame, (cx, cy), 8, color, -1)
        cv2.putText(frame, celda, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        resultados.append({"celda": celda, "estado": estado})
    if not resultados:
        print(f"{Path(ruta).name}: nitidez={n:.0f} ({'OK' if n >= 50 else 'BORROSA'}) -> ninguna vista")
    else:
        txt = ", ".join(f"{r['celda']} {r['estado']}" for r in resultados)
        print(f"{Path(ruta).name}: nitidez={n:.0f} ({'OK' if n >= 50 else 'BORROSA'}) -> {len(resultados)} mini(s): {txt}")
    for i in range(cols + 1):
        cv2.line(frame, (i * cw, 0), (i * cw, h), (255, 255, 255), 1)
    for j in range(rows + 1):
        cv2.line(frame, (0, j * rh), (w, j * rh), (255, 255, 255), 1)
    titulo = f"{len(resultados)} minis" if resultados else "ninguna"
    if mostrar:
        cv2.imshow(f"{titulo} - Q para cerrar", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return {"archivo": str(ruta), "nitidez": n, "minis": resultados}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("foto", nargs="?", default=None)
    ap.add_argument("--todas", action="store_true")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--rows", type=int, default=4)
    ap.add_argument("--minis", type=int, default=3, help="cuántas minis buscar máximo (default 3)")
    ap.add_argument("--no-ver", action="store_true")
    a = ap.parse_args()
    base = Path(__file__).resolve().parents[2] / "tests" / "capturas"
    if a.todas:
        fotos = sorted(base.glob("webcam_foto_*.jpg"))
        for f in fotos:
            procesar(f, a.cols, a.rows, mostrar=not a.no_ver, max_minis=a.minis)
    elif a.foto:
        procesar(a.foto, a.cols, a.rows, mostrar=not a.no_ver, max_minis=a.minis)
    else:
        print('Uso: python probar_foto.py "C:\\ruta\\foto.jpg"  o  python probar_foto.py --todas --no-ver')
        sys.exit(1)
