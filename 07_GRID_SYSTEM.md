# 07 — Sistema Grid Dual: Cuadrados + Hexágonos + Escenas SVG

> Dos grids principales, un solo `table/state`. El grid no es dibujo, es matemática + capas SVG + conexión a escenas y animaciones.

Referencia: redblobgames hexagons (axial/cube), `03_TABLE_PROJECTOR.md`.

## 1. Decisión: cuándo cuadrado, cuándo hex

|  | Cuadrado (rejilla típica) | Hexagonal |
|---|---|---|
| Sistemas | D&D, Pathfinder, CoC, Gloomhaven | Stargrave, wargames, exteriores |
| Coordenada jugador | `A1, B4` (col letra + row núm) | `q,r axial` mostrado como `03.04 offset-odd-r` o `C-04` |
| Vecinos | 4 (Manhattan) u 8 (Chebyshev) | 6, distancia única, sin diagonales rotas |
| Movimiento | `Chebyshev max(dx,dy)` para D&D 5e | `cube_distance = (dx+dy+dz)/2` |
| Mejor para | interiores, muros rectos, puertas | campo abierto, flanqueo, conos |
| Proyección | rectángulos, fácil keystone | pointy-top para pasillos verticales, flat-top para horizontales |

Soporte dual desde día 1: `grid.json` lleva `tipo`. JEV y visión leen `tipo` y cambian fórmula distancia/validación. Proyector cambia renderer, nada más.

```json
// grid.json
{"tipo": "square", "cols": 12, "rows": 9, "cell_mm": 50, "origen": "A1-arriba-izq"}
{"tipo": "hex", "cols": 11, "rows": 9, "cell_mm": 50, "orientacion": "pointy", "offset": "odd-r"}
```

## 2. Matemática mínima (implementada en `grid/grids.py`)

**Square:**

```python
def square_to_pixel(col, row, cell_px, origin): return (origin[0]+col*cell_px, origin[1]+row*cell_px)
def square_distance(a, b, diagonal="chebyshev"):
    dx, dy = abs(a[0]-b[0]), abs(a[1]-b[1])
    return max(dx,dy) if diagonal=="chebyshev" else dx+dy
def square_to_A1(col,row): return f"{chr(65+col)}{row+1}"
```

**Hex (axial q,r, s=-q-r, pointy-top default):**

```python
import math
# pointy: x = sqrt(3)*(q + r/2), y = 3/2*r  | flat: x = 3/2*q, y = sqrt(3)*(r + q/2)
def hex_to_pixel(q,r,size,origin,orient="pointy"):
    if orient=="pointy":
        return (size*math.sqrt(3)*(q+r/2)+origin[0], size*1.5*r+origin[1])
    else:
        return (size*1.5*q+origin[0], size*math.sqrt(3)*(r+q/2)+origin[1])
def hex_distance(a,b):  # a,b=(q,r)
    aq,ar=a; bq,br=b; return (abs(aq-bq)+abs(aq+ar-bq-br)+abs(ar-br))//2
def hex_neighbors(q,r): return [(q+1,r),(q+1,r-1),(q,r-1),(q-1,r),(q-1,r+1),(q,r+1)]
def hex_round(qf,rf):
    sf=-qf-rf; qi,ri,si=round(qf),round(rf),round(sf)
    dq,dr,ds=abs(qi-qf),abs(ri-rf),abs(si-sf)
    if dq>dr and dq>ds: qi=-ri-si
    elif dr>ds: ri=-qi-si
    return (qi,ri)
```

Rango, línea, anillo y FOV salen de `hex_distance` + `hex_neighbors` (ver redblobgames). No reinventar.

## 3. Recursos para dibujar (todos free/abiertos)

**Proyector web (recomendado):**

* `SVG puro + React` — 60fps con <200 nodos, sin libs. Cada celda `<polygon>`, cada overlay `<g>` con CSS `pulse/dash`.
* `hex-grid-kit` (MIT, TS) — `createHexGrid({shape:'rectangle',columns:10,rows:6})` + `renderHexGridSvg` + `hitTest`. Úsalo si no quieres escribir math en JS.
* Alternativa Canvas si >500 celdas: `<canvas>` + `requestAnimationFrame`, mismo math.

**Python calibración/test:**

* `OpenCV (Apache2)` — ArUco, `findHomography`, `perspectiveTransform`, dibujar grids en fotos test.
* `Albumentations (MIT)` — ya lo usas para dataset.

**Animaciones SVG (solo CSS, cero JS por frame):**

```svg
<!-- spawn pulsante -->
<polygon points="..." fill="#ff444422" stroke="#ff4444" stroke-width="3" class="pulse"/>
<!-- flecha movimiento -->
<line x1=".." y1=".." x2=".." y2=".." stroke="#44ff88" stroke-dasharray="8 6" class="dash-move" marker-end="url(#arrow)"/>
<!-- círculo ? -->
<circle r="28" fill="none" stroke="#ffcc00" stroke-width="4" class="ping"/>
<style>.pulse{animation:pulse 1.2s infinite}@keyframes pulse{50%{opacity:.35}}</style>
```

Capas fijas: `#bg-escena` (imagen tenue 30%) → `#grid` → `#spawns` → `#tokens-confirmados` → `#overlays` → `#fog`. La escena nunca tapa el grid, va debajo.

## 4. Conexión escena ↔ grid ↔ animación

```json
// scenes/escena_selva_hex.json
{"id": "selva_hex_01", "grid": {"tipo": "hex", "orientacion": "pointy"},
 "bg": "selva tenue.jpg", "spawns": [{"mini": "xenomorph", "celda": "05.04", "clase": "enemigo"}],
 "overlays_intro": [{"tipo": "niebla", "celdas": ["00.00", "01.00"]}],
 "anim": "pulse-spawn + fog-fade 2s"}
```

Flujo: DM elige escena → JEV valida presupuesto MiniBase → proyector renderiza `bg+grid+spawns` → jugador coloca → visión confirma → overlays cambian a `flechas/rangos`.

Rangos: JEV calcula `alcance = range_casillas` y manda lista celdas a iluminar. Proyector solo pinta.

## 5. Qué crear en código (ver `grid/`)

* `grids.py` — math square+hex + `to_svg()` + `to_A1()` + `hex_to_offset()` para mostrar al jugador.
* `scenes/*.json` — 12 escenas base (ver `08_VISION_TEST_PLAN.md`).
* `web/table/GridOverlay.tsx` — switch `square|hex`, props `tokens, spawns, overlays`, CSS anims.
* `calibrate_projector.py` — genera patrón square y hex para alinear proyector una vez.

Test dual: misma encounter en square y hex debe dar misma cantidad detecciones, solo cambia etiqueta celda.
