"""construir_fuentes.py - fuentes del sistema v4 (todas OFL 1.1, ver LEEME.md).

A partir de fonts/originales genera:

  fonts/web/*.woff       subconjuntos para pantalla (latin, latin extendido,
                         griego, puntuacion, operadores matematicos), WOFF zlib
  incluir/fuentes.html   los @font-face con las WOFF incrustadas en base64, como
                         include de cabecera para Pandoc: los HTML quedan
                         autocontenidos, sin pedir nada a internet
  fonts/graficos/*.ttf   Alegreya Sans con las cifras de caja alta (lining) como
                         cifras por defecto, para los graficos de Matplotlib y el
                         .docx (herramientas/graficos_v4.py, docx/construir_docx.py).
                         Alegreya Sans trae por defecto cifras de estilo antiguo
                         (con ascendentes y descendentes); en HTML se corrige con
                         font-variant-numeric, pero Matplotlib y Word no aplican
                         rasgos OpenType: se reescribe el mapa de caracteres para
                         que 0-9 apunten a las cifras de caja alta. Familia
                         "Estudio Sans PDF" (nombre historico interno; ya no hay
                         generador de PDF, y los archivos conservan ese nombre).

Familias que declara la pagina (nombres propios del sistema, para no chocar
con una Alegreya Sans instalada en la compu con otra version):
  "Estudio Sans"   Alegreya Sans 400, 400 italica, 500, 500 italica, 700, 700 italica, 800
  "Estudio Mono"   JetBrains Mono (solo codigo)
  "Estudio Mate"   Noto Sans Math recortada, con su tabla MATH (MathML en Firefox)
  "Estudio Marcas" visto, aspa y asterisco (U+2713, U+2717, U+2731) de Noto Sans Symbols 2

Uso:  python herramientas/construir_fuentes.py
"""
import base64
import os

from fontTools import subset
from fontTools.ttLib import TTFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O = os.path.join(RAIZ, "fonts", "originales")
WEB = os.path.join(RAIZ, "fonts", "web")
PDF = os.path.join(RAIZ, "fonts", "graficos")   # cifras de caja alta para Matplotlib y .docx
INC = os.path.join(RAIZ, "incluir", "fuentes.html")
os.makedirs(WEB, exist_ok=True)
os.makedirs(PDF, exist_ok=True)

TEXTO = ("U+0020-007E,U+00A0-00FF,U+0100-024F,U+02C6-02DC,U+0300-036F,U+0370-03FF,"
         "U+2000-206F,U+2070-209F,U+20AC,U+2100-215F,U+2190-21FF,U+2200-22FF,U+25A0-25FF,U+FB00-FB06")
FEATS = ["kern", "liga", "clig", "calt", "ccmp", "locl", "mark", "mkmk", "smcp", "c2sc",
         "onum", "lnum", "tnum", "pnum", "frac", "sups", "subs", "case", "ordn", "sinf", "numr", "dnom"]

ALEGREYA = [  # archivo original, peso, estilo
    ("AlegreyaSans-Regular.ttf", "400", "normal"),
    ("AlegreyaSans-Italic.ttf", "400", "italic"),
    ("AlegreyaSans-Medium.ttf", "500", "normal"),
    ("AlegreyaSans-MediumItalic.ttf", "500", "italic"),
    ("AlegreyaSans-Bold.ttf", "700", "normal"),
    ("AlegreyaSans-BoldItalic.ttf", "700", "italic"),
    ("AlegreyaSans-ExtraBold.ttf", "800", "normal"),
]
PARA_PDF = {"AlegreyaSans-Regular.ttf": "Regular", "AlegreyaSans-Italic.ttf": "Italic",
            "AlegreyaSans-Bold.ttf": "Bold", "AlegreyaSans-BoldItalic.ttf": "Bold Italic",
            "AlegreyaSans-ExtraBold.ttf": "ExtraBold"}


def rangos(spec):
    out = []
    for parte in spec.split(","):
        a, _, b = parte.replace("U+", "").partition("-")
        out.extend(range(int(a, 16), int(b or a, 16) + 1))
    return out


def recortar(origen, destino, unicodes, feats=FEATS, math=False):
    op = subset.Options()
    op.layout_features = feats
    op.flavor = "woff"
    op.name_IDs = ["*"]
    op.name_languages = ["*"]
    op.notdef_outline = True
    op.glyph_names = False
    op.hinting = False
    op.desubroutinize = True
    if math:
        op.layout_closure = True
    f = subset.load_font(origen, op)
    s = subset.Subsetter(op)
    s.populate(unicodes=unicodes)
    s.subset(f)
    subset.save_font(f, destino, op)
    return os.path.getsize(destino)


def marcas():
    return recortar(os.path.join(O, "NotoSansSymbols2-Regular.ttf"), os.path.join(WEB, "EstudioMarcas.woff"),
                    rangos("U+2713,U+2717,U+2731"), feats=["ccmp"])


def matematica():
    uni = rangos("U+0020-007E,U+00A0-00FF,U+0370-03FF,U+2000-206F,U+2070-209F,U+2100-214F,U+2190-21FF,"
                 "U+2200-22FF,U+2308-230B,U+27E8-27E9,U+1D400-1D433,U+1D6A8-1D6E1,U+1D7CE-1D7D7")
    return recortar(os.path.join(O, "NotoSansMath-Regular.ttf"), os.path.join(WEB, "EstudioMate.woff"), uni,
                    feats=["ssty", "flac", "dtls", "ccmp", "kern"], math=True)


def cifras_de_caja_alta(t):
    """Mapa de sustituciones del rasgo lnum (una sola por glifo)."""
    mapa = {}
    gsub = t["GSUB"].table
    for fr in gsub.FeatureList.FeatureRecord:
        if fr.FeatureTag != "lnum":
            continue
        for i in fr.Feature.LookupListIndex:
            lk = gsub.LookupList.Lookup[i]
            for st in lk.SubTable:
                if lk.LookupType == 7:
                    st = st.ExtSubTable
                if hasattr(st, "mapping"):
                    mapa.update(st.mapping)
    return mapa


def fuentes_pdf():
    """Alegreya Sans con cifras de caja alta por defecto, familia "Estudio Sans PDF"."""
    hechas = []
    for archivo, sub in PARA_PDF.items():
        t = TTFont(os.path.join(O, archivo))
        lnum = cifras_de_caja_alta(t)
        for tabla in t["cmap"].tables:
            if not tabla.isUnicode():
                continue
            for cp in range(0x30, 0x3A):
                g = tabla.cmap.get(cp)
                if g in lnum:
                    tabla.cmap[cp] = lnum[g]
        nt = t["name"]
        fam = "Estudio Sans PDF" if sub in ("Regular", "Italic", "Bold", "Bold Italic") else "Estudio Sans PDF ExtraBold"
        estilo = sub if fam == "Estudio Sans PDF" else "Regular"
        for pid, eid, lid in ((3, 1, 0x409), (1, 0, 0)):
            nt.setName(fam, 1, pid, eid, lid)
            nt.setName(estilo, 2, pid, eid, lid)
            nt.setName(f"{fam} {estilo}", 4, pid, eid, lid)
            nt.setName(f"{fam.replace(' ', '')}-{estilo.replace(' ', '')}", 6, pid, eid, lid)
        for i in (16, 17, 21, 22):
            nt.removeNames(nameID=i)
        destino = os.path.join(PDF, archivo.replace("AlegreyaSans", "EstudioSansPDF"))
        t.save(destino)
        hechas.append((os.path.basename(destino), os.path.getsize(destino), len(lnum)))
    return hechas


def face(familia, archivo, peso="400", estilo="normal"):
    datos = base64.b64encode(open(os.path.join(WEB, archivo), "rb").read()).decode()
    return (f'@font-face{{font-family:"{familia}";src:url(data:font/woff;base64,{datos}) format("woff");'
            f'font-weight:{peso};font-style:{estilo};font-display:block;}}\n')


def css_fuentes(con_mono=True, con_mate=True):
    """Bloque @font-face completo. Lo usan fuentes.html y la plantilla del cuestionario."""
    partes = []
    for archivo, peso, estilo in ALEGREYA:
        partes.append(face("Estudio Sans", archivo.replace(".ttf", ".woff"), peso, estilo))
    if con_mono:
        partes.append(face("Estudio Mono", "JetBrainsMono.woff", "100 800"))
    if con_mate:
        partes.append(face("Estudio Mate", "EstudioMate.woff"))
    partes.append(face("Estudio Marcas", "EstudioMarcas.woff"))
    return "".join(partes)


def main():
    uni = rangos(TEXTO)
    tam = {}
    for archivo, _, _ in ALEGREYA:
        destino = archivo.replace(".ttf", ".woff")
        tam[destino] = recortar(os.path.join(O, archivo), os.path.join(WEB, destino), uni)
    tam["JetBrainsMono.woff"] = recortar(
        os.path.join(O, "JetBrainsMono-VF.ttf"), os.path.join(WEB, "JetBrainsMono.woff"),
        rangos("U+0020-007E,U+00A0-00FF,U+0100-017F,U+2000-206F,U+2190-21FF,U+2200-22FF"),
        feats=["kern", "calt", "ccmp", "locl", "mark", "mkmk"])
    tam["EstudioMarcas.woff"] = marcas()
    tam["EstudioMate.woff"] = matematica()
    with open(INC, "w", encoding="utf-8") as f:
        f.write("<!-- fuentes.html: generado por herramientas/construir_fuentes.py, no editar a mano.\n"
                "     Fuentes OFL 1.1 incrustadas (ver LEEME.md). data-pagedjs-ignore: Paged.js no\n"
                "     reprocesa este bloque, pero el navegador lo usa igual. -->\n"
                "<style data-pagedjs-ignore>\n" + css_fuentes() + "</style>\n")
    for k, v in tam.items():
        print(f"fonts/web/{k}: {v / 1024:.0f} KB")
    for n, v, k in fuentes_pdf():
        print(f"fonts/graficos/{n}: {v / 1024:.0f} KB ({k} sustituciones lnum)")
    print(f"incluir/fuentes.html: {os.path.getsize(INC) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
