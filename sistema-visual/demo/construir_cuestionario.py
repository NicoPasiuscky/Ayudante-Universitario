"""Arma demo/cuestionario.html igual que el flujo `cuestionario`: copia la
plantilla, reemplaza los marcadores y el bloque JSON. Banco de demostracion:
5 preguntas de los 3 tipos sobre la unidad 3 de demostración (resumen-extenso.md),
con el mismo formato de entrada que produce el agente cuestionador."""
import json
import os

D = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(D)

PREGUNTAS = [
    {"id": "u3-001", "unit": 3, "type": "mc-single",
     "question": "Con los datos de la tabla de la muestra (A: t = 0 min, y = 30 °C; F: t = 50 min, y = −53 °C), ¿cuánto vale la tasa de variación promedio entre A y F?",
     "options": ["−1,7 °C/min", "1,7 °C/min", "2,5 °C/min", "−0,6 °C/min"], "correct": [0],
     "explanation": "Es la variación neta sobre el intervalo: (−53 °C − 30 °C) / (50 min − 0 min) = −83 °C / 50 min = −1,7 °C/min. El signo indica que la temperatura bajó en neto."},
    {"id": "u3-002", "unit": 3, "type": "mc-multi",
     "question": "¿Cuáles de estas magnitudes pueden ser negativas?",
     "options": ["El valor de una magnitud", "La variación neta", "La tasa de variación total", "La tasa de variación promedio"], "correct": [0, 1, 3],
     "explanation": "El valor, la variación neta y la tasa promedio tienen signo. La tasa de variación total suma cambios en valor absoluto, así que nunca es negativa."},
    {"id": "u3-003", "unit": 3, "type": "tf",
     "question": "La variación neta de una magnitud depende de todos los valores intermedios por los que pasó.",
     "options": ["Verdadero", "Falso"], "correct": [1],
     "explanation": "Solo depende del valor inicial y del final. Lo que depende de todo el recorrido es la variación total."},
    {"id": "u3-004", "unit": 3, "type": "tf",
     "question": "Una muestra que sube 30 °C y después baja 30 °C tiene tasa de variación promedio cero.",
     "options": ["Verdadero", "Falso"], "correct": [0],
     "explanation": "Su variación neta es cero, así que la tasa promedio es cero, aunque la tasa total no lo sea."},
    {"id": "u3-005", "unit": 3, "type": "mc-single",
     "question": "En una gráfica del valor en función del tiempo, ¿qué representa la pendiente de la recta que une dos puntos?",
     "options": ["La tasa de variación total en ese intervalo", "La tasa de variación promedio en ese intervalo",
                 "La variación neta", "El valor medio"], "correct": [1],
     "explanation": "La recta entre dos puntos es la hipotenusa de un triángulo de altura Δy y base Δt: su pendiente es Δy/Δt, la tasa promedio."},
    # Tipos de la plantilla ampliada: formulas, tabla, respuesta numerica, V o F por items, completar y partes
    {"id": "u3-006", "unit": 3, "type": "numeric",
     "question": "Una muestra varía $-83$ °C en $50$ min. ¿Cuánto vale la tasa de variación promedio, en °C/min?",
     "answer": -1.66, "decimals": 2, "tolerance": 0.01, "answerUnit": "°C/min",
     "explanation": "$\\bar{r} = \\frac{\\Delta y}{\\Delta t} = \\frac{-83}{50} = -1{,}66$ °C/min."},
    {"id": "u3-007", "unit": 3, "type": "tf-items",
     "question": "Marcá Verdadero o Falso en cada caso.",
     "items": [{"text": "La variación neta es la diferencia entre el valor final y el inicial.", "correct": True},
               {"text": "La tasa de variación total es $\\frac{\\Delta y}{\\Delta t}$.", "correct": False}],
     "explanation": "La tasa total usa la suma de los cambios en valor absoluto, no la variación neta."},
    {"id": "u3-008", "unit": 3, "type": "cloze",
     "question": "La tasa de variación promedio [[1]] signo y la tasa de variación total [[2]] signo.",
     "blanks": [{"options": ["tiene", "no tiene"], "correct": 0}, {"options": ["tiene", "no tiene"], "correct": 1}],
     "explanation": "La tasa promedio hereda el signo de la variación neta; la total es siempre mayor o igual que cero."},
    {"id": "u3-009", "unit": 3, "type": "group",
     "question": "Con las mediciones de la tabla, respondé las dos partes.",
     "table": {"caption": "Temperatura de la muestra", "head": ["$t$ (min)", "$y$ (°C)"], "rows": [["0", "30"], ["50", "−53"]], "align": ["c", "c"]},
     "parts": [{"type": "numeric", "question": "Variación neta entre $t = 0$ y $t = 50$ min, en °C.", "answer": -83, "decimals": 0, "tolerance": 0,
                "explanation": "$-53 - 30 = -83$ °C."},
               {"type": "mc-single", "question": "En neto, la temperatura:", "options": ["Bajó", "Subió"], "correct": [0],
                "explanation": "La variación neta es negativa."}],
     "explanation": "Se usa $\\Delta y = y_f - y_i$."},
]

if __name__ == "__main__":
    t = open(os.path.join(RAIZ, "cuestionario", "Plantilla-Cuestionario.html"), encoding="utf-8").read()
    rep = {"{{ACCENT}}": "#1C3F94",
           "{{TITULO_PAGINA}}": "Cuestionario de demostración, Materia de ejemplo",
           "{{KICKER}}": "<b>Materia de ejemplo</b>, cuestionario de demostración del sistema visual",
           "{{H1}}": "Variación y tasa de cambio",
           "{{PREGUNTA_HERO}}": "¿Cuánto recordás de variación y tasa de cambio?",
           "{{LEDE}}": "Nueve preguntas de demostración sobre la unidad 3 de demostración, de todos los tipos: opción múltiple, selección múltiple, verdadero o falso, respuesta numérica, verdadero o falso por ítems, completar y varias partes. No es un banco real de la materia.",
           "{{QUIZ_LEN}}": "5", "{{LS_KEY}}": "demo_v4_ejemplo_best_score"}
    for k, v in rep.items():
        t = t.replace(k, v)
    a = t.index("/* CUESTIONARIO_JSON_START */") + len("/* CUESTIONARIO_JSON_START */")
    b = t.index("/* CUESTIONARIO_JSON_END */")
    t = t[:a] + "\nwindow.QUESTIONS = " + json.dumps(PREGUNTAS, ensure_ascii=False, indent=1) + ";\n" + t[b:]
    assert "{{" not in t
    with open(os.path.join(D, "cuestionario.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(t)
    print("demo/cuestionario.html", len(PREGUNTAS), "preguntas")
