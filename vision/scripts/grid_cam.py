# grid_cam.py — prueba del grid SOBRE tu webcam (sin impresora ni proyector).
# IDEA CLAVE: el grid NO es una casilla física donde debe caber la mini.
# Es un sistema de coordenadas: solo importa el CENTRO (punto medio) de la mini.
# Aunque la mini toque 4 cuadros, el sistema dice "está en B2" porque su centro cayó en B2.
# Para pruebas usa grid CHICO (4x4). El 9x9 queda guardado para tableros grandes después.
# Controles: Q = salir. G = guardar foto. + = más sensible. - = menos sensible.
# Uso: python grid_cam.py  (prueba chica 4x4)
#      python grid_cam.py --cols 9 --rows 9  (tablero grande, solo cuando la cámara vea de lejos y nítido)
#      python grid_cam.py --cam 1  (si tu webcam es la 1)
import argparse
import cv2
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("cam_pos", nargs="?", default=None, help="índice de cámara (0 o 1), forma vieja")
ap.add_argument("--cols", type=int, default=4, help="columnas del grid de prueba (default 4, grande 9)")
ap.add_argument("--rows", type=int, default=4, help="filas del grid de prueba (default 4, grande 9)")
ap.add_argument("--cam", type=int, default=0, help="índice de cámara")
ap.add_argument("--url", default=None, help="URL MJPEG del teléfono, ej http://192.168.1.50:8080/video")
ap.add_argument("--area", type=int, default=1200, help="tamaño mínimo para detectar (800 de lejos, 2000 de cerca)")
ap.add_argument("--minis", type=int, default=3, help="cuántas minis seguir máximo en vivo (default 3)")
ap.add_argument("--no-ver", action="store_true", help="sin ventana: imprime detecciones y guarda foto cada 5s (por si OpenCV no tiene GUI)")
a = ap.parse_args()
if a.cam_pos is not None and a.cam_pos.isdigit():
    a.cam = int(a.cam_pos)

COLS, ROWS = a.cols, a.rows
AREA_MIN = a.area
MAX_MINIS = a.minis

def nombre_cuadro(c, r):
    return f"{chr(65 + c)}{r + 1}"

fuente = a.url if a.url else a.cam
cam = cv2.VideoCapture(fuente)
if not cam.isOpened():
    print(f"ERROR: no abre {fuente}.")
    print("1. Esa IP era un EJEMPLO. Lee en tu teléfono la IP real que muestra la app (ej 192.168.1.34).")
    print("2. Prueba primero en el navegador del PC: http://TU_IP:8080  (debe abrir la página de la app).")
    print("3. Si el navegador no abre: no es el mismo WiFi, o el firewall bloquea. Acerca el teléfono al router.")
    print('4. Encuentra el camino bueno con: python vision/scripts/probar_url.py --ip TU_IP')
    raise SystemExit(1)

fondo = cv2.createBackgroundSubtractorMOG2(history=150, varThreshold=25)
print(f"=== PRUEBA GRID {COLS}x{ROWS} ===")
print("REGLA: solo importa el CENTRO (punto) de la mini, aunque toque varios cuadros.")
print("POR QUE SE BORRA AL SEGUNDO: el detector aprende el fondo. Si dejas la mini quieta,")
print("cree que ya es parte de la mesa y deja de marcarla. Es normal, no es tu cámara.")
print("ARREGLO: ahora la marca queda CONGELADA 4 segundos aunque la dejes quieta.")
print("1. Pon 1 minito a 40-60cm de la webcam.")
print("2. Mueve el minito de cuadro. El punto del centro decide el nombre (ej A1 -> B1).")
print("3. Acuesta el minito (volteado). Debe ponerse ROJO y decir caido.")
print("Q salir | G guardar | + mas sensible | - menos sensible | R reiniciar fondo")
area_min = AREA_MIN
# Memoria: guarda las últimas detecciones para que no se borren al quedar quietas.
ultima = {"minis": [], "quieto": 0}
LATCH_FRAMES = 120  # ~4 segundos a 30fps

while True:
    ok, frame = cam.read()
    if not ok:
        break
    h, w = frame.shape[:2]
    cw, rh = w // COLS, h // ROWS

    # Medidor de nitidez: si sale menos de 50, la foto está borrosa (enfoque o poca luz).
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    nitidez = cv2.Laplacian(gris, cv2.CV_64F).var()

    # movimiento = silueta de tu mini / mano
    mask = fondo.apply(frame)
    _, mask = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    mejor = None
    # En vivo buscamos hasta MAX_MINIS manchas grandes (no solo 1).
    candidatas = []
    for c in cnts:
        ar = cv2.contourArea(c)
        if ar > area_min:
            candidatas.append((ar, c))
    candidatas = sorted(candidatas, key=lambda t: t[0], reverse=True)[:MAX_MINIS]

    vivas = []  # lista de (celda, estado, box, centro)
    for _, c in candidatas:
        x, y, bw, bh = cv2.boundingRect(c)
        cx, cy = x + bw // 2, y + bh // 2
        col = min(COLS - 1, max(0, cx // cw))
        fil = min(ROWS - 1, max(0, cy // rh))
        celda_txt = nombre_cuadro(col, fil)
        estado = "caido" if bw / max(bh, 1) > 1.2 else "de_pie"
        vivas.append((celda_txt, estado, (x, y, bw, bh), (cx, cy)))

    if vivas:
        # guarda en memoria para que no se borre al quedar quietas 4 seg
        ultima = {"minis": vivas, "quieto": 0}
        mostrar = [(c, e + "", b, p) for c, e, b, p in vivas]
        etiqueta = ", ".join(f"{c} {e}" for c, e, _, _ in vivas)
    else:
        # Sin movimiento: muestra las últimas 4 segundos con aviso "quieto"
        if ultima.get("minis") and ultima["quieto"] < LATCH_FRAMES:
            ultima["quieto"] += 1
            mostrar = [(c, e + " (quieto)", b, p) for c, e, b, p in ultima["minis"]]
            etiqueta = ", ".join(f"{c} {e}" for c, e, _, _ in mostrar)
        else:
            ultima = {"minis": [], "quieto": 0}
            mostrar = []
            etiqueta = "---"

    for celda_txt, estado, box, centro in mostrar:
        x, y, bw, bh = box
        color = (0, 0, 255) if "caido" in estado else (0, 255, 0)
        cv2.rectangle(frame, (x, y), (x + bw, y + bh), color, 3)
        if centro is not None:
            cv2.circle(frame, centro, 8, color, -1)
        cv2.putText(frame, celda_txt, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    celda_txt, estado = etiqueta, f"{len(mostrar)} mini(s)"

    # dibuja grid
    for c in range(COLS + 1):
        cv2.line(frame, (c * cw, 0), (c * cw, h), (255, 255, 255), 1)
    for r in range(ROWS + 1):
        cv2.line(frame, (0, r * rh), (w, r * rh), (255, 255, 255), 1)
    for c in range(COLS):
        for r in range(ROWS):
            cv2.putText(frame, nombre_cuadro(c, r), (c * cw + 6, r * rh + 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.rectangle(frame, (0, 0), (w, 94), (0, 0, 0), -1)
    aviso = "BORROSA - acerca o pon mas luz" if nitidez < 50 else "nítida OK"
    cv2.putText(frame, f"Cuadro: {celda_txt}  Estado: {estado}  sens:{area_min}", (12, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.putText(frame, f"Nitidez: {nitidez:.0f} ({aviso})", (12, 58),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255) if nitidez < 50 else (0, 255, 0), 2)
    cv2.putText(frame, "Q salir | G guardar | + mas | - menos | R fondo", (12, 84),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    try:
        if not a.no_ver:
            cv2.imshow(f"PRUEBA grid {COLS}x{ROWS} (Q salir, G guardar, +/- sens)", frame)
    except cv2.error:
        print("AVISO: OpenCV sin ventanas en este PC. Activo modo --no-ver (solo texto + fotos).")
        a.no_ver = True
    if a.no_ver:
        import time as _t
        if int(_t.time()) % 5 == 0:
            from pathlib import Path as _P
            _out = _P(__file__).resolve().parents[2] / "tests" / "capturas" / "grid_nover.jpg"
            cv2.imwrite(str(_out), frame)
            print(f"[{etiqueta}] foto en {_out}")
            _t.sleep(1.1)
        continue
    k = cv2.waitKey(30) & 0xFF
    if k in (ord("q"), ord("Q")):
        break
    if k in (ord("+"), ord("=")):
        area_min = max(200, area_min - 200)
        print(f"Sensibilidad: ahora detecta desde {area_min} pixeles (mas sensible)")
    if k in (ord("-"), ord("_")):
        area_min = min(5000, area_min + 200)
        print(f"Sensibilidad: ahora detecta desde {area_min} pixeles (menos sensible)")
    if k in (ord("r"), ord("R")):
        fondo = cv2.createBackgroundSubtractorMOG2(history=150, varThreshold=25)
        ultima = {"minis": [], "quieto": 0}
        print("Fondo reiniciado: quita las minis 2 segundos y vuelve a ponerlas.")
    if k in (ord("g"), ord("G")):
        from pathlib import Path
        import datetime
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out = Path(__file__).resolve().parents[2] / "tests" / "capturas" / f"prueba_grid_{ts}.jpg"
        cv2.imwrite(str(out), frame)
        print(f"Foto guardada: {out} -> {celda_txt} {estado}")

cam.release()
cv2.destroyAllWindows()
