"""imprimir_a4.py - imprime un HTML A4 (Paged.js) a PDF con navegador sin interfaz,
via Marionette. Reusa la clase Navegador de captura_espera.py.

El PDF es un formato de entrega del proyecto: un
resumen en Hoja A4, un TP, un parcial o una hoja de soluciones pueden
salir en HTML, en PDF o en .docx (el cuestionario, solo HTML). No es un generador aparte:
es el mismo HTML A4 impreso por el navegador. `entregar()` deja el PDF (y el HTML, si se
pide) en la carpeta de salida, con el titulo del PDF igual al nombre base. Como
artefacto de verificacion (herramientas/verificar_margenes.py lo mide) va al
directorio temporal.

Mismo mecanismo que "Imprimir" del navegador: A4 (21 x 29,7 cm), margenes de
pagina en cero (los margenes de carpeta los dan los @page del CSS), escala 100 %,
sin encabezados ni pies, con fondos. Espera a que Paged.js termine de armar las
hojas (document.documentElement.dataset.paginado == '1') antes de imprimir.
El PDF sale con las fuentes incrustadas y las formulas nitidas; el ancho de la
pagina sale 210,3 mm, una diferencia despreciable.

Uso:
    python herramientas/imprimir_a4.py demo/parcial.html               -> <temp>/v4_impresion/parcial.pdf
    python herramientas/imprimir_a4.py demo/parcial.html salida.pdf    -> salida.pdf
    python herramientas/imprimir_a4.py --todo                          todas las piezas A4 de demo/ al temporal
    python herramientas/imprimir_a4.py --entregar x.html "<carpeta de salida>" "<nombre base>" [--salida html|html+pdf|pdf] [--sin-espejo]
        deja en la carpeta de salida el PDF (y el HTML si la salida es html o html+pdf) con el
        nombre base dado (el de herramientas/nombres.py) y el titulo del PDF = nombre base;
        --sin-espejo exige que el HTML se haya armado con margenes iguales (no se imprime); sin la
        opcion se entrega el HTML tal cual esta armado (espejado por defecto)
Como modulo:
    import imprimir_a4
    pdf, hojas = imprimir_a4.pdf_de("demo/parcial.html")   # con cache: reimprime solo si el HTML cambio
    imprimir_a4.entregar("x.html", carpeta, base, salida="html+pdf", espejo=True)   # entrega en la carpeta de salida
    imprimir_a4.espejo_de("x.html")   # True: espejado (se imprime); False: margenes iguales (no se imprime)
"""
import base64
import json
import os
import pathlib
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
from captura_espera import Navegador  # noqa: E402

TEMPORAL = os.path.join(tempfile.gettempdir(), "v4_impresion")
PAGINADO = "document.documentElement.dataset.paginado=='1'"
HOJAS = "return document.querySelectorAll('.pagedjs_page').length;"

# Piezas A4 del sistema (relativas a v4/): resumenes y material impreso
PIEZAS_A4 = ["demo/resumen-extenso-a4.html", "demo/resumen-corto-a4.html", "demo/parcial.html",
             "demo/soluciones-resultados.html", "demo/soluciones-resolucion.html",
             "demo/tp.html"]


def imprimir(ff, html, pdf, maximo=180):
    """Imprime `html` en `pdf` con la sesion del navegador `ff`. Devuelve la cantidad
    de hojas que armo Paged.js."""
    url = pathlib.Path(os.path.abspath(html)).as_uri()
    ff.ventana(1280, 900)
    ff.ir(url)
    ff.esperar("document.readyState=='complete'")
    ff.js("return document.fonts.ready.then(function(){return 1});")
    if not ff.esperar(PAGINADO, maximo=maximo):
        raise SystemExit(f"Paged.js no termino de armar las hojas de {html}")
    hojas = ff.js(HOJAS)
    datos = ff.pdf()
    os.makedirs(os.path.dirname(os.path.abspath(pdf)), exist_ok=True)
    with open(pdf, "wb") as f:
        f.write(datos)
    return hojas


def poner_titulo(pdf, titulo):
    """Pone el titulo del PDF (metadato Title) y borra el resto de los metadatos que
    agrega el navegador. PyMuPDF solo se usa para esto."""
    import pymupdf
    tmp = pdf + ".tmp"
    with pymupdf.open(pdf) as doc:
        doc.set_metadata({"title": titulo, "author": "", "subject": "", "keywords": "", "creator": "", "producer": ""})
        doc.save(tmp, garbage=3, deflate=True)
    os.replace(tmp, pdf)


SALIDAS = ("html", "html+pdf", "pdf")


def espejo_de(html):
    """True si el HTML A4 se armo con margenes espejados (doble faz, para imprimir) o False si se
    armo sin espejo (-M espejo=false: margenes iguales en todas las hojas; incluir/espejo.lua lo
    marca con data-espejo="no")."""
    with open(html, encoding="utf-8") as f:
        return "setAttribute('data-espejo','no')" not in f.read()


def entregar(html, carpeta, base, salida="html+pdf", ff=None, espejo=None):
    """Deja en `carpeta` la salida pedida de un HTML A4 ya armado (normalmente en el
    directorio temporal): `base`.html y/o `base`.pdf, con el mismo nombre base (el de
    herramientas/nombres.py) y el titulo del PDF igual a `base`. salida: "html",
    "html+pdf" o "pdf" (con "pdf" el HTML no se copia y en la carpeta queda solo el
    PDF). Devuelve la lista de rutas escritas y la cantidad de hojas del PDF (None si
    no hay PDF).
    espejo: margenes espejados (True, por defecto: se imprime a doble faz) o iguales en todas las
    hojas (False: no se imprime). Es una propiedad del HTML, que ya sale armado con uno u otro
    (pandoc -M espejo=false; construir.resumen/material/tp(espejo=False)): aca se comprueba que
    coincida con lo pedido y falla si no (None = el que tenga el HTML)."""
    if salida not in SALIDAS:
        raise SystemExit(f"salida no valida: {salida!r} (validas: {', '.join(SALIDAS)})")
    real = espejo_de(html)
    if espejo is not None and bool(espejo) != real:
        raise SystemExit(f"{html} se armo {'con' if real else 'sin'} margenes espejados y se pidio "
                         f"espejo={bool(espejo)}: volver a armarlo con espejo={bool(espejo)} (pandoc -M espejo=false)")
    os.makedirs(carpeta, exist_ok=True)
    escritas, hojas = [], None
    if "pdf" in salida:
        pdf = os.path.join(carpeta, base + ".pdf")
        if ff is None:
            with Navegador("claro") as f:
                hojas = imprimir(f, html, pdf)
        else:
            hojas = imprimir(ff, html, pdf)
        poner_titulo(pdf, base)
        escritas.append(pdf)
    if salida.startswith("html"):
        destino = os.path.join(carpeta, base + ".html")
        shutil.copyfile(html, destino)
        escritas.insert(0, destino)
    return escritas, hojas


def pdf_de(html, forzar=False, ff=None):
    """PDF temporal de `html`, con cache: se reimprime solo si el HTML es mas nuevo.
    Devuelve (ruta del PDF, hojas armadas por Paged.js)."""
    html = html if os.path.isabs(html) else os.path.join(RAIZ, html)
    nombre = os.path.splitext(os.path.basename(html))[0]
    pdf = os.path.join(TEMPORAL, nombre + ".pdf")
    meta = pdf + ".json"
    if not forzar and os.path.exists(pdf) and os.path.exists(meta) and os.path.getmtime(pdf) >= os.path.getmtime(html):
        return pdf, json.load(open(meta, encoding="utf-8"))["hojas"]
    if ff is None:
        with Navegador("claro") as f:
            hojas = imprimir(f, html, pdf)
    else:
        hojas = imprimir(ff, html, pdf)
    with open(meta, "w", encoding="utf-8") as fh:
        json.dump({"hojas": hojas}, fh)
    return pdf, hojas


def pdfs_de(htmls, forzar=False):
    """Varias piezas con una sola sesion del navegador: {html: (pdf, hojas)}."""
    out = {}
    with Navegador("claro") as ff:
        for h in htmls:
            out[h] = pdf_de(h, forzar=forzar, ff=ff)
    return out


if __name__ == "__main__":
    argv = sys.argv[1:]
    if "--entregar" in argv:
        salida = "html+pdf"
        sin_espejo = "--sin-espejo" in argv
        if "--salida" in argv:
            i = argv.index("--salida")
            salida = argv[i + 1]
            del argv[i:i + 2]
        pos = [x for x in argv if not x.startswith("--")]
        if len(pos) != 3:
            raise SystemExit(__doc__)
        rutas, n = entregar(pos[0], pos[1], pos[2], salida, espejo=False if sin_espejo else None)
        for r_ in rutas:
            print(r_ + (f"  ({n} hojas)" if r_.endswith(".pdf") else ""))
        sys.exit(0)
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if "--todo" in sys.argv:
        for h, (pdf, n) in pdfs_de(PIEZAS_A4, forzar=True).items():
            print(f"{h}: {n} hojas -> {pdf}")
    elif a:
        if len(a) > 1:
            with Navegador("claro") as f:
                n = imprimir(f, a[0], a[1])
            poner_titulo(a[1], os.path.splitext(os.path.basename(a[1]))[0])
            print(f"{a[0]}: {n} hojas -> {a[1]}")
        else:
            pdf, n = pdf_de(a[0], forzar=True)
            print(f"{a[0]}: {n} hojas -> {pdf}")
    else:
        raise SystemExit(__doc__)
