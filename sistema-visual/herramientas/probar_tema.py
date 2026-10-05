"""probar_tema.py - prueba en Firefox el modo claro u oscuro:

  * HTML completo y diapositivas: UN solo boton de tema; sin eleccion guardada siguen al
    sistema (claro u oscuro); un clic cambia el tema y los colores reales; se recuerda al
    recargar.
  * Hoja A4 del resumen y material impreso en HTML A4 (parcial, soluciones, TP):
    SIEMPRE claros y sin boton, aun con el tema oscuro del sistema; el HTML para imprimir
    es siempre hoja blanca con texto oscuro, sin modos de color (el PDF de prueba impreso
    con el tema oscuro del sistema sale igual).

Escribe el resultado en capturas/medidas.json, clave "tema"; lo lee verificar_reglas.py
(reglas 32 y 33). Los PDF de prueba van al directorio temporal.

Uso:  python herramientas/probar_tema.py
"""
import json
import os
import pathlib
import re
import sys
import tempfile

sys.dont_write_bytecode = True
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
from captura_espera import Firefox  # noqa: E402
import imprimir_a4  # noqa: E402
import pymupdf  # noqa: E402

TEMP = os.path.join(tempfile.gettempdir(), "v4_impresion")
COMPLETO = "demo/resumen-extenso-completo.html"
DIAPOS = "demo/resumen-extenso-diapositivas.html"
A4S = {"resumen A4": "demo/resumen-extenso-a4.html", "parcial": "demo/parcial.html",
       "soluciones": "demo/soluciones-resolucion.html", "tp": "demo/tp.html"}
FONDO = "var b=getComputedStyle(document.body).backgroundColor;if(!b||b==='rgba(0, 0, 0, 0)')b=getComputedStyle(document.documentElement).backgroundColor;return b;"


def luz(rgb):
    n = [int(x) for x in re.findall(r"\d+", rgb)[:3]]
    return round(n[0] * .2126 + n[1] * .7152 + n[2] * .0722)


def ir(ff, rel, espera=None):
    url = pathlib.Path(os.path.join(RAIZ, rel)).as_uri()
    ff.cmd("WebDriver:SetWindowRect", {"width": 1280, "height": 900})
    ff.cmd("WebDriver:Navigate", {"url": url})
    ff.esperar("document.readyState=='complete'")
    ff.js("try{localStorage.removeItem('estudio-v4-tema')}catch(e){} return 1;")
    ff.cmd("WebDriver:Refresh", {})
    ff.esperar("document.readyState=='complete'")
    if espera:
        ff.esperar(espera, maximo=120)


def boton(ff, rel, nombre, sistema, res):
    """Sin eleccion guardada sigue al sistema; un clic cambia; se recuerda al recargar."""
    ir(ff, rel)
    n = ff.js("return document.querySelectorAll('#temaBoton,.tema-boton').length")
    inicio = luz(ff.js(FONDO))
    ff.js("document.getElementById('temaBoton').click(); return 1;")
    tras = luz(ff.js(FONDO))
    tema = ff.js("return document.documentElement.getAttribute('data-theme')")
    ff.cmd("WebDriver:Refresh", {})
    ff.esperar("document.readyState=='complete'")
    recuerda = ff.js("return document.documentElement.getAttribute('data-theme')")
    despues = luz(ff.js(FONDO))
    ff.js("try{localStorage.removeItem('estudio-v4-tema')}catch(e){} return 1;")
    res[f"{nombre}, sistema {sistema}"] = {
        "botones": n, "fondo_inicial": inicio, "fondo_tras_clic": tras, "tema_tras_clic": tema,
        "recuerda": recuerda, "fondo_tras_recargar": despues}


def analizar_pdf(pdf):
    doc = pymupdf.open(pdf)
    claros = total = 0
    fondos = []
    for pg in doc:
        for b in pg.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    if s["text"].strip():
                        total += 1
                        c = s["color"]
                        if ((c >> 16) & 255) * .2126 + ((c >> 8) & 255) * .7152 + (c & 255) * .0722 > 160:
                            claros += 1
        pix = pg.get_pixmap(dpi=30)
        fondos.append(pix.pixel(2, 2))
    n = len(doc)
    doc.close()
    return {"hojas": n, "spans": total, "spans_claros": claros,
            "esquinas_blancas": all(min(p[:3]) > 250 for p in fondos)}


def main():
    res = {}
    with Firefox("oscuro") as ff:
        boton(ff, COMPLETO, "HTML completo", "oscuro", res)
        boton(ff, DIAPOS, "diapositivas", "oscuro", res)
        for nombre, rel in A4S.items():
            ir(ff, rel, imprimir_a4.PAGINADO)
            pagina = ff.js("var p=document.querySelector('.pagedjs_page');return p?getComputedStyle(p).backgroundColor:null")
            res[f"{nombre}, sistema oscuro"] = {
                "botones": ff.js("return document.querySelectorAll('#temaBoton,.tema-boton').length"),
                "fondo_mesa": luz(ff.js(FONDO)), "fondo_hoja": luz(pagina),
                "texto": luz(ff.js("return getComputedStyle(document.querySelector('.pagedjs_page_content p, .pagedjs_page_content h1, .pagedjs_page_content h2')).color")),
                "data_theme": ff.js("return document.documentElement.getAttribute('data-theme')")}
            pdf = os.path.join(TEMP, "oscuro_" + os.path.basename(rel).replace(".html", ".pdf"))
            imprimir_a4.imprimir(ff, os.path.join(RAIZ, rel), pdf)
            res[f"{nombre}, PDF con sistema oscuro"] = analizar_pdf(pdf)
    with Firefox("claro") as ff:
        boton(ff, COMPLETO, "HTML completo", "claro", res)
        boton(ff, DIAPOS, "diapositivas", "claro", res)
    ruta = os.path.join(RAIZ, "capturas", "medidas.json")
    medidas = json.load(open(ruta, encoding="utf-8")) if os.path.exists(ruta) else {}
    medidas["tema"] = res
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(medidas, f, ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
