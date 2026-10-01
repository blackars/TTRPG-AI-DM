# 13 — Dataset rico: 6 minis × ángulos × luces (trípode + aro)

Minis: verde, roja, azul, amarilla, morada, naranja. 6 colores = el modelo aprende FORMA, no color.

## Ángulos (marca cada posición del trípode con cinta)

| ID | Ángulo | Para qué | Estado |
|---|---|---|---|
| A1 cenital 90° | teléfono mirando recto abajo, 50cm | grid perfecto, sin oclusión | PENDIENTE (siguiente montaje) |
| A2 alto 60° | el actual `mover_alto` | juego principal | HECHO (21 fotos, nitidez 2869) |
| A3 medio 45° | a mitad entre A2 y mesa | variedad caras laterales | PENDIENTE |
| A4 lateral 25° | el primer set | variedad extrema/oclusión | HECHO (64 fotos, nitidez ~1400) |
| A5 macro 20cm | 1 mini llenando media pantalla | texturas/detalle | opcional después |

## Luces (aro + RGB)

L1 blanca 100% (base de todo) · L2 cálida · L3 penumbra 50% · L4 azul real · L5 rojo real.
Digital con `tenir.py` (azul/rojo/verde/cálido/penumbra/frío) cubre el resto: probado OK,
genera variedad válida aunque el tono no sea exacto al RGB físico.

## Qué tomar por combo (fotos quietas + 1 video 20s por ángulo)

- Vacía x3 (fondos HD).
- 1 mini x3 (una de cada 2 colores, rota).
- 3 separadas x3 (1 cuadro entre ellas).
- 3 pegadas x2 (oclusión a propósito).
- 6 batalla campal x2 (todas, mezcladas pie/acostada).
- Video 20s moviendo 1 mini por 4 puntos.

## Checklist mínimo rico (lo que falta)

- [ ] A1 cenital × L1: 9 fotos + 1 video `cenital_batalla` (SIGUIENTE MONTAJE PEDIDO)
- [ ] A3 medio × L1: 6 fotos + 1 video `medio_batalla`
- [ ] A2 alto × L2 cálida: 6 fotos (ya tienes tablero, solo cambia luz)
- [ ] A2 alto × L4 azul real: 4 fotos con 2-3 minis (casos difíciles reales)
- [ ] Estudio celu: 1 frontal por mini nueva (roja, azul, amarilla, morada, naranja) → PNG masters lote 2
- [ ] Digital: `tenir.py --carpeta dataset/frames_phone --color X` para azul/rojo/verde/cálido

Total estimado lote 2: ~40 fotos reales HD + ~120 variantes digitales + 200 sintéticas lote 1 + masters nuevos.
