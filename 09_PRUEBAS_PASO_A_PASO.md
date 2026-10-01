# 09 — Pruebas de visión + grid, explicado sin tecnicismos

## Qué es cada cosa (en una línea)

- **YOLO segmentación:** un programa que mira la foto de tu mesa y recorta las siluetas. No sabe si es orco o mago, solo dice "aquí hay una pieza". Eso es todo.
- **Grid cuadrado:** la rejilla típica de cuadros como ajedrez. Cada cuadro se llama A1, A2, B1...
- **Grid hexagonal:** rejilla de hexágonos (6 lados) como juegos de guerra. Cada hexágono se llama 03.04, etc. Sirve para medir distancias sin trampas en diagonal.
- **Homografía / ArUco:** 4 stickers cuadrados impresos que pegas en las esquinas de la mesa. La cámara los busca para saber dónde empieza y termina el tablero. Sin esto, la cámara no sabe qué cuadro es cuál.
- **Escena:** una foto o configuración de prueba. Ej: "3 minis en cuadros + luz de día".
- **SVG:** el dibujo del grid que ve el proyector. Es un archivo de texto que el navegador dibuja como líneas. Las animaciones son solo parpadeo (círculo que late, flecha punteada que se mueve).

## Qué archivos ya tienes y para qué sirven

- `grid/grids.py` = genera los dibujos. Ya generé 3 para ti: `patron_square.svg`, `patron_hex_pointy.svg`, `patron_hex_flat.svg`.
- `grid/scenes/S01...S12.json` = las 12 escenas a probar (vacía, 3 minis, muros, caída, etc).
- `vision/scripts/cutout.py` = quita el fondo negro de tus fotos de minis.
- `vision/scripts/synth.py` = pega tus minis sobre fotos de tu mesa para crear 200 fotos falsas para entrenar. Así no tomas 200 fotos reales.
- `vision/scripts/calibrate.py` = con 1 foto de los 4 stickers calcula dónde está cada cuadro.
- `vision/scripts/track_test.py` = con 1 video prueba si la cámara sigue una mini de A1 a A2.
- `web/table/GridOverlay.tsx` = el dibujo que verá el proyector (cuadros o hexágonos + círculos + flechas).
- `dm/decide_ejemplo.py` = ejemplo de decisión rápida sin LLM.

## Paso a paso para esta semana (hazlo en orden)

### Día 1 — Proyecta y mide (sin instalar nada raro, 1 hora)
1. Abre `grid/patron_square.svg` en Chrome, ponlo en pantalla completa en el proyector.
2. Mide un cuadro con una regla. Debe medir 50mm. Si mide 40mm, abre `grids.py` y sube `--cell-px` de 60 a 75 y genera de nuevo:
   `python grid/grids.py --tipo square --cols 12 --rows 9 --cell-px 75 --out grid/patron_square.svg`
3. Haz lo mismo con `patron_hex_pointy.svg`.
4. Toma 10 fotos con tu webcam desde arriba: 5 con proyector apagado, 5 con grid encendido. Guárdalas en `tests/capturas/`. Esos son tus fondos.

### Día 2 — Recorta tus minis (30 min)
1. Pon 1 mini sobre tela negra, tómale 5 fotos (frente, lado, arriba).
2. Corre: `python vision/scripts/cutout.py --in tests/capturas/raw --out tests/pngs`
3. Te deja `mago.png`, `orco.png` sin fondo. Revisa que no tengan halo negro.

### Día 3 — Crea fotos falsas y entrena (2 horas, 1 comando largo)
1. Corre: `python vision/scripts/synth.py --pngs tests/pngs --fondos tests/capturas --n 200 --out data/synth`
2. Te crea 200 fotos + etiquetas. Abre 5 al azar, deben verse tus minis sobre tu mesa.
3. Entrena el nano:
   `yolo segment train model=yolo11n-seg.pt data=data.yaml epochs=60 imgsz=640`
   Si no tienes GPU, usa Google Colab gratis y sube `data/synth`.
4. Prueba: `yolo predict model=best.pt source=tests/capturas/tu_foto_con_3_minis.jpg save=True`
   Éxito = recuadra las 3. Si recuadra el grid, repite synth con más fotos con grid encendido.

### Día 4 — Los 4 stickers (calibración, 20 min)
1. Imprime 4 ArUco (id 10,11,12,13 de https://chev.me/arucogen/) en papel mate, 5x5cm. Pégalos en las 4 esquinas.
2. Toma 1 foto desde tu webcam fija. Corre:
   `python vision/scripts/calibrate.py --foto tests/capturas/aruco.jpg --out H.npy`
3. Ese `H.npy` es tu traductor "píxel -> cuadro". No lo borres. Si mueves la cámara, repite.

### Día 5 — Video moviendo (tracking)
1. Graba 20 segundos moviendo 1 mini de A1 a A2.
2. Corre: `python vision/scripts/track_test.py --video tests/capturas/mov.mp4 --H H.npy --grid square`
3. Debe decir `A1 -> A2` y `de_pie`. Tumba la mini, debe decir `caido`.

## Los 2 grids: qué probar de cada uno

- **Cuadrado:** prueba S01 (vacía, debe dar 0), S02 (3 minis, debe dar 3/3), S04 (muros, no debe contar muros como minis), S05 (tumbada = caído).
- **Hexagonal:** prueba S03 (5 minis), S07 (spawn en selva), S11 (1 vs 1). Usa `patron_hex_pointy.svg` para pasillos verticales, `flat` para horizontales.

Si el cuadrado falla con luz fuerte pero el hex funciona, no es el grid, es la luz. Cambia de entorno (E1 día, E2 noche, E3 proyector full) y anota en `tests/resultados.csv`.

## Qué necesitas para dibujar y animar (recursos)

- Para el proyector: solo Chrome + `GridOverlay.tsx`. Ya trae 3 animaciones con puro CSS: `pulse` (círculo que late para spawn), `dash` (flecha punteada que camina), `niebla` (cuadro negro para esconder). No necesitas librerías.
- Si quieres librería: `hex-grid-kit` (gratis, MIT) ya hace hexágonos + clic. Solo si no quieres usar mi `grids.py`.
- Para Python: `opencv-python` (ver stickers y traducir a cuadros) + `albumentations` (hacer fotos falsas). Ambos gratis.
- Escenas + animaciones se conectan así en `grid/scenes/*.json`: `grid (cuál) + bg (foto tenue) + spawns (dónde late) + overlays (flecha/círculo)`. El proyector lee ese JSON y dibuja.

## Lista de escenas que ya tienes (no las borres)

S01 vacía / S02 3 minis cuadrado / S03 5 hex / S04 muros / S05 caída / S06 spawn xeno / S07 spawn selva hex / S08 luz baja / S09 proyector fuerte / S10 doble altura / S11 guerra 1v1 / S12 niebla campaña. Detalle de cada una en `08_VISION_TEST_PLAN.md`.
