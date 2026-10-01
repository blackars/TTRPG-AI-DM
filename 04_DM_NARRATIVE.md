# 04 — DM Narrativo (LLM local) + Plantillas + TTS + Sonido

> El LLM es actor de voz y escritor, no juez. JEV sentencia, MiniBase da inventario, el LLM narra el resultado en ES/EN y lo manda a voz + texto.

Stack free: `Ollama + mistral:7b / llama3.1:8b` local, `Piper` TTS CPU, `Web Audio API` ambiente.

## 1. Los 3 prompts (no uno solo)

Separar roles evita que el LLM invente reglas o minis que no tienes.

**A. Story (narración visible):**

```text
Eres el DM. Sistema: {d20|d100|...}. Tono: {cosmic_horror}.
Inventario real: {xenomorph:23, facebug:7}. No inventes minis fuera de esta lista.
Fase: {movement}. Guion secreto (no revelar): {el nido está en F5}.
Último veredicto JEV: {tirada d20+3=18, spawnean 18, casillas F5,F6...}.
Responde en {es}, 2-4 frases + 1 pregunta al jugador. Caja texto obligatoria.
```

**B. GM oculto (extractor deltas, no visible):**

```text
Dada la última interacción, extrae JSON: {hp_deltas, items, npc_actitud, eventos_mundo, objetivos_avance}.
No narres, solo JSON válido.
```

**C. Summarizer (memoria campaña):**

```text
Resume capítulo en 10 líneas: hechos, muertos, loot, pistas. Preserva nombres y casillas.
```

Modelos sugeridos 1 PC: `Story=mistral:7b-instruct`, `GM=qwen2.5:3b` rápido, `Summarizer=llama3.1:8b`. Todo vía OpenAI-compatible `http://localhost:11434/v1`.

```bash
ollama pull mistral:7b-instruct
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

## 2. Orquestación por turno (código, no magia)

```python
# dm/turn.py — pseudocódigo
def turno(input_jugador):
    contexto = minibase.search(input_jugador) + table_state() + plantilla()
    propuesta = llm_story(contexto, input_jugador)          # borrador
    veredicto = jev.validar(propuesta)                       # dados, spawn, muros, Mythic si ambiguo
    texto_final = llm_story.narrar(veredicto)                # 2-4 frases ES + EN corto
    gm_delta = llm_gm.extraer(input_jugador, texto_final)    # JSON stats
    aplicar(gm_delta, table_state)                           # hp, loot, fase
    tts.encolar(texto_final)                                 # Piper, no bloquea
    return texto_final
```

Latencia objetivo: JEV <10ms, GM <2s, Story 5-12s. Mostrar "DM pensando..." + overlay en proyector mientras tanto. Streaming token por token al dashboard vía SSE.

## 3. Plantillas historia (las que pide requerimientos)

```json
// dm/templates/campaign.json
{"titulo": "", "sistema": "d100", "tono": "cosmic_horror", "idioma": "es",
 "actos": [{"id": 1, "objetivo_marco": "rastrear nido", "pistas": 3,
            "presupuesto": {"xenomorph": 23, "escenografia": 5}}],
 "filtros": {"excluir_tipos": [], "solo_genero": ["horror", "sci-fi"]},
 "guion_secreto": ""}
```

* `one_shot.json`: 1 acto, spawn generoso, sin carry-over.
* `wargame.json`: sin narración larga, objetivos `eliminar/capturar`, JEV estricto.
* Input usuario opcional al inicio: tono, excluir tipos ("sin payasos"), idioma. Si no responde, usa defaults + lo que falte lo vuelve misterio.
* Nombres: si slug es `bestia_04`, Story propone nombre según núcleo y lo guarda en `nickname` (no se pierde).

## 4. Filtros lenguaje natural + MiniBase

```python
# "no quiero bichos voladores, solo selva"
filtros = llm_gm.parsear_filtros(texto)  # {excluir_tags:["volador"], incluir_tags:["selva"]}
candidatos = minibase.agent_search(query, filtros)
```

Siempre mostrar en dashboard qué filtros se aplicaron + botón limpiar. Nunca excluir silenciosamente.

## 5. TTS ES/EN + caja texto (requerimiento)

* Motor base: `Piper` (MIT, CPU, rapidísimo). Voces: `es_MX-ald-medium` / `es_ES-carlfm-x-low` + `en_US-lessac-medium`.
* Clonación DM (opcional): `XTTS-v2 / Chatterbox` con 6s de referencia, solo si hay GPU. Si no, Piper basta.
* Servidor compatible OpenAI audio para que Corvus/NarrativeEngine-style funcione:

```bash
pip install piper-tts
# voz Narrador grave, voz NPC aguda (+pitch), cola con pause/resume
python dm/tts_server.py --voice-es es_MX-ald-medium --voice-en en_US-lessac-medium
```

Reglas: toda respuesta tiene `texto` visible + `audio` opcional con toggle ES/EN. Velocidad 1.0x narración, 1.15x combate. Nunca solo audio.

## 6. Sonido ambiente (no todo es TTS)

Capas `Web Audio API`, assets `freesound.org` (free, atribución en `assets/CREDITS.md`):

* `ambiente` loop bajo (selva/nave/lluvia) -12dB.
* `stinger` en spawn/daño (1-2s).
* `música` combate/narrativa, crossfade con fase.
* Ducking: al hablar TTS, ambiente baja -6dB automáticamente.

```text
dm/audio/
  ambient_selva.mp3, ambient_nave.mp3, stinger_spawn.wav, stinger_crit.wav
  mixer.ts  # 3 canales + ducking + mute global
```

## 7. Archivos a crear

```
TTRPG-AI-DM/dm/
  prompts/story.txt, gm.txt, summarizer.txt
  templates/one_shot.json, campaign.json, wargame.json
  turn.py, memory.py, tts_server.py, mixer.ts
```

Test aceptación: turno completo con `23 xenos` narra en ES + EN, muestra caja texto, reproduce TTS, actualiza `table/state` y guarda delta JSON sin inventar minis.
