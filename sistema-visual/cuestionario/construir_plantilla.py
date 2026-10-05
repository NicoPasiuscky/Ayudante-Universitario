"""construir_plantilla.py - arma cuestionario/Plantilla-Cuestionario.html a partir
de cuestionario/plantilla-fuente.html, incrustando las fuentes (base64) y
css/cuestionario.css. La plantilla resultante queda autocontenida y con los
mismos marcadores de siempre para el flujo `cuestionario`.

Correr de nuevo si se edita la plantilla fuente o el CSS:
    python cuestionario/construir_plantilla.py
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(RAIZ, "herramientas"))
sys.dont_write_bytecode = True
from construir_fuentes import css_fuentes  # noqa: E402

MARCADORES = ("{{ACCENT}}", "{{TITULO_PAGINA}}", "{{KICKER}}", "{{H1}}", "{{PREGUNTA_HERO}}",
              "{{LEDE}}", "{{QUIZ_LEN}}", "{{LS_KEY}}", "/* CUESTIONARIO_JSON_START */",
              "/* CUESTIONARIO_JSON_END */")

if __name__ == "__main__":
    fuente = open(os.path.join(AQUI, "plantilla-fuente.html"), encoding="utf-8").read()
    css = open(os.path.join(RAIZ, "css", "cuestionario.css"), encoding="utf-8").read()
    assert fuente.count("/*@@FUENTES@@*/") == 1 and fuente.count("/*@@CSS@@*/") == 1
    # Sin mono (no hay codigo); con la fuente matematica: las formulas $...$ se dibujan como MathML
    salida = fuente.replace("/*@@FUENTES@@*/", css_fuentes(con_mono=False, con_mate=True)).replace("/*@@CSS@@*/", css)
    for m in MARCADORES:
        assert m in salida, m
    ruta = os.path.join(AQUI, "Plantilla-Cuestionario.html")
    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write(salida)
    print(os.path.relpath(ruta, RAIZ), round(os.path.getsize(ruta) / 1024), "KB")
