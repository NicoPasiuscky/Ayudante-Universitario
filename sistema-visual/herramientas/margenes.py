"""margenes.py - margenes de carpeta, leidos de css/tokens.css
(--hoja-interior, --hoja-exterior, --hoja-superior, --hoja-inferior), que es
la unica fuente de valores para todo lo imprimible: las hojas A4 en HTML (los @page
de los CSS, que repiten estos numeros), Word (docx/construir_docx.py) y las reglas 22
y 23 de verificar_reglas.py.

Uso:
    import margenes
    margenes.MM   -> {"interior": 20.0, "exterior": 10.0, "superior": 15.0, "inferior": 5.0}
    margenes.util_a4()  -> (ancho, alto) util de la hoja A4 en mm: 180 x 277
"""
import os
import re

_TOKENS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "css", "tokens.css")


def leer(ruta=_TOKENS):
    css = open(ruta, encoding="utf-8").read()
    out = {}
    for lado in ("interior", "exterior", "superior", "inferior"):
        m = re.search(r"--hoja-" + lado + r"\s*:\s*([0-9.]+)mm", css)
        if not m:
            raise SystemExit(f"tokens.css: falta --hoja-{lado}")
        out[lado] = float(m.group(1))
    return out


MM = leer()


def util_a4():
    """Area util de una hoja A4 con estos margenes, en mm (ancho, alto)."""
    return 210 - MM["interior"] - MM["exterior"], 297 - MM["superior"] - MM["inferior"]
