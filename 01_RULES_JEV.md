# 01 — Motor JEV (Juicio / Evaluación / Veredicto) + Reglas + Mythic

> Cerebro determinista rápido. Python puro, <5ms, sin GPU, sin LLM.
> Todo lo que sea número, dado, distancia o tabla lo decide aquí. El LLM narra, el JEV sentencia.

Referencia: `00_OVERVIEW.md §2, §6`. Fuente verdad inventario: MiniBase `GET /api/minis`, `GET /api/agent/search`.

## 1. Qué es y qué no es

* **ES:** máquina de estados + calculadora de dados + Mythic emulator + validador de movimientos + economía/stats.
* **NO ES:** narrador, no genera texto libre, no necesita Ollama. Si tarda >10ms, está mal diseñado.

```
[LLM propone] -> [JEV valida/calcula] -> [table/state + dashboard] -> [LLM narra resultado]
Ej: "quiero spawnear xenos" -> JEV: tienes 23, tira d20+3 -> sale 18 -> spawnea 18 -> LLM narra
```

## 2. Máquina de estados canónica

```text
Game { mode: one_shot | campaign | wargame_1v1 | wargame_vs_machine | creative_locked }
 └─ Chapter { id, resumen, objetivos_marco[] }
     └─ Encounter { id, mapa_id, presupuesto_spawn }
         └─ Turn { n, iniciativa[] }
             └─ Phase: narrativa -> movement (grid ON) -> combate -> loot -> narrativa...
```

Reglas:

* Solo `phase=movement` permite `grid_visible=true` y movimientos validados por `rpg_profile.movement`.
* Cambio de fase solo vía `POST /api/table/state`. El proyector obedece, nunca decide.
* Todo cambio de stats/inventario genera evento JSONL append-only para poder rebobinar campaña.

```json
// POST /api/table/state ejemplo
{"encounter_id": "enc03", "phase": "movement", "grid_visible": true,
 "tokens": [{"mini_id": "xenomorph-01", "x": 2, "y": 5, "hp": 12, "track_id": 7}]}
```

## 3. Cálculo spawn dX+Y (requerimiento núcleo)

Dados típicos: `d4, d6, d8, d10, d10dec, d12, d20`. Dado N disponible, cantidad C real de MiniBase.

Objetivo: sugerir `dN + modificador` tal que `max(dN)+mod = C`, con `|mod|` mínimo. Si C > 20, combinar tiradas.

```python
DADOS = [4,6,8,10,12,20]
def sugerir_dado(cantidad: int):
    # retorna (dado, mod) con menor |mod|, prefiere mod positivo pequeño
    best = None
    for d in DADOS:
        mod = cantidad - d
        # permite d10dec como d10*10 si hace falta, se maneja aparte
        score = (abs(mod), -mod)  # prefiere +3 sobre -3
        if best is None or score < best[0]:
            best = (score, (d, mod))
    return best[1]  # ej. 23 -> (20, +3), 7 -> (8, -1) compite con (6,+1), gana (6,+1) por |1| vs |1| y positivo
```

Casos:

* 23 xenos -> `d20+3` (max 23). Min 4, media 13.5. Si sale 18, spawnean 18, faltan 5 en reserva.
* 7 facebugs -> `d6+1` (candidatos `d8-1` y `d6+1`, elegir `|mod|` menor, desempate positivo).
* C=1 -> no tirar, spawn directo. C>40 -> `2d20` o `d20+d12` según prefieras, documentar en evento.
* Siempre reportar: `tirada, total, spawneados, sobrantes/faltantes, casillas sugeridas`.

Endpoint futuro: `POST /api/jev/spawn {mini_slug, cantidad_total} -> {dado, mod, tirada, total}`.

## 4. Plugins de sistemas (d20 / d100 / PbtA / FATE / GURPS)

Un archivo por sistema en `jev/rules/`. Interfaz común:

```python
def check(atributo: int, mod: int, dificultad: int, modo: str) -> dict
# retorna {tirada:[...], total:int, exito:bool, grado:str, raw:str}
```

* **d20 (D&D 7e / Pathfinder / Gloomhaven / Stargrave táctico):** `d20+mod >= DC`. Crit 20/1. Ventaja = 2d20 quédate mayor.
* **d100 BRP (CoC):** `1d100 <= habilidad`. Grados: crítico <=5%, pifia 96-100. No sumar, comparar.
* **PbtA 2d6:** `2d6+attr`: 10+ éxito, 7-9 parcial (el DM complica), 6- falla (DM mueve). Sin DC fija.
* **FATE 4dF:** cada dado -1/0/+1. Invocar aspecto = +2 o reroll gastando Fate point.
* **GURPS 3d6:** `3d6 <= habilidad`. Campana gaussiana, crítico 3-4 / pifia 17-18.

MVP: implementar `d20.py + mythic.py` primero. Los demás son 30 líneas cada uno.

## 5. Mythic Game Master Emulator (tablas internas)

Cuando la historia no tiene regla, JEV tira Mythic, no el LLM.

* **Fate Check:** probabilidad por `chaos_rank 1-9` + pregunta sí/no. Tabla `d100 <= umbral`. Excepcional en dobles.
* **Event Meaning:** `d100 acción + d100 sujeto` (100x100 tablas). JEV devuelve par crudo, LLM lo interpreta con lore MiniBase.
* **Scene Check / Lists:** `d10 vs chaos` para escena alterada/interrumpida, listas objetivo marco.

```python
def fate_check(odds: str, chaos: int) -> bool  # odds: imposible..seguro
def event_meaning() -> tuple[str,str]          # ej. ("Perseguir","Esperanza")
```

El LLM recibe: `mythic={pregunta, odds, chaos, resultado: Sí, pero...}` y narra. Nunca deja al LLM tirar dados mentales.

## 6. Plantillas historia + guion secreto + objetivos marco

```json
// campaign_template.json (MiniBase rpg_profile + lore la rellenan)
{"titulo": "", "tono": "cosmic_horror", "sistema": "d100",
 "actos": [{"id": 1, "objetivo_marco": "descubrir nido", "presupuesto_spawn": {"xenomorph": 23}}],
 "guion_secreto": "solo DM, nunca al jugador",
 "filtros_excluir": ["sci-fi limpio"], "idioma": "es"}
```

* JEV valida que `presupuesto_spawn <= cantidad MiniBase`. Si falta, convierte carencia en misterio ("rastros, no nido completo").
* Nombres: si mini es `descriptor_genérico_04`, JEV pide al LLM bautizar según núcleo historia y lo guarda en `nickname`.
* Input usuario opcional (tono, excluir tipos por lenguaje natural) solo ajusta plantilla, nunca es obligatorio.

## 7. Modos de juego

| Modo | Estado guarda | JEV hace distinto |
|---|---|---|
| `one_shot` | solo encounter | sin persistencia larga, spawn generoso |
| `campaign` | chapters + resumen Summarizer | presupuesto por capítulo, carry-over hp/loot |
| `wargame_1v1` | simétrico | desactiva narración larga, valida `range/movement` estricto |
| `wargame_vs_machine` | IA enemiga = JEV + heurística | decide movimientos enemigos por distancia/cobertura, LLM solo narra |
| `creative_locked` | nada (botón referencia) | `feature_flag=false`, no entra al orquestador |

## 8. Dados MVP + TTS/texto

* MVP: `random` Python + animación CSS en dashboard. v2: `react-three-fiber + cannon` y tomar resultado de física.
* Toda sentencia JEV genera `texto_es + texto_en` corto para `Piper TTS` + caja texto obligatoria. El audio nunca es la única salida.

## 9. Archivos a crear (cuando pasemos a código)

```
TTRPG-AI-DM/jev/
  state.py        # Game>Chapter>Encounter>Turn>Phase + table/state sync
  dice.py         # d4..d20 + sugerir_dado()
  rules/d20.py, brp.py, pbta.py, fate.py, gurps.py
  mythic.py       # fate_check, event_meaning
  spawn.py        # presupuesto vs MiniBase + casillas estratégicas
  templates/      # one_shot.json, campaign.json, wargame.json
```

Test de aceptación: `23 -> d20+3`, `7 -> d6+1`, `fate 2d6=7 -> parcial`, `phase=movement -> grid ON`.
