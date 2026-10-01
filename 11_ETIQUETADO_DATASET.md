# 11 — Etiquetado y dataset acumulativo (sesión 1 medida)

Inventario real en `tests/sesion1/manifest.csv`: **65 fotos** (15 estudio + 50 tablero).
Medidas con nitidez + detección: **51 sirven (SI), 13 parcial, 1 repetir**.

## Esquema de nombres (usa este de ahora en adelante)

`{luz}_{posicion}_{estado}_{nn}.jpg` todo minúscula, sin typos. Ej: `calida_centro_caido_01.jpg`.

- luz: `blanca | calida | azul | rojo | verde | studio`
- posición: `centro | izquierda | derecha | arriba | abajo | esquina`
- estado: `depie | caido | vacio`
- `conminito_` al inicio sobra: si estado es vacio = no hay mini, si no = sí hay.

Typos que vi y ya normalizo en el manifest (columna canon): `cderecha→derecha`, `derech→derecha`, `depie` unificado, `Calido3→calido3`.

## Qué sirve y para qué (veredicto por grupo)

| Grupo | Nitidez real | ¿Sirve? | Uso |
|---|---|---|---|
| Studio celu (8 cenital/caído + 7 frontal/lateral, 12MP) | 25-84, una en 8 | SI (14/15) | Recorte PNG + entrenar YOLO. La joya es `cenital_frontal.jpg` (68, nítida, grande). |
| `frontal3.JPG` | 8 | REPETIR | Movida, repite solo esa toma. |
| Tablero cálida/blanca con mini (20 fotos) | 14-30 | SI | Entrenar/test real webcam. Borrosas pero YOLO las necesita tal cual se verá jugando. |
| Tablero vacía blanca/cálida (12 fotos) | 10-28 | SI | Fondos para `synth.py` (pegar PNGs encima). No necesitan nitidez alta. |
| Tablero azul/rojo/verde (18 fotos) | 4-20, azul 4-6 | PARCIAL | Mini casi invisible (azul = negro total). Guárdalas como casos difíciles a futuro, NO para entrenar ahora. |
| Vacías que el detector marca con minis | — | SI como fondo | Prueba de que el método por contraste falla en tablero texturizado (detecta cráteres/brillos). Justifica ir a YOLO. |

## El esfuerzo extra SÍ se reutiliza

Todo lo que guardes con nombre bueno + fila en el manifest se suma al dataset:
- `dataset/fondos/` ← vacías (las 12 + las que traigas).
- `dataset/images/` + `dataset/labels/` ← con mini (etiqueta YOLO-seg se genera con `synth.py` + corrección).
- Casos RGB difíciles ← se guardan aparte y se mezclan al final (10-20% del total), no al inicio.

Regla a futuro: cada tanda nueva corre `python vision/scripts/gen_manifest.py` y se agrega al CSV. Nunca borres fotos, ni las borrosas: el modelo debe ver blur real.

## Videos: ¿grabo o no?

- SÍ graba los 3 de luz blanca/cálida (mover, poner/quitar, acostar). Esos alimentan tracking + frames extra.
- NO grabes en azul/rojo todavía: sale negro total (nitidez 4-6), no aporta nada hasta tener más luz o el celular como cámara.
- Comando: `python vision/scripts/grabar_video.py --nombre mover_A1_C3 --seg 20`
