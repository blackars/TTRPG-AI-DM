# 15 — Mientras entrena + siguiente nivel (no todo espera al V1)

## Lo que NO necesita el resultado del V1 (hazlo ya)

1. **Biomas en ráfaga (20 min):** por cada fondo digital: F11 fullscreen, sin cursor,
   foto con teléfono trípode A2 + misma con brillo 60%. Nombres `bioma_{nombre}_{100,60}.jpg`
   a `dataset/fondos_biomas/`. Luego `recortar_marco.py` y `tenir.py --carpeta` x6 tintes.
   Tienes cientos: con 20 ya duplicas los fondos del V2.
2. **Digitalizar módulos físicos:** cada árbol/hongo/edificio: fondo blanco, 3 fotos
   (frente, lado, arriba 45°) con celular a 20cm. Van a `tests/sesion1/modulos/`.
   Después `cutout` → PNGs de escenografía (clase 1 futura + obstáculos del synth).
3. **Batallas en dioramas:** igual que `cenital_batalla` pero en bosque/agua:
   3-6 minis + 1 video 20s por montaje. Esas fotos son test real del nivel 2.
4. **Hiperzonas:** fotografía cada zona por separado (no toda la mesa junta):
   `zona_{bosque,rio,ciudad}_{vacia,conminis}.jpg`. El modelo aprende por zona mejor que revuelto.

## Lo que SÍ espera al best.pt (~2h)

- `detect_live.py --foto` en tus 6-minis + `mAP` del val. Umbrales:
  >0.80 integra en vivo / 0.50-0.80 suma frames reales / <0.50 revisa etiquetas.
- Puente visión→TinyJev→table/state (siguiente script tras el mAP).

## Scripts listos esperando pesos

- `detect_live.py` (compila OK, pide ultralytics + best.pt y sale limpio sin ellos).
- `recortar_marco.py`, `tenir.py`, `extraer_frames.py`, `gen_manifest.py` (este último:
  agregar loops de `modulos/` y nuevas tandas igual que dioramas/biomas).
