# 06 — Jev (el modelo decidor) y sus alternativas abiertas

## 1. Qué es Jev, en 3 frases

1. Jev es de la empresa TypeSafe, salió el 15 de septiembre de 2026. No es un chat como ChatGPT.
2. Tú le pasas un texto (ej: "el mago tiene 14 de vida y está en A1") + una pregunta con opciones fijas (ej: ¿qué hace? opciones: atacar / huir / curar). Él NO escribe un párrafo, solo devuelve: "atacar, 92% seguro". Eso es todo.
3. Por eso es rapidísimo: 70 a 500 milisegundos. Un LLM normal tarda 3 a 30 segundos porque escribe palabra por palabra. Jev responde de una sola pasada, sin escribir texto.

Por qué no tienes acceso: está en lista de espera (early access), con alta demanda. Es cerrado y de pago.

## 2. Cómo lo usamos en tu juego (ejemplo real)

En tu mesa NO necesitas que una IA escriba bonito para decidir. Necesitas decidir rápido:

- Estado = "xenomorpho en F5, mago en A1 con 14hp, fase=movement"
- Pregunta fija = "¿el xenomorpho ataca? opciones: sí / no"
- Respuesta = "sí, 88%". El código entonces mueve la mini y el LLM narrativo después cuenta la historia.

Eso lo hace Jev, y lo hacen sus copias abiertas. El narrador bonito (Ollama mistral/llama) va aparte y puede ser lento, no importa.

## 3. Alternativas abiertas que YA existen (todas verificadas hoy)

Todas hacen lo mismo: estado + opciones fijas = respuesta + probabilidad. Todas son gratis, código abierto, corren en tu PC sin internet tras descargarlas.

| Nombre | Tamaño / qué PC necesitas | Licencia | Instalar con | Cuándo usarla |
|---|---|---|---|---|
| **TinyJev 0.6B** (recomendada para ti) | 1.2 GB, corre en cualquier laptop, 85ms | MIT | `pip install tinyjev` | Empieza aquí. Para decisiones de mesa: atacar/huir, spawn sí/no, urgencia 1-5 |
| **TinyJev 4B** | 8 GB, necesitas 16GB RAM, 628ms | MIT | `pip install tinyjev` | Si la 0.6B se equivoca mucho, sube a esta |
| **Kev 0.8B / 4B / 9B** | 0.8B laptop / 4B PC gamer / 9B PC potente | Apache 2.0 | `git clone https://github.com/jaredpalmer/kev` | Si quieres la más compatible con Jev original (mismo conector) |
| **fastjev + Qwen3.5-4B** | 3 GB en Q4, PC normal, 82ms con GPU / 2.3s en CPU | MIT | `pip install fastjev` | Si quieres calidad máxima en PC normal, la que mejor mide (81% calidad) |
| **Von 0.4B** | 0.4 GB, la más pequeña, 1 pasada | Apache 2.0 | `https://github.com/wfzyx/von` | Si tu PC es muy vieja |
| **FastDecider 149M** | 285 MB, <15ms, rapidísima | Apache 2.0 | `HuggingFace mkzero/FastDecider-149M` | Para dentro del loop de cámara (decidir 30 veces por segundo) |
| **autotrust/JEV-27B** | 55 GB, necesitas H100 80GB (NO es para ti) | Apache 2.0 | no instalar | Solo para saber que existe la más precisa, ignórala por ahora |

## 4. Recomendación concreta para ti (haz esto)

Tienes Windows y quieres probar ya, sin GPU cara:

```powershell
pip install tinyjev
python -m tinyjev.server --port 8000
```

Y en tu juego lo llamas así (ejemplo en Python):

```python
from tinyjev import load
juez = load("TinyJev-0.6B")  # se descarga 1 vez, luego offline

respuesta = juez.decide(
  state="mago hp=14 en A1, xenomorpho en F5, fase=movement",
  pregunta="¿el xenomorpho ataca al mago?",
  opciones=["si", "no"]
)
print(respuesta.choice, respuesta.confidence)
# si -> 0.88 : entonces tu código mueve la mini en el grid, no el LLM
```

Regla de uso en partida:
- Si confianza >= 0.85 -> el juego lo hace solo.
- Si 0.60 - 0.85 -> lo hace pero lo marca para revisar.
- Si < 0.60 -> le pregunta al humano o al LLM grande.

## 5. Qué NO hacer

- No uses Jev ni sus copias para escribir historia. Para eso sigue Ollama mistral/llama.
- No llames a la API de TypeSafe en mesa (se cae, tiene cola, necesita internet).
- No instales la de 27B, no te cabe en el PC.

Test de que funciona: desconecta el wifi, corre el ejemplo de arriba, debe responder igual en <1 segundo.
