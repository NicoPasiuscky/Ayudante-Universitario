"""verificar_margenes.py - regla 22: nada fuera del area imprimible.

Margenes de carpeta (css/tokens.css),
doble faz espejada: interior 20 mm, exterior 10 mm, superior 15 mm, inferior
5 mm. En una hoja impar el interior es el borde izquierdo; en una par, el
derecho.

Para cada hoja de cada salida A4 mide la distancia de TODO lo visible (texto,
imagenes, filetes, recuadros, marcas) a cada borde fisico y falla si algo queda
mas cerca que el margen de ese lado. No cuentan los rectangulos de fondo de
pagina (mas del 90 % de la hoja). Unica excepcion, de diseño:
la cabeza de hoja (sigla o asignatura y "Hoja n de N") vive en la franja del
margen superior; ahi se exige que no invada los margenes laterales y que quede
a 5 mm o mas del borde de arriba (la misma distancia que el margen inferior,
que muchas impresoras imprimen bien).

Salidas medidas:
  - Todas las hojas A4 (Paged.js): herramientas/imprimir_a4.py imprime cada HTML a
    PDF con el navegador (al directorio temporal, con cache: solo reimprime lo que
    cambio) y aca se mide ese PDF con PyMuPDF (get_text("rawdict"),
    get_drawings, get_image_info): resumen extenso y corto en hoja A4, parcial
    digitalizado, las dos hojas de soluciones y el TP. Ese
    PDF es solo un artefacto de verificacion, nunca un formato del proyecto.
  - docx/demo/tp-demo.pdf (el .docx exportado por Word con
    herramientas/captura_docx.py, si existe).
  Las diapositivas no se imprimen: no se miden (no hay folleto ni giro de margenes).

Uso:  python herramientas/verificar_margenes.py      (tabla y codigo 1 si algo invade)
      python herramientas/verificar_margenes.py x.html|x.pdf ...    piezas sueltas
Tambien lo llama verificar_reglas.py (regla 22). PyMuPDF ya no genera nada: solo mide.
"""
import os
import sys

import pymupdf

sys.dont_write_bytecode = True
AQUI = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(AQUI)
MM = 72 / 25.4
sys.path.insert(0, AQUI)
import margenes as _mg  # noqa: E402  (valores de css/tokens.css)

MARGEN = {"interior": _mg.MM["interior"], "exterior": _mg.MM["exterior"],
          "arriba": _mg.MM["superior"], "abajo": _mg.MM["inferior"]}
CABEZA_MIN = 5.0          # mm desde el borde superior para la cabeza de hoja
TOL = 0.1                 # mm de tolerancia de medicion
TOL_LIBREOFFICE = 1.0     # un .docx exportado con LibreOffice coloca la cabeza de hoja distinto que Word (hasta ~1 mm)
# (nombre, HTML A4 relativo a v4/): se imprimen con imprimir_a4.py
HTML_A4 = [("resumen extenso, hoja A4", "demo/resumen-extenso-a4.html"),
           ("resumen corto, hoja A4", "demo/resumen-corto-a4.html"),
           ("parcial digitalizado, hoja A4", "demo/parcial.html"),
           ("soluciones, resultados, hoja A4", "demo/soluciones-resultados.html"),
           ("soluciones, resolución, hoja A4", "demo/soluciones-resolucion.html"),
           ("TP en HTML, hoja A4", "demo/tp.html")]
PDFS = [("TP en Word (docx exportado)", "docx/demo/tp-demo.pdf", True),
        ("resumen extenso en Word (docx exportado)", "docx/demo/resumen-extenso.pdf", True),
        ("parcial en Word (docx exportado)", "docx/demo/parcial.pdf", True),
        ("soluciones, resolucion, en Word (docx exportado)", "docx/demo/soluciones-resolucion.pdf", True)]
FONDO = 0.9               # un rectangulo de mas del 90 % de la hoja es el fondo de pagina, no contenido


def limites(i, espejo=True):
    """(izquierdo, derecho) exigidos en la hoja de indice i (0 = hoja 1, impar). Sin espejo
    (documento que no se imprime): interior a la izquierda y exterior a la derecha en todas."""
    if i % 2 == 0 or not espejo:
        return MARGEN["interior"], MARGEN["exterior"]
    return MARGEN["exterior"], MARGEN["interior"]


def _es_blanco(c):
    return c is None or all(v > 0.98 for v in c)


def cajas_pdf(pg):
    """Rectangulos (x0, y0, x1, y1) en puntos de todo lo visible de la hoja."""
    out = []
    # texto caracter por caracter, sin los espacios (Word deja un espacio
    # final invisible en cada renglon justificado, que asoma al margen)
    for b in pg.get_text("rawdict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                caja = pymupdf.Rect()
                for c in s["chars"]:
                    if c["c"].strip():
                        caja |= pymupdf.Rect(c["bbox"])
                if not caja.is_empty:
                    out.append(("texto", caja))
    for im in pg.get_image_info():
        out.append(("imagen", pymupdf.Rect(im["bbox"])))
    for d in pg.get_drawings():
        trazo = d.get("color")
        relleno = d.get("fill")
        if _es_blanco(trazo) and _es_blanco(relleno):
            continue
        r = pymupdf.Rect(d["rect"])
        if r.width * r.height > FONDO * pg.rect.width * pg.rect.height:
            continue
        w = (d.get("width") or 0) / 2 if not _es_blanco(trazo) else 0
        out.append(("trazo", r + (-w, -w, w, w)))
    return [(t, r) for t, r in out if not r.is_empty or r.width > 0 or r.height > 0]


def medir_pdf(ruta, con_cabeza, hojas_esperadas=None, espejo=True):
    doc = pymupdf.open(ruta)
    tol = TOL_LIBREOFFICE if "libreoffice" in (doc.metadata.get("producer") or "").lower() else TOL
    hojas = []
    for i, pg in enumerate(doc):
        W, H = pg.rect.width, pg.rect.height
        cuerpo, cabeza = [], []
        for tipo, r in cajas_pdf(pg):
            dist = {"izq": r.x0 / MM, "der": (W - r.x1) / MM, "arr": r.y0 / MM, "aba": (H - r.y1) / MM}
            if con_cabeza and r.y1 / MM <= MARGEN["arriba"] + tol:
                cabeza.append(dist)
            else:
                cuerpo.append(dist)
        hojas.append(resumir(i, cuerpo, cabeza, espejo, tol))
    if hojas_esperadas is not None and len(doc) != hojas_esperadas:
        hojas[0]["fallas"].append(f"el PDF tiene {len(doc)} hojas y Paged.js armó {hojas_esperadas}")
    doc.close()
    return hojas


def resumir(i, cuerpo, cabeza, espejo=True, tol=TOL):
    izq, der = limites(i, espejo)
    m = {k: round(min((d[k] for d in cuerpo), default=99), 1) for k in ("izq", "der", "arr", "aba")}
    c = {k: round(min((d[k] for d in cabeza), default=99), 1) for k in ("izq", "der", "arr")}
    fallas = []
    for k, lim in (("izq", izq), ("der", der), ("arr", MARGEN["arriba"]), ("aba", MARGEN["abajo"])):
        if m[k] < lim - tol:
            fallas.append(f"hoja {i + 1}: contenido a {m[k]} mm del borde {k} (margen {lim})")
    if cabeza:
        for k, lim in (("izq", izq), ("der", der), ("arr", CABEZA_MIN)):
            if c[k] < lim - tol:
                fallas.append(f"hoja {i + 1}: cabeza a {c[k]} mm del borde {k} (minimo {lim})")
    return {"hoja": i + 1, "cuerpo": m, "cabeza": c if cabeza else None, "fallas": fallas, "espejo": espejo}


def minimos(hojas):
    """Minimo por lado, separando interior y exterior segun la paridad."""
    out = {"interior": 99, "exterior": 99, "arriba": 99, "abajo": 99, "cabeza": 99}
    for h in hojas:
        i = h["hoja"] - 1
        m = h["cuerpo"]
        inte, exte = (m["izq"], m["der"]) if i % 2 == 0 or not h.get("espejo", True) else (m["der"], m["izq"])
        out["interior"] = min(out["interior"], inte)
        out["exterior"] = min(out["exterior"], exte)
        out["arriba"] = min(out["arriba"], m["arr"])
        out["abajo"] = min(out["abajo"], m["aba"])
        if h["cabeza"]:
            out["cabeza"] = min(out["cabeza"], h["cabeza"]["arr"])
    return out


def sin_espejo():
    """Arma en el temporal las piezas A4 con margenes iguales (-M espejo=false) y las imprime con
    Navegador: [(nombre, html, hojas, pdf)]. No toca demo/."""
    import tempfile
    sys.path.insert(0, R)
    import construir as c
    import imprimir_a4
    t = os.path.join(tempfile.gettempdir(), "v4_sin_espejo")
    os.makedirs(t, exist_ok=True)
    armar = [
        ("resumen extenso, hoja A4, sin espejo", "resumen-extenso-a4.html",
         lambda o: c.resumen(c.r("demo", "resumen-extenso.md"), o, "a4", "extenso", indice=True, espejo=False)),
        ("resumen corto, hoja A4, sin espejo", "resumen-corto-a4.html",
         lambda o: c.resumen(c.r("demo", "resumen-corto.md"), o, "a4", "corto", espejo=False)),
        ("parcial digitalizado, sin espejo", "parcial.html",
         lambda o: c.material(c.r("demo", "material", "parcial.md"), o, espejo=False)),
        ("soluciones, resolución, sin espejo", "soluciones-resolucion.html",
         lambda o: c.material(c.r("demo", "material", "soluciones-resolucion.md"), o, espejo=False)),
        ("TP en HTML, sin espejo", "tp.html",
         lambda o: c.tp(c.r("docx", "demo", "tp-demo.md"), o, datos=c.r("docx", "demo", "tp-demo.json"), espejo=False)),
    ]
    out = []
    with imprimir_a4.Navegador("claro") as ff:
        for nombre, archivo, f in armar:
            h = os.path.join(t, archivo)
            f(h)
            pdf = h[:-5] + ".pdf"
            n = imprimir_a4.imprimir(ff, h, pdf)
            if imprimir_a4.espejo_de(h):
                raise SystemExit(f"{nombre}: el HTML no quedo marcado sin espejo")
            out.append((nombre, h, n, pdf))
    return out


def verificar():
    """Devuelve (filas de la tabla, fallas, piezas sin medir)."""
    filas, fallas, faltan = [], [], []
    piezas = []
    import imprimir_a4  # noqa: E402  (necesita un navegador; solo reimprime lo que cambio)
    existentes = [(n, h) for n, h in HTML_A4 if os.path.exists(os.path.join(R, h))]
    faltan += [n for n, h in HTML_A4 if not os.path.exists(os.path.join(R, h))]
    hechos = imprimir_a4.pdfs_de([h for _, h in existentes]) if existentes else {}
    for nombre, h in existentes:
        pdf, n = hechos[h]
        piezas.append((nombre, medir_pdf(pdf, True, n)))
    # Sin espejo (el documento no se imprime): se arman al vuelo en el temporal, con
    # construir.py y -M espejo=false, y se exige 20 mm a la izquierda y 10 a la derecha en TODAS las hojas
    if existentes:
        for nombre, h, n, pdf in sin_espejo():
            piezas.append((nombre, medir_pdf(pdf, True, n, espejo=False)))
    for nombre, rel, cab in PDFS:
        ruta = os.path.join(R, rel)
        if os.path.exists(ruta):
            piezas.append((nombre, medir_pdf(ruta, cab)))
        else:
            faltan.append(nombre)
    for nombre, hojas in piezas:
        m = minimos(hojas)
        filas.append((nombre, len(hojas), m))
        for h in hojas:
            fallas += [f"{nombre}, {f}" for f in h["fallas"]]
    return filas, fallas, faltan


def tabla(filas):
    t = ["| Pieza | Hojas | Interior (20) | Exterior (10) | Superior (15) | Inferior (5) | Cabeza desde arriba (5) |",
         "|---|---|---|---|---|---|---|"]
    for nombre, n, m in filas:
        cab = "sin cabeza" if m["cabeza"] == 99 else f'{m["cabeza"]:.1f}'
        t.append(f'| {nombre} | {n} | {m["interior"]:.1f} | {m["exterior"]:.1f} | {m["arriba"]:.1f} | '
                 f'{m["abajo"]:.1f} | {cab} |')
    return "\n".join(t)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # PDF sueltos (por ejemplo el .docx de un TP real exportado con captura_docx.py)
        # o HTML A4, que se imprimen antes con imprimir_a4.py
        filas, fallas = [], []
        for ruta in sys.argv[1:]:
            n = None
            if ruta.lower().endswith(".html"):
                import imprimir_a4
                ruta, n = imprimir_a4.pdf_de(os.path.abspath(ruta), forzar=True)
            hojas = medir_pdf(ruta, True, n)
            filas.append((os.path.basename(ruta), len(hojas), minimos(hojas)))
            fallas += [f"{os.path.basename(ruta)}, {f}" for h in hojas for f in h["fallas"]]
        print(tabla(filas))
        for f in fallas:
            print("INVADE:", f)
        sys.exit(1 if fallas else 0)
    filas, fallas, faltan = verificar()
    print("Minimo medido por lado (mm; entre parentesis, el margen exigido)")
    print(tabla(filas))
    for f in faltan:
        print("SIN MEDIR:", f)
    for f in fallas:
        print("INVADE:", f)
    sys.exit(1 if fallas else 0)
