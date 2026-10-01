# 08 — Plan de Pruebas Visión + Grid (multi-entorno + lista escenas)

> Objetivo: probar mucho, barato y repetible. Sin pintar minis nuevas, sin mesa final. Fotos + proyección + scripts.

## 1. Matriz de entornos (probar cada escena aquí)

| ID entorno | Luz | Fondo tablero | Proyector | Cámara |
|---|---|---|---|---|
| E1-mesa-blanca-dia | día ventana | lona blanca mate | apagado | 70cm cenital 1080p |
| E2-mesa-oscura-noche | cálida tenue | madera oscura | grid square tenue 60% | misma |
| E3-proyector-full | noche | blanca | grid + bg escena 100% | misma |
| E4-suelo-prueba | mixta | cartulina gris | hex pointy | móvil trípode |
| E5-estres | baja + sombra mano | cualquiera | parpadeo | misma |

Toda foto/video se guarda como `tests/capturas/{escena}_{entorno}_{fecha}.jpg` + `meta.json {luz, grid, H.npy usado}`.

## 2. Lista de 12 escenas (casos que sí pasan en mesa)

| # | Escena JSON | Grid | Qué prueba | Éxito |
|---|---|---|---|---|
| S01 | `vacia_square` | square 12x9 | cero falsos positivos con grid proyectado | 0 detecciones |
| S02 | `3minis_square` | square | pacto A1,A2,A3 + tracking A1->A2 | 3/3, casillas exactas |
| S03 | `5minis_hex` | hex pointy | hex + oclusión leve (2 pegadas) | 5/5 o 4/5 con flag `pegadas` |
| S04 | `muros_square` | square + 3 muros | `escenografia` no cuenta como pieza, bloquea | muros=3, piezas=N, JEV rechaza cruce |
| S05 | `caida` | square | 1 tumbada 90° | `estado=caido` por ratio>1.2 |
| S06 | `spawn_xeno` | square | 23 slots? prueba con 5 físicas + resto virtual | markers 5, confirma 5 |
| S07 | `spawn_hex_selva` | hex flat | spawn estratégico cerca cobertura | casillas válidas, no sobre muro |
| S08 | `luz_baja` | square | E5 sombra mano 2s | track sobrevive 5 frames |
| S09 | `proyector_fuerte` | square E3 | grid 100% no se detecta como pieza | 0 extras |
| S10 | `doble_altura` | hex | escenografía alta tapa medio mini | flag `ocluida`, no pierde ID |
| S11 | `wargame_1v1` | hex | 2 bandos, rangos iluminados | celdas alcance correctas |
| S12 | `campaña_niebla` | square | fog + `?` overlay | niebla no genera detección |

Cada escena: `scenes/{id}.json {grid, bg, spawns, overlays_intro, esperado:{conteo, casillas}}`.

## 3. Paso a paso para empezar hoy (sin entrenar aún)

**Día 1 — grids en papel y proyector (0 GPU):**

```bash
cd Desktop/TTRPG-AI-DM/grid
python grids.py --tipo square --cols 12 --rows 9 --cell-mm 50 --out patron_square.svg
python grids.py --tipo hex --orientacion pointy --cols 11 --rows 9 --out patron_hex.svg
# proyecta cada SVG fullscreen, mide casilla con regla, ajusta cell_px hasta 50mm reales
# saca 10 fotos tablero vacío E1-E3 (base para dataset sintético)
```

**Día 2 — PNGs + sintético:**

```bash
pip install rembg albumentations opencv-python ultralytics
python ../vision/scripts/cutout.py --in tests/capturas/raw --out tests/pngs
python ../vision/scripts/synth.py --pngs tests/pngs --fondos tests/capturas/E1_E2 --n 200 --grid square,hex --out data/synth
# revisa 20 al azar, deben verse grises de luz + grids tenues
```

**Día 3 — entrena nano y mide:**

```bash
yolo segment train model=yolo11n-seg.pt data=data.yaml epochs=60 imgsz=640
yolo segment val model=runs/segment/train/weights/best.pt
yolo predict model=best.pt source=tests/capturas/S02_E2.jpg save=True
# objetivo MVP: recall>0.9, mAP50_mask>0.8. Si grid se detecta, sube % sintético con grid al 70%.
```

**Día 4 — tracking + homografía:**

```bash
python ../vision/scripts/calibrate.py --foto tests/capturas/aruco.jpg --out H.npy
python ../vision/scripts/track_test.py --video tests/capturas/S02_movimiento.mp4 --grid square --H H.npy
# mueve A1->A2 en video, verifica ID estable + casilla cambia
```

## 4. Métricas por prueba (guardar en `tests/resultados.csv`)

`escena, entorno, grid, esperadas, detectadas, precision, recall, casillas_ok, ids_estables, caido_ok, notas_luz`. No avances a LLM hasta `S01-S05` en verde en E1-E3.

## 5. Estructura que creamos ahora

```
TTRPG-AI-DM/
  grid/grids.py, patron_square.svg, patron_hex.svg, scenes/*.json
  vision/scripts/cutout.py, synth.py, calibrate.py, track_test.py
  tests/capturas/, tests/resultados.csv
  web/table/GridOverlay.tsx (siguiente paso)
```
