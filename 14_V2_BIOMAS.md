# 14 — V2 Biomas digitales (pantalla/proyector como tablero)

## Idea (tuya, correcta)

V1 = Kill Team físico + 6 minis (ya lo tenemos, no tocar más minis).
V2 = cientos de biomas (cyberpunk, bosques, ciudades góticas…) como FONDOS, no como tableros físicos.
El tablero físico se vuelve pantalla/proyector que muestra el bioma + grid + overlays.

## Hasta qué punto agregar fotos fullscreen de biomas: MUCHO, pero con reglas

- **Sí, 70% de los fondos del V2 pueden ser biomas digitales.** El modelo agnóstico aprende
  "mini vs fondo", y cada bioma distinto le enseña a ignorar otro tipo de textura. 30-50 biomas
  distintos x 4-6 variantes de brillo = 150-300 fondos. Con eso + tus PNGs de 6 minis, el lote V2
  llega a 600-1000 sintéticas sin tomar 1 foto más.
- **Captúralos en la MISMA pantalla/proyector que vas a usar** (fullscreen, sin UI, 16:9).
  La pantalla mete brillo, contraste y temperatura propios: un screenshot del PC no es igual a la
  foto de la pantalla encendida. Toma la foto CON EL TELÉFONO a la pantalla, desde el trípode,
  mismo ángulo A2 60°.
- **Mezcla obligatoria:** 50% fondos reales (Kill Team + mesa), 30% biomas digitales fotografiados,
  20% lisos (blanco/negro/gris). Si metes 100% digital, el modelo falla en tablero físico real.
- **Brillo doble:** por cada bioma captura 2 versiones (brillo proyector 100% y 60%). La luz del
  proyector cambia los colores de las minis (ya lo vimos con RGB: el azul se las traga).
- **NO antes del V1:** entrena y valida el nano en Kill Team primero (lote 1+2). Los biomas entran
  cuando el V1 dé mAP50 > 0.80 en tablero real. Si no, no sabrás si el fallo es el modelo o el bioma.

## Niveles de fondos (currículo: simple → complejo, no mezclar todo de golpe)

- **Nivel 1 (AHORA, V1 nano):** Kill Team físico + 6 minis. Cierra el nano aquí primero.
- **Nivel 2 (lote 2-3):** dioramas físicos con textura (bosques, edificios, tus montajes).
  Van como `set=diorama` en el manifest: misma receta que Kill Team (vacías + minis + 1 video por montaje).
  La escenografía será la clase 1 después; por ahora cuenta como fondo texturizado.
- **Nivel 3 (V2):** biomas digitales en pantalla/proyector fotografiados (sección anterior).
- **Nivel 4 (después del V2):** videos de competencias wargaming, partidas grabadas, screenshots.
  Esos NO traen máscaras: sirven como validación/test + minado de fondos (extraer frames vacíos),
  no como entrenamiento directo hasta tener el V2 estable. Si los metes ahora, el entreno se
  contamina y no sabrás qué falló.

Regla: cada nivel entra solo cuando el anterior da mAP50 > 0.80 en tablero real.

## Cómo capturar los digitales (cuando lleguemos, 20 min)

1. Proyector/pantalla en fullscreen con el bioma (oculta cursor, F11).
2. Teléfono en trípode A2, foto al tablero vacío proyectado: `bioma_{nombre}_100.jpg` y baja brillo a 60%: `bioma_{nombre}_60.jpg`.
3. 10 biomas variados = 20 fondos. `tenir.py` los multiplica x6 tintes.
4. Van a `dataset/fondos_biomas/`. `synth.py` los mezcla con `--fondos` múltiple (lote V2).

## Dato que lo justifica (medido hoy)

`probar_foto.py` en tu mejor foto (nitidez 3051, 6 minis perfectas) detectó **0 minis** por contraste:
el tablero texturizado derrota al método simple siempre. YOLO + biomas variados es el camino.
