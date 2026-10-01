# 03 — Mesa / Table State + Proyector Dual + Overlays

> El proyector obedece, nunca decide. La única verdad es `table/state`. El dashboard muestra números, el proyector muestra luz.

Referencia: `00_OVERVIEW.md §4,§5,§8`, `01_RULES_JEV.md §2`, `02_VISION_DATASET.md §4`.

## 1. Principio de doble pantalla

| Monitor 1 — Dashboard (operador/DM) | Monitor 2 — Proyector (jugadores/mesa) |
|---|---|
| Stats, HP, dados, caja texto, `agent/search`, fase actual, botones | Solo escenarios: grid, spawn markers, círculos/flechas, niebla, animaciones |
| Tema oscuro, denso, con texto | Fullscreen negro, sin texto largo, alto contraste |
| Siempre visible | `grid_visible=true` solo si `phase=movement`, si no solo ambiente + overlays |

Nunca mostrar en proyector: guion secreto, stats enemigos exactos, tiradas Mythic crudas.

## 2. Contrato `table/state` (fuente verdad)

```json
// GET /api/table/state?encounter_id=enc03
{
  "encounter_id": "enc03",
  "phase": "movement",
  "grid_visible": true,
  "grid": {"cols": 12, "rows": 9, "cell_mm": 50},
  "tokens": [
    {"mini_id": "mago-01", "track_id": 7, "x": 2, "y": 5, "hp": 14, "estado": "de_pie"},
    {"mini_id": "xenomorph-03", "track_id": 11, "x": 6, "y": 5, "hp": 12, "estado": "de_pie"}
  ],
  "spawns_sugeridos": [
    {"mini_id": "xenomorph-04", "casilla": "F5", "clase": "enemigo", "prioridad": 1}
  ],
  "overlays": [
    {"tipo": "circulo", "casilla": "C3", "color": "#ff4444", "texto": "?"},
    {"tipo": "flecha", "de": "A1", "a": "A2", "color": "#44ff88"}
  ]
}
```

Reglas:

* `POST /api/table/state` solo lo emite JEV o DM Core. Visión hace `PATCH` parcial de posiciones, nunca cambia fase.
* WebSocket `/ws/table/{encounter_id}` emite diff, no frame completo. Proyector re-renderiza <50ms.
* Historial append-only `table_events.jsonl` para rebobinar turno.

## 3. Grid proyectado + calibración proyector

El proyector tiene su propia homografía `H_proyector->grid`, distinta de la cámara. Se calibra una vez por mesa:

1. Proyectar patrón 4 esquinas + chessboard.
2. Alinear esquinas físicas ArUco con esquinas proyectadas (ajuste keystone manual + `cv2.getPerspectiveTransform` fino).
3. Guardar `H_proj.npy` + `grid.json`. Si mueves proyector, recalibrar.

```python
# calibrate_projector.py — idea
# proyecta cruz en (0,0),(W,0),(W,H),(0,H), operador clickea en cámara dónde cayó,
# calcula H que mapea casilla lógica -> píxel proyector.
```

Tamaño: casilla lógica 50mm debe medir 50mm en mesa. Verificar con regla física, no a ojo.

## 4. Overlays que el DM puede dibujar

Tipos mínimos (SVG, no PNG pesado):

* `circulo / cruz / ? / !` en casilla para "investigar aquí".
* `flecha de->a` para explicar movimiento enemigo o sugerencia.
* `spawn_marker` pulsante por clase: jugador `#44ff88`, enemigo `#ff4444`, npc `#44aaff`, criatura `#cc66ff`.
* `cono/línea` para rango/visión (calculado por JEV con `range` de `rpg_profile`, no a ojo).
* `niebla` (fog of war): rectángulos negros semitransparentes donde el guion secreto dice "no revelado".

Todo overlay lleva `ttl_seg` + `autor: jev|dm|vision`. Expiran solos para no ensuciar mesa.

```json
{"tipo": "circulo", "casilla": "D4", "color": "#ffcc00", "ttl_seg": 20, "autor": "dm"}
```

## 5. Spawn interactivo estratégico

JEV no spawnea aleatorio. Flujo:

1. `spawn.py` pide a MiniBase candidatos por `tag/genre/lore` + cantidades.
2. Calcula casillas: lejos de jugadores (>3 casillas), cerca de `escenografia` (cobertura), no sobre muro.
3. Proyector muestra markers pulsantes numerados. Jugador coloca mini física encima.
4. Visión confirma: silueta nueva en casilla esperada -> `track_id` asignado. Si coloca mal, overlay rojo + TTS "ahí no, es muro".

## 6. Implementación web (Next.js, lo que ya tienes)

```
web/app/(dashboard)/encounter/[id]/page.tsx  # control DM, dados, fase, tokens
web/app/table/page.tsx                        # ruta proyector: ?encounter=enc03&fullscreen=1
web/lib/tableSocket.ts                        # ws subscribe + re-render canvas
```

`table/page.tsx`: `<svg viewBox="0 0 1200 900">` + `<g id="grid">` + `<g id="spawns">` + `<g id="overlays">`. Fondo `#000`, grid `#ffffff22`, animación CSS pulse. Sin Tailwind pesado, 60fps con <100 nodos.

Modo kiosco: Chrome `--kiosk --app=http://localhost:3000/table?encounter=enc03` en monitor 2 extendido (no duplicado).

## 7. Fallos típicos y cómo evitarlos

* Proyector lava colores minis -> usar colores spawn saturados + borde blanco 3px, nunca rellenar casilla completa.
* Latencia ws -> diff + `requestAnimationFrame`, no re-mount React por token.
* Jugador tapa ArUco con mano -> tracking predice 5 frames, si pierde pide "levanta la mano", no se cuelga.
* Luz ambiente cambia -> guardar preset `día/noche` con brillo proyector distinto.

Test aceptación: cambiar `phase` a `movement` enciende grid en <200ms, spawn de 3 xenos muestra 3 markers, al colocarlos visión los confirma y markers desaparecen.
