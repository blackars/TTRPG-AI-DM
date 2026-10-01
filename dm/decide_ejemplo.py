# Ejemplo simple: cómo decidir sin LLM lento (funciona con TinyJev o con Python puro si aún no instalas nada)

# Qué hace este archivo:
# - Le das el estado del juego en texto normal
# - Le das opciones fijas
# - Te devuelve una decisión + % seguro
# Así trabaja Jev y sus copias abiertas. Sin escribir párrafos.

# PASO 0: si aún no instalas tinyjev, este ejemplo corre igual con reglas simples.
# Cuando instales tinyjev, solo cambia DECIDOR = "tinyjev".

DECIDOR = "reglas"  # cambia a "tinyjev" cuando hagas pip install tinyjev

def decidir_con_reglas(estado: dict, pregunta: str, opciones: list):
    """Decisor de juguete: solo para probar el flujo sin instalar nada."""
    # Ejemplo real tuyo: 23 xenomorphos -> sugerir d20+3
    if "spawn" in pregunta.lower():
        total = estado.get("cantidad_total", 0)
        # busca dado + modificador (misma lógica de 01_RULES_JEV.md)
        for dado in [4, 6, 8, 10, 12, 20]:
            if total - dado <= 5 and total - dado >= -5:
                return {"choice": f"d{dado}{total-dado:+d}", "confidence": 0.95}
        return {"choice": "d20", "confidence": 0.6}
    # Ejemplo combate: si hp bajo, huir
    if estado.get("hp_mago", 99) < 5 and "huir" in opciones:
        return {"choice": "huir", "confidence": 0.9}
    return {"choice": opciones[0], "confidence": 0.7}

def decidir_con_tinyjev(estado: dict, pregunta: str, opciones: list):
    from tinyjev import load
    juez = load("TinyJev-0.6B")
    texto_estado = str(estado)  # ej: "{'hp_mago': 14, 'xeno': 'F5'}"
    r = juez.decide(state=texto_estado, pregunta=pregunta, opciones=opciones)
    return {"choice": r.choice, "confidence": float(r.confidence)}

def decidir(estado, pregunta, opciones):
    if DECIDOR == "tinyjev":
        return decidir_con_tinyjev(estado, pregunta, opciones)
    return decidir_con_reglas(estado, pregunta, opciones)

if __name__ == "__main__":
    # Prueba 1: spawn
    print(decidir({"cantidad_total": 23}, "¿qué dado para spawn?", ["dado"]))
    # Prueba 2: combate
    print(decidir({"hp_mago": 3}, "¿qué hace el mago?", ["atacar", "huir", "curar"]))
    # Regla de mesa:
    # >=0.85 hazlo solo / 0.60-0.85 hazlo y marca / <0.60 pregunta al humano
