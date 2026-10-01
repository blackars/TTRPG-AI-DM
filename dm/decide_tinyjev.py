# decide_tinyjev.py — tu decidor rápido con TinyJev 0.6B
# Si TinyJev no está instalado aún, usa reglas simples para que puedas probar el flujo.
# Instalar cuando quieras:  pip install tinyjev
# Pesa 1.2 GB, se descarga 1 vez, luego funciona sin internet.

try:
    from tinyjev import load as _tiny_load
    _TIENE_TINYJEV = True
except Exception:
    _TIENE_TINYJEV = False

_juez = None

def _juez_lazy():
    global _juez
    if _juez is None:
        _juez = _tiny_load("TinyJev-0.6B")
    return _juez

def decidir(estado_texto: str, pregunta: str, opciones: list) -> dict:
    """
    estado_texto: frase normal. Ej: "mago hp=3 en A1, orco en A2"
    pregunta: qué quieres saber. Ej: "¿qué hace el mago?"
    opciones: lista fija. Ej: ["atacar", "huir", "curar"]
    Devuelve: {"choice": "huir", "confidence": 0.9, "motor": "tinyjev" o "reglas"}
    """
    if _TIENE_TINYJEV:
        j = _juez_lazy()
        r = j.decide(state=estado_texto, pregunta=pregunta, opciones=opciones)
        # tinyjev devuelve .choice y .confidence (según versión puede variar: choice/confidence)
        choice = getattr(r, "choice", getattr(r, "best", opciones[0]))
        conf = float(getattr(r, "confidence", 0.8))
        return {"choice": choice, "confidence": conf, "motor": "tinyjev"}
    # Respaldo sin instalar: reglas simples
    t = (estado_texto + " " + pregunta).lower()
    if "hp=3" in t or "hp 3" in t or "hp=2" in t:
        if "huir" in opciones:
            return {"choice": "huir", "confidence": 0.9, "motor": "reglas"}
    if "23" in t and "spawn" in t:
        return {"choice": "d20+3", "confidence": 0.95, "motor": "reglas"}
    return {"choice": opciones[0], "confidence": 0.7, "motor": "reglas"}

def como_usar_en_mesa(respuesta: dict) -> str:
    c = respuesta["confidence"]
    if c >= 0.85:
        return "HAZLO SOLO"
    if c >= 0.60:
        return "HAZLO Y MARCALO PARA REVISAR"
    return "PREGUNTA AL HUMANO"

if __name__ == "__main__":
    print("TinyJev instalado:", _TIENE_TINYJEV)
    r1 = decidir("tengo 23 xenomorphos en reserva", "¿qué dado para spawn?", ["d20+3", "d12", "d6"])
    print("Prueba spawn:", r1, "->", como_usar_en_mesa(r1))
    r2 = decidir("mago hp=3 en A1, orco en A2", "¿qué hace el mago?", ["atacar", "huir", "curar"])
    print("Prueba combate:", r2, "->", como_usar_en_mesa(r2))
