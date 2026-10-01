# 10 — Plan desde cero (previo a YOLO). Mini a color + Kill Team + luz RGB.

> Esto NO es YOLO todavía. Es el previo para probar que el grid entiende dónde está cada mini.
> Cuando esto salga 8 de 10 veces, vamos a YOLO. Todo verificado, scripts compilan OK.

## Tus carpetas nuevas (usa SOLO estas, olvida las 22 viejas)

- `tests/sesion1/studio_celu/` = fotos de cerca con CELULAR (tienen mejor cámara).
- `tests/sesion1/tablero_webcam/` = fotos abiertas con WEBCAM (la que va a jugar).
- `tests/sesion1/videos/` = videos con WEBCAM.

## BLOQUE 1 — Estudio con celular (ya tienes 7, agrega 2 = 9)

Ya tienes: 6 fondo blanco todos los ángulos + 1 fondo negro frontal. Están bien, cópialas a `studio_celu/`.

Agrega con celular, a 20cm, luz blanca de día o lámpara blanca:
8. `cenital.jpg` = desde arriba mirando la base.
9. `acostada.jpg` = la mini acostada de lado (volteada) en fondo blanco.

Para qué sirven: recortar la silueta y enseñarle al YOLO cómo es tu criatura. La acostada NO se puede inventar bien, por eso te pido 1 real.

## BLOQUE 2 — Tablero vacío con webcam (6 fotos, SIN mini)

Pon el Kill Team estirado con cinta, sin arrugas. Webcam quieta a 60cm mirando a 45°. Corre:

```
python "vision\scripts\foto_webcam.py"
```
Pulsa ESPACIO para cada foto. Guarda en `tablero_webcam/` (muévelas ahí al terminar).

- 2 con luz blanca fría (lámpara blanca).
- 2 con luz cálida (bombillo amarillo normal).
- 2 con RGB (1 azul + 1 rojo, el que más uses jugando).

Para qué sirven: fondos reales + medir falsos positivos. La prueba S01 es: tablero vacío debe dar 0 minis.

OJO RGB: la luz de color cambia todo. El programa actual busca por brillo, con rojo/azul fuerte va a fallar más. Es normal, lo anotamos, YOLO lo maneja mejor después.

## BLOQUE 3 — Mini en tablero con webcam (12 fotos, CON mini)

Misma posición de cámara, no la muevas. Mini a color en el centro del Kill Team.

- 3 posiciones (izquierda, centro, derecha) x 2 estados (de pie / acostada) = 6 con luz blanca.
- Repite esas 6 con tu RGB favorito (el que más uses) = 6 más.
- Total 12. Nombres: `blanca_centro_pie.jpg`, `rgb_derecha_acostada.jpg`, etc.

Prueba cada foto quieta con:
```
python "vision\scripts\probar_foto.py" "C:\Users\OSCAR\Desktop\TTRPG-AI-DM\tests\sesion1\tablero_webcam\blanca_centro_pie.jpg" --minis 1
```
Debe decir: nitidez (OK si >=50), cuadro (ej B2) y estado (de_pie/caido).

## BLOQUE 4 — Videos con webcam (3 videos de 20 segundos)

```
python "vision\scripts\grabar_video.py" --nombre mover_A1_C3 --seg 20
python "vision\scripts\grabar_video.py" --nombre poner_quitar --seg 20
python "vision\scripts\grabar_video.py" --nombre acostar_levantar --seg 20
```
1. `mover_A1_C3`: mueve la mini lento de izquierda a derecha.
2. `poner_quitar`: ponla y quítala 3 veces.
3. `acostar_levantar`: de pie -> acostada -> de pie.

## BLOQUE 5 — Vivo con grid 4x4 (la prueba final del previo)

```
python "vision\scripts\grid_cam.py" --cols 4 --rows 4 --minis 1
```
Cuando salga 8/10 bien, sube a:
```
python "vision\scripts\grid_cam.py" --cols 4 --rows 4 --minis 3
```

Qué comprobar exactamente (anota sí/no):
1. [ ] Muevo a otro cuadro -> el nombre cambia (A1->B1). Solo importa el CENTRO (punto), aunque toque varios.
2. [ ] La dejo quieta -> se queda marcada 4 seg y dice (quieto), no se borra al segundo.
3. [ ] La acuesto -> se pone ROJO y dice caido. La paro -> VERDE de_pie.
4. [ ] Tablero vacío -> dice --- (0 minis). Si marca algo, pulsa R.
5. [ ] Nitidez arriba: verde OK (>=50). Si rojo BORROSA, más luz blanca o limpia el lente.
6. [ ] Con RGB: anota si falla más que con blanca (esperado, no es error tuyo).

## Resumen de conteos

- Estudio celular: 9 (7 que ya tienes + cenital + acostada).
- Tablero vacío webcam: 6 (2 blanca + 2 cálida + 2 RGB).
- Mini en tablero webcam: 12 (6 blanca + 6 RGB).
- Videos: 3 x 20s.
- Total: 27 fotos + 3 videos.

Cuando tengas eso dime "sesión 1 lista" y hacemos la medición 8/10 juntos antes de YOLO.
