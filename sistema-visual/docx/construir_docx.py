"""construir_docx.py - Markdown -> Word (.docx) con el sistema visual v4.

Una sola orden arma el .docx completo, para todos los tipos de documento: el MISMO Markdown que alimenta el HTML.

  --tipo tp          TP de laboratorio o de problemas (caratula desde un JSON; filtro docx.lua)
  --tipo resumen     resumen extenso o corto (--modo); filtro docx-resumen.lua
  --tipo parcial     parcial digitalizado o modelo de practica; docx-material.lua
  --tipo soluciones  hoja de resultados o de resolucion; docx-material.lua

  1. (tp) Caratula desde un JSON (modelo habitual; campos vacios = a completar).
  2. Los SVG del Markdown pasan a PNG de 300 a 500 ppp con el navegador (Word no dibuja
     SVG con CSS), en la carpeta temporal.
  3. Pandoc con el reference-*.docx del perfil (estilos v4) y el filtro del tipo.
  4. Post-proceso: formulas OMML en letra recta (m:sty p) y cocientes apilados,
     tablas (datos: ancho y columnas; de diseno: notas al margen, figuras,
     ecuaciones, ejercicios), sangria de parrafos como el HTML, cabeza de hoja
     "Hoja n de N" (+ la seccion vigente en el resumen; en el material, el rotulo tipo
     plano de una sola linea: materia y tema del lado interior), fuentes incrustadas
     (Word: .odttf ofuscadas).

Uso:
    python construir_docx.py TP.md --datos TP.json [-o TP.docx]                 (tipo tp)
    python construir_docx.py Resumen.md --tipo resumen --modo extenso|corto [-o X.docx]
    python construir_docx.py Parcial.md --tipo parcial [--datos x.json]
    python construir_docx.py Soluciones.md --tipo soluciones [--datos x.json]
    python construir_docx.py --referencia        regenera los reference-*.docx (los 3 perfiles)
  Opciones: --chequeo (resumen del .docx), --indice (resumen extenso con indice),
  --practica (activa los componentes de practica), --datos JSON (caratula del TP o
  {"cabecera": {"materia", "tema", "trabajo"}} para el rotulo y la cabeza).
  Caratula del TP: "integrantes": [{"nombre": "...", "legajo": "..."}] (una fila por integrante;
  sin la lista, la tabla sale con dos filas vacias). Los datos de integrantes los pasa el
  la persona en cada TP: no se guardan en ningun archivo del proyecto.
  Sin --datos, materia y tema salen del encabezado YAML del .md.

Letra: Alegreya Sans en todo, incrustada como familia "Estudio Sans" (la misma
copia con cifras de caja alta que usa Matplotlib, renombrada como en
los HTML: Word no aplica el rasgo lnum y un nombre propio no choca con otra
Alegreya instalada). Formulas: Noto Sans Math (fuente matematica sans con
tabla MATH, tambien incrustada); Word solo acepta en las ecuaciones fuentes con
tabla MATH, y Alegreya Sans no la tiene.

Margenes: los de carpeta (css/tokens.css): A4, doble faz espejada (w:mirrorMargins), interior 2,0 cm (perforar
y encarpetar), exterior 1,0 cm, superior 1,5 cm, inferior 0,5 cm. Con 5 mm abajo
no entra un pie: la cabeza de hoja, dentro del margen superior (a 7 mm del
borde, zona imprimible), lleva "Hoja n de N" (sin la asignatura) del lado exterior y
el trabajo ("Trabajo Practico N° X") del lado interior;
hojas pares e impares con cabeza propia. En el material impreso (parcial, modelo,
soluciones) la misma linea lleva ademas el rotulo tipo plano: "materia | tema"
del lado interior, sin pie. El inferior es MARGEN["aba"]: subirlo
si la impresora corta. Algunas catedras piden 3 cm / 2 cm y el
numero de pagina al pie: prevalecen los margenes de carpeta.

Bugs de Word ya conocidos que este script evita (ver la skill generar-docx):
lista de definicion nativa (no usarla), docDefaults apuntando a la fuente del
tema (se fija la familia en docDefaults, en cada estilo y en el tema), autoajuste
de tablas segun los guiones del Markdown (tblLayout autofit), filas partidas
entre hojas (w:cantSplit) y w:caps (nunca se usa: sin mayusculas en el sistema).

Los archivos de trabajo (caratula, fuentes renombradas) van a una carpeta
temporal del sistema que se borra al terminar.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
import zipfile

from lxml import etree

sys.dont_write_bytecode = True

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)                                    # sistema-visual
REFERENCIA = os.path.join(AQUI, "reference.docx")
FILTRO = os.path.join(AQUI, "docx.lua")
F_PDF = os.path.join(RAIZ, "fonts", "graficos")
F_ORIG = os.path.join(RAIZ, "fonts", "originales")
sys.path.insert(0, os.path.join(RAIZ, "herramientas"))
import entorno  # noqa: E402

PANDOC = entorno.pandoc()

FAMILIA = "Estudio Sans"
MATE = "Noto Sans Math"
CODIGO = "Consolas"
TINTA, LAPIZ, FILETE, AZUL = "1D1F23", "55585E", "C9CCD1", "1C3F94"

CM = 1440 / 2.54                                                # twips por cm
A4_W, A4_H = 11906, 16838
# cm; margenes de carpeta , doble faz espejada,
# leidos de css/tokens.css (unica fuente, herramientas/margenes.py). "cab":
# posicion de la cabeza de hoja desde el borde superior.
sys.path.insert(0, os.path.join(RAIZ, "herramientas"))
import margenes as _mg  # noqa: E402

MARGEN = {"int": _mg.MM["interior"] / 10, "ext": _mg.MM["exterior"] / 10, "arr": _mg.MM["superior"] / 10,
          "aba": _mg.MM["inferior"] / 10, "cab": 0.7}
ANCHO = round(A4_W - (MARGEN["int"] + MARGEN["ext"]) * CM)      # caja de texto en twips

# Perfiles de estilos. Cuerpo de 12 pt en todos.
# tp: el TP de siempre (justificado, sangria de primera linea, titulos numerados al borde).
# resumen: como la Hoja A4: sangria de 1,3 cm donde cuelgan numeros, rotulos y aspas.
# material: parcial y soluciones: sin sangria, izquierda, encabezado fiel del original.
SANGRIA_RES = 1.3                                               # cm
PERFILES = {
    "tp": {"ref": "reference.docx", "filtro": "docx.lua", "sangria": 0.0},
    "resumen": {"ref": "reference-resumen.docx", "filtro": "docx-resumen.lua", "sangria": SANGRIA_RES},
    "material": {"ref": "reference-material.docx", "filtro": "docx-material.lua", "sangria": 0.0},
}
TIPOS = {"tp": "tp", "resumen": "resumen", "parcial": "material", "soluciones": "material"}
VERDE, ROJO = "1E6B3A", "C8373D"
MARCAS = "Estudio Marcas"

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}
W = "{%s}" % NS["w"]
M = "{%s}" % NS["m"]
REL_FUENTE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/font"
REL_CAB = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/header"
REL_PIE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer"
CT_ODTTF = "application/vnd.openxmlformats-officedocument.obfuscatedFont"
CT_CAB = "application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"
CT_PIE = "application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"
DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
NSDECL = ('xmlns:w="%s" xmlns:r="%s" xmlns:m="%s"' % (NS["w"], NS["r"], NS["m"]))

# Estilos (familia "Estudio Sans"): variante de fonts/graficos, renombrada
ESTILOS_FUENTE = [("Regular", "EstudioSansPDF-Regular.ttf", "embedRegular"),
                  ("Bold", "EstudioSansPDF-Bold.ttf", "embedBold"),
                  ("Italic", "EstudioSansPDF-Italic.ttf", "embedItalic"),
                  ("Bold Italic", "EstudioSansPDF-BoldItalic.ttf", "embedBoldItalic")]


def tw(cm):
    return str(round(cm * CM))


def twi(cm):
    return round(cm * CM)


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ---------------------------------------------------------------------------
# Estilos de Word (styles.xml completo: Pandoc agrega solo los que falten)
# ---------------------------------------------------------------------------
def _rpr(tam=None, negrita=False, italica=False, color=None, fuente=None, extra=""):
    x = ""
    if fuente:
        x += f'<w:rFonts w:ascii="{fuente}" w:hAnsi="{fuente}" w:cs="{fuente}" w:eastAsia="{fuente}"/>'
    if negrita:
        x += "<w:b/><w:bCs/>"
    if italica:
        x += "<w:i/><w:iCs/>"
    if color:
        x += f'<w:color w:val="{color}"/>'
    if tam:
        x += f'<w:sz w:val="{int(tam * 2)}"/><w:szCs w:val="{int(tam * 2)}"/>'
    return f"<w:rPr>{x}{extra}</w:rPr>" if (x or extra) else ""


def _p(tipo, sid, nombre, base=None, sig=None, ppr="", rpr="", extra="", default=False, custom=True):
    d = ' w:default="1"' if default else ""
    c = ' w:customStyle="1"' if custom else ""
    s = f'<w:style w:type="{tipo}"{d}{c} w:styleId="{sid}"><w:name w:val="{nombre}"/>'
    if base:
        s += f'<w:basedOn w:val="{base}"/>'
    if sig:
        s += f'<w:next w:val="{sig}"/>'
    s += "<w:qFormat/>" + extra
    if ppr:
        s += f"<w:pPr>{ppr}</w:pPr>"
    s += rpr + "</w:style>"
    return s


def estilos_xml(perfil="tp"):
    # Numero de titulo en azul al borde de la caja y el titulo alineado en 0,9 cm
    # (no se cuelga en el margen: el exterior mide 1 cm y quedaria al filo del papel)
    colgado = f'<w:ind w:left="{tw(0.9)}" w:hanging="{tw(0.9)}"/>'
    S = PERFILES[perfil]["sangria"]
    col_s = f'<w:ind w:left="{tw(S)}" w:hanging="{tw(S)}"/>'          # numero colgado en la sangria
    ind_s = f'<w:ind w:left="{tw(S)}"/>'
    # (interlinea, espacio despues, sangria de primera linea en cm, alineacion) del cuerpo
    linea, desp_cuerpo, primera, jc = {"tp": (324, 100, 0.7, "both"), "resumen": (331, 0, 0.55, "both"),
                                       "material": (322, 60, 0.0, "both")}[perfil]   # material justificado
    sin_corte = "<w:suppressAutoHyphens/>"
    e = []
    e.append(_p("paragraph", "Normal", "Normal", default=True, custom=False,
                ppr='<w:spacing w:after="0" w:line="312" w:lineRule="auto"/>'))
    e.append(_p("paragraph", "BodyText", "Body Text", "Normal", custom=False,
                ppr=f'<w:widowControl/><w:spacing w:before="0" w:after="{desp_cuerpo}" w:line="{linea}" w:lineRule="auto"/>'
                    + (f'<w:ind w:left="{tw(S)}" w:firstLine="{tw(primera)}"/>' if perfil != "tp" else
                       f'<w:ind w:firstLine="{tw(0.7)}"/>') + f'<w:jc w:val="{jc}"/>'))
    e.append(_p("paragraph", "FirstParagraph", "First Paragraph", "BodyText", "BodyText",
                ppr=f'<w:ind w:left="{tw(S)}" w:firstLine="0"/>' if perfil != "tp" else ""))
    e.append(_p("paragraph", "Compact", "Compact", "Normal",
                ppr=f'{sin_corte}<w:spacing w:before="30" w:after="30"/>'
                    + ('<w:jc w:val="both"/>' if perfil == "material" else "")))
    e.append(_p("paragraph", "Title", "Title", "Normal", "BodyText", custom=False,
                ppr='<w:spacing w:before="0" w:after="120"/>', rpr=_rpr(22, True)))
    e.append(_p("paragraph", "Subtitle", "Subtitle", "Normal", "BodyText", custom=False,
                ppr='<w:spacing w:after="120"/>', rpr=_rpr(14)))
    for sid in ("Author", "Date"):
        e.append(_p("paragraph", sid, sid, "Normal", "BodyText", rpr=_rpr(11, color=LAPIZ)))
    e.append(_p("paragraph", "AbstractTitle", "Abstract Title", "Normal", "Abstract", rpr=_rpr(11, True)))
    e.append(_p("paragraph", "Abstract", "Abstract", "BodyText"))
    e.append(_p("paragraph", "Bibliography", "Bibliography", "BodyText",
                ppr=f'<w:ind w:left="{tw(0.7)}" w:hanging="{tw(0.7)}"/><w:jc w:val="left"/>'))
    # Titulos: tinta, sin color ni mayusculas; numero colgado (lo pone docx.lua)
    tit = {"tp": [(1, 15, True, False, 360, 120, colgado), (2, 12.5, True, False, 260, 80, colgado),
                  (3, 12, True, False, 200, 60, "")],
           "resumen": [(1, 25, True, False, 0, 360, col_s), (2, 14.4, True, False, 560, 100, col_s),
                       (3, 12, False, True, 340, 60, ind_s)],
           "material": [(1, 16.5, True, False, 0, 80, ""), (2, 12.8, True, False, 200, 60, ""),
                        (3, 12, False, True, 160, 40, "")]}[perfil]
    for n in range(1, 10):
        _, tam, neg, ita, antes, desp, ind = tit[min(n, 3) - 1]
        e.append(_p("paragraph", f"Heading{n}", f"heading {n}", "Normal", "BodyText", custom=False,
                    extra=f'<w:uiPriority w:val="9"/>',
                    ppr=f'<w:keepNext/><w:keepLines/>{sin_corte}<w:spacing w:before="{antes}" w:after="{desp}" '
                        f'w:line="264" w:lineRule="auto"/>{ind}<w:jc w:val="left"/><w:outlineLvl w:val="{n - 1}"/>',
                    rpr=_rpr(tam, neg, ita, TINTA)))
    e.append(_p("paragraph", "BlockText", "Block Text", "BodyText", "BodyText", custom=False,
                ppr=f'<w:ind w:left="{tw(0.6)}" w:firstLine="0"/>'))
    e.append(_p("paragraph", "Enunciado", "Enunciado", "BodyText",
                ppr=f'<w:ind w:left="{tw(0.6)}" w:firstLine="0"/><w:spacing w:after="80"/>'))
    e.append(_p("paragraph", "Resultado", "Resultado", "BodyText",
                ppr=f'<w:keepLines/>{sin_corte}<w:spacing w:before="60" w:after="60"/><w:ind w:firstLine="0"/>'
                    f'<w:jc w:val="{"both" if perfil in ("tp", "material") else "left"}"/>'))
    e.append(_p("paragraph", "Supuesto", "Supuesto", "BodyText",
                ppr='<w:spacing w:before="120" w:after="120"/><w:ind w:firstLine="0"/>', rpr=_rpr(10.5, color=LAPIZ)))
    e.append(_p("paragraph", "FootnoteText", "footnote text", "Normal", custom=False, rpr=_rpr(10)))
    e.append(_p("paragraph", "FootnoteBlockText", "Footnote Block Text", "FootnoteText"))
    # Lista de definicion: bug de sangria conocido, no usarla (se define igual)
    e.append(_p("paragraph", "DefinitionTerm", "Definition Term", "Normal", "Definition",
                ppr='<w:keepNext/><w:spacing w:before="120" w:after="0"/>', rpr=_rpr(None, True)))
    e.append(_p("paragraph", "Definition", "Definition", "Normal"))
    e.append(_p("paragraph", "Caption", "caption", "Normal", custom=False,
                ppr=f'{sin_corte}<w:spacing w:before="60" w:after="220"/>', rpr=_rpr(10, color=LAPIZ)))
    e.append(_p("paragraph", "TableCaption", "Table Caption", "Caption",
                ppr='<w:keepNext/><w:spacing w:before="200" w:after="80"/><w:jc w:val="both"/>'))
    # epigrafes de figura y tabla justificados, no centrados
    e.append(_p("paragraph", "ImageCaption", "Image Caption", "Caption",
                ppr='<w:jc w:val="both"/>'))
    e.append(_p("paragraph", "Figure", "Figure", "Normal", ppr='<w:jc w:val="center"/>'))
    e.append(_p("paragraph", "CaptionedFigure", "Captioned Figure", "Figure",
                ppr='<w:keepNext/><w:spacing w:before="160" w:after="40"/><w:jc w:val="center"/>'))
    e.append(_p("paragraph", "TOCHeading", "TOC Heading", "Heading1", "BodyText", custom=False,
                ppr='<w:ind w:left="0" w:firstLine="0"/><w:outlineLvl w:val="9"/>'))
    tabs = f'<w:tabs><w:tab w:val="right" w:pos="{ANCHO}"/></w:tabs>'
    e.append(_p("paragraph", "Header", "header", "Normal", custom=False,
                ppr=tabs + '<w:spacing w:line="240" w:lineRule="auto"/>', rpr=_rpr(9.5, color=LAPIZ)))
    e.append(_p("paragraph", "Footer", "footer", "Normal", custom=False, ppr=tabs, rpr=_rpr(9.5, color=LAPIZ)))
    # Caratula (modelo habitual)
    e.append(_p("paragraph", "CaratulaMarco", "Caratula Marco", "Normal", rpr=_rpr(11, color=LAPIZ)))
    e.append(_p("paragraph", "CaratulaLogo", "Caratula Logo", "Normal",      # logo opcional (docx.lua, caratula.logo)
                ppr=f'{sin_corte}<w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>'
                    '<w:ind w:left="0" w:right="0" w:firstLine="0"/><w:jc w:val="left"/>'))
    e.append(_p("paragraph", "CaratulaTP", "Caratula TP", "Normal",
                ppr=f'{sin_corte}<w:spacing w:before="0" w:after="160"/>', rpr=_rpr(15)))
    e.append(_p("paragraph", "CaratulaTitulo", "Caratula Titulo", "Normal",
                ppr=f'{sin_corte}<w:spacing w:before="0" w:after="0" w:line="252" w:lineRule="auto"/>'
                    f'<w:ind w:left="{tw(0.1)}" w:right="{tw(0.1)}"/>'
                    f'<w:pBdr><w:bottom w:val="single" w:sz="18" w:space="10" w:color="{TINTA}"/></w:pBdr>',
                rpr=_rpr(26, True)))
    e.append(_p("paragraph", "CaratulaCampo", "Caratula Campo", "Normal",
                ppr=f'<w:tabs><w:tab w:val="left" w:pos="{tw(4.4)}"/><w:tab w:val="right" w:leader="underscore" '
                    f'w:pos="{ANCHO}"/></w:tabs><w:spacing w:before="0" w:after="160"/>',
                rpr=_rpr(12)))
    # Caracter
    e.append('<w:style w:type="character" w:default="1" w:styleId="DefaultParagraphFont">'
             '<w:name w:val="Default Paragraph Font"/><w:uiPriority w:val="1"/><w:semiHidden/>'
             '<w:unhideWhenUsed/></w:style>')
    e.append(_p("character", "BodyTextChar", "Body Text Char", "DefaultParagraphFont"))
    e.append(_p("character", "VerbatimChar", "Verbatim Char", "DefaultParagraphFont",
                rpr=_rpr(10.5, fuente=CODIGO)))
    e.append(_p("character", "SectionNumber", "Section Number", "DefaultParagraphFont", rpr=_rpr(None, color=AZUL)))
    e.append(_p("character", "FootnoteReference", "footnote reference", "DefaultParagraphFont", custom=False,
                rpr=_rpr(None, color=AZUL, extra='<w:vertAlign w:val="superscript"/>')))
    e.append(_p("character", "Hyperlink", "Hyperlink", "DefaultParagraphFont", custom=False,
                rpr=_rpr(None, color=AZUL)))
    e.append(_p("character", "Numero", "Numero", "DefaultParagraphFont", rpr=_rpr(None, color=AZUL)))
    e.append(_p("character", "NumeroRotulo", "Numero Rotulo", "DefaultParagraphFont", rpr=_rpr(None, True, color=AZUL)))
    e.append(_p("character", "Referencia", "Referencia", "DefaultParagraphFont", rpr=_rpr(None, color=AZUL)))
    # Tabla: filetes arriba, abajo y bajo la cabecera; sin fondos ni verticales
    e.append(
        '<w:style w:type="table" w:default="1" w:styleId="Table"><w:name w:val="Table"/><w:uiPriority w:val="59"/>'
        '<w:pPr><w:spacing w:before="30" w:after="30"/></w:pPr>'
        # sangria de 1 mm: Word dibuja el filete medio trazo hacia afuera de la caja
        f'<w:tblPr><w:tblInd w:w="{tw(0.1)}" w:type="dxa"/>'
        f'<w:tblBorders><w:top w:val="single" w:sz="8" w:space="0" w:color="{TINTA}"/>'
        f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="{TINTA}"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{FILETE}"/>'
        f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="{FILETE}"/></w:tblBorders>'
        '<w:tblCellMar><w:top w:w="30" w:type="dxa"/><w:left w:w="110" w:type="dxa"/>'
        '<w:bottom w:w="30" w:type="dxa"/><w:right w:w="110" w:type="dxa"/></w:tblCellMar></w:tblPr>'
        '<w:tblStylePr w:type="firstRow"><w:rPr><w:b/><w:bCs/></w:rPr><w:tblPr/>'
        f'<w:tcPr><w:tcBorders><w:bottom w:val="single" w:sz="6" w:space="0" w:color="{TINTA}"/></w:tcBorders>'
        '</w:tcPr></w:tblStylePr></w:style>')
    defaults = (
        "<w:docDefaults><w:rPrDefault><w:rPr>"
        f'<w:rFonts w:ascii="{FAMILIA}" w:hAnsi="{FAMILIA}" w:eastAsia="{FAMILIA}" w:cs="{FAMILIA}"/>'
        f'<w:color w:val="{TINTA}"/><w:sz w:val="24"/><w:szCs w:val="24"/>'
        '<w:lang w:val="es-AR" w:eastAsia="es-AR" w:bidi="ar-SA"/>'
        "</w:rPr></w:rPrDefault><w:pPrDefault><w:pPr>"
        '<w:spacing w:after="0" w:line="312" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>')
    if perfil != "tp":
        nuevos = [re.sub(r'(w:customStyle="1" w:styleId="([^"]+)"><w:name w:val=")[^"]*', r"\1\2", x)
                  for x in estilos_extra(perfil)]
        e = reemplazar(e, nuevos)
    return (DECL + f'<w:styles {NSDECL}>' + defaults +
            '<w:latentStyles w:defLockedState="0" w:defUIPriority="99" w:defSemiHidden="0" '
            'w:defUnhideWhenUsed="0" w:defQFormat="0" w:count="376"/>' + "".join(e) + "</w:styles>")


def reemplazar(base, nuevos):
    """Agrega los estilos nuevos; si uno ya estaba (mismo styleId), lo reemplaza."""
    ids = {re.search(r'w:styleId="([^"]+)"', x).group(1) for x in nuevos}
    return [x for x in base if re.search(r'w:styleId="([^"]+)"', x).group(1) not in ids] + list(nuevos)


def _ind(izq=0.0, colgado=0.0, primera=0.0, der=0.0):
    a = f'<w:ind w:left="{tw(izq)}"'
    if der:
        a += f' w:right="{tw(der)}"'
    if colgado:
        a += f' w:hanging="{tw(colgado)}"'
    else:
        a += f' w:firstLine="{tw(primera)}"'
    return a + "/>"


AIRE = 0.07          # cm que entra un parrafo con filete para que el trazo no invada el margen


def _borde(lado, val="single", sz=6, color=FILETE, espacio=0):
    return f'<w:pBdr><w:{lado} w:val="{val}" w:sz="{sz}" w:space="{espacio}" w:color="{color}"/></w:pBdr>'


def estilos_extra(perfil):
    """Estilos propios de los perfiles resumen y material (los que nombran los filtros
    docx-resumen.lua y docx-material.lua, y los que pone el post-proceso)."""
    S = PERFILES[perfil]["sangria"]
    res = perfil == "resumen"
    sc = "<w:suppressAutoHyphens/>"
    kl = "<w:keepLines/>"
    kn = "<w:keepNext/>"
    izq = "<w:jc w:val=\"left\"/>"
    tab_col = f'<w:tabs><w:tab w:val="right" w:pos="{tw(S - 0.15)}"/></w:tabs>' if S else ""
    jus = '<w:jc w:val="both"/>'     # el texto del material va justificado y sin guionado, como los TP
    e = []
    # ---- comunes
    e.append(_p("paragraph", "TablaTexto", "Tabla Texto", "Normal",
                ppr=f'{sc}<w:spacing w:before="20" w:after="20" w:line="264" w:lineRule="auto"/>{izq}',
                rpr=_rpr(9.5 if res else 10.5)))
    e.append(_p("paragraph", "EspacioRespuesta", "Espacio Respuesta", "Normal", rpr=_rpr(2)))
    e.append(_p("paragraph", "Header", "header", "Normal", custom=False,
                ppr=f'<w:tabs><w:tab w:val="right" w:pos="{ANCHO}"/></w:tabs><w:spacing w:line="240" w:lineRule="auto"/>',
                rpr=_rpr(9, color=LAPIZ)))
    e.append(_p("paragraph", "Footer", "footer", "Normal", custom=False,
                ppr=f'<w:tabs><w:tab w:val="right" w:pos="{ANCHO}"/></w:tabs><w:spacing w:line="240" w:lineRule="auto"/>',
                rpr=_rpr(9, color=LAPIZ)))
    e.append(_p("character", "Aspa", "Aspa", "DefaultParagraphFont", rpr=_rpr(12, color=ROJO, fuente=MARCAS)))
    e.append(_p("character", "Marca", "Marca", "DefaultParagraphFont", rpr=_rpr(None, fuente=MARCAS)))
    # tablas de diseno: sin bordes ni margenes de celda; el post-proceso fija ancho y celdas
    cm0 = ('<w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="0" w:type="dxa"/>'
           '<w:bottom w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tblCellMar>')
    e.append('<w:style w:type="table" w:customStyle="1" w:styleId="TablaDiseno"><w:name w:val="TablaDiseno"/>'
             f'<w:uiPriority w:val="59"/><w:tblPr><w:tblInd w:w="0" w:type="dxa"/>{cm0}</w:tblPr></w:style>')
    for sid in ("TablaNota", "TablaFigura", "TablaEcuacion", "TablaClave", "TablaGlosario", "TablaEjercicio",
                "TablaEjercicioLibre"):
        e.append(f'<w:style w:type="table" w:customStyle="1" w:styleId="{sid}"><w:name w:val="{sid}"/>'
                 '<w:basedOn w:val="TablaDiseno"/><w:uiPriority w:val="59"/></w:style>')
    e.append('<w:style w:type="table" w:customStyle="1" w:styleId="TablaResultados"><w:name w:val="TablaResultados"/>'
             '<w:basedOn w:val="Table"/><w:uiPriority w:val="59"/><w:tblPr><w:tblBorders>'
             f'<w:top w:val="nil"/><w:bottom w:val="nil"/>'
             f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{FILETE}"/></w:tblBorders></w:tblPr>'
             f'<w:tblStylePr w:type="firstRow"><w:rPr><w:b/><w:bCs/></w:rPr><w:tblPr/><w:tcPr><w:tcBorders>'
             f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="{TINTA}"/></w:tcBorders></w:tcPr>'
             '</w:tblStylePr></w:style>')
    if res:
        e += _extra_resumen(S, tab_col, sc, kl, kn, izq)
    else:
        e += _extra_material(sc, kl, kn, izq, jus)
    return e


def _extra_resumen(S, tab_col, sc, kl, kn, izq):
    e = []
    e.append(_p("paragraph", "Encabezado", "Encabezado", "Normal",
                ppr=f'{sc}<w:spacing w:before="0" w:after="380"/>', rpr=_rpr(10)))
    e.append(_p("character", "EncMateria", "Enc Materia", "DefaultParagraphFont", rpr=_rpr(None, True)))
    e.append(_p("character", "EncSep", "Enc Sep", "DefaultParagraphFont", rpr=_rpr(None, color=LAPIZ)))
    e.append(_p("character", "EncUnidad", "Enc Unidad", "DefaultParagraphFont", rpr=_rpr(None, color=LAPIZ)))
    # Apertura de unidad: numeral grande azul colgado en la sangria, titulo y filete grueso
    e.append(_p("paragraph", "Apertura", "Apertura", "Normal", "BodyText",
                ppr=f'{kn}{kl}{sc}<w:spacing w:before="0" w:after="380" w:line="1120" w:lineRule="exact"/>'
                    f'<w:ind w:left="{tw(S + AIRE)}" w:right="{tw(AIRE)}" w:hanging="{tw(S)}"/>'
                    f'{_borde("bottom", "single", 18, TINTA, 4)}{izq}<w:outlineLvl w:val="0"/>',
                rpr=_rpr(25, True)))
    e.append(_p("paragraph", "AperturaNueva", "Apertura Nueva", "Apertura", "BodyText",
                ppr='<w:pageBreakBefore/><w:spacing w:before="260" w:after="380" w:line="1120" w:lineRule="exact"/>'))
    e.append(_p("character", "Numeral", "Numeral", "DefaultParagraphFont", rpr=_rpr(59, True, color=AZUL)))
    e.append(_p("character", "TituloSec", "TituloSec", "DefaultParagraphFont"))
    # enunciados (definicion, ejemplo, propiedad, demostracion): rotulo en linea
    e.append(_p("paragraph", "Enunciado", "Enunciado", "BodyText",
                ppr=f'{kl}<w:spacing w:before="140" w:after="0"/>{_ind(S)}'))
    e.append(_p("paragraph", "CuerpoCelda", "Cuerpo Celda", "BodyText",
                ppr=f'<w:spacing w:before="0" w:after="0"/>{_ind()}'))
    e.append(_p("paragraph", "EcuacionP", "Ecuacion P", "Normal",
                ppr='<w:spacing w:before="60" w:after="60" w:line="240" w:lineRule="auto"/><w:jc w:val="center"/>',
                rpr=_rpr(13)))
    e.append(_p("paragraph", "EcNum", "Ec Num", "Normal",
                ppr='<w:spacing w:before="60" w:after="60"/><w:jc w:val="right"/>', rpr=_rpr(11.5, color=LAPIZ)))
    e.append(_p("paragraph", "FiguraP", "Figura P", "Normal", ppr='<w:spacing w:before="0" w:after="0"/>' + izq))
    e.append(_p("paragraph", "EpigrafeFigura", "Epigrafe Figura", "Normal",
                ppr=f'{sc}<w:spacing w:before="0" w:after="0" w:line="264" w:lineRule="auto"/>{izq}',
                rpr=_rpr(9.5, color=LAPIZ)))
    e.append(_p("paragraph", "NotaMargen", "Nota Margen", "Normal",
                ppr=f'{sc}<w:spacing w:before="0" w:after="60" w:line="264" w:lineRule="auto"/>{izq}', rpr=_rpr(9.5)))
    e.append(_p("character", "NotaRef", "Nota Ref", "DefaultParagraphFont",
                rpr=_rpr(None, True, color=AZUL, extra='<w:vertAlign w:val="superscript"/>')))
    e.append(_p("character", "NotaNum", "Nota Num", "DefaultParagraphFont", rpr=_rpr(None, True, color=AZUL)))
    e.append(_p("character", "Colgado", "Colgado", "DefaultParagraphFont", rpr=_rpr(9.6, False, True, LAPIZ)))
    e.append(_p("character", "AvisoPractica", "Aviso Practica", "DefaultParagraphFont",
                rpr=_rpr(None, False, True, LAPIZ)))
    # sintesis y practica: filete, rotulo colgado
    e.append(_p("paragraph", "SintesisFilete", "Sintesis Filete", "Normal",
                ppr=f'{kn}<w:spacing w:before="260" w:after="60" w:line="20" w:lineRule="exact"/>{_ind(S + AIRE, der=AIRE)}'
                    f'{_borde("bottom", "single", 6, FILETE)}', rpr=_rpr(2)))
    e.append(_p("paragraph", "PracticaFilete", "Practica Filete", "Normal",
                ppr=f'{kn}<w:spacing w:before="200" w:after="60" w:line="20" w:lineRule="exact"/>{_ind(S + AIRE, der=AIRE)}'
                    f'{_borde("bottom", "dashed", 6, LAPIZ)}', rpr=_rpr(2)))
    e.append(_p("paragraph", "Sintesis", "Sintesis", "BodyText",
                ppr=f'{kl}{tab_col}<w:spacing w:before="0" w:after="0"/>{_ind(S, S)}', rpr=_rpr(11.5)))
    e.append(_p("paragraph", "SintesisCont", "Sintesis Cont", "BodyText",
                ppr=f'{kl}<w:spacing w:before="40" w:after="0"/>{_ind(S)}', rpr=_rpr(11.5)))
    e.append(_p("paragraph", "PracticaP", "Practica P", "BodyText",
                ppr=f'{kn}{kl}{tab_col}<w:spacing w:before="0" w:after="40"/>{_ind(S, S)}{izq}'))
    # ojo y errores frecuentes: aspa roja colgada (y la palabra)
    e.append(_p("paragraph", "Ojo", "Ojo", "BodyText",
                ppr=f'{kl}{tab_col}<w:spacing w:before="140" w:after="60"/>{_ind(S, S)}'))
    e.append(_p("paragraph", "OjoCont", "Ojo Cont", "BodyText",
                ppr=f'{kl}<w:spacing w:before="40" w:after="0"/>{_ind(S)}'))
    e.append(_p("paragraph", "ErrorItem", "Error Item", "BodyText",
                ppr=f'{kl}{tab_col}<w:spacing w:before="60" w:after="40"/>{_ind(S, S)}'))
    e.append(_p("paragraph", "ErrorItemCont", "Error Item Cont", "BodyText",
                ppr=f'{kl}<w:spacing w:before="40" w:after="0"/>{_ind(S)}'))
    e.append(_p("paragraph", "RotuloBloque", "Rotulo Bloque", "BodyText",
                ppr=f'{kn}<w:spacing w:before="220" w:after="40"/>{_ind(S)}{izq}'))
    e.append(_p("paragraph", "GlosarioT", "Glosario T", "Normal",
                ppr=f'{sc}<w:spacing w:before="20" w:after="60" w:line="264" w:lineRule="auto"/>{izq}', rpr=_rpr(11)))
    e.append(_p("paragraph", "GlosarioD", "Glosario D", "Normal",
                ppr=f'{sc}<w:spacing w:before="20" w:after="60" w:line="264" w:lineRule="auto"/>{izq}', rpr=_rpr(11)))
    e.append(_p("paragraph", "IndiceUnidad", "Indice Unidad", "Normal",
                ppr=f'{sc}{kl}<w:spacing w:before="60" w:after="20"/>{_ind(S + 0.7, 0.7)}{izq}', rpr=_rpr(10.5, True)))
    e.append(_p("paragraph", "IndiceSeccion", "Indice Seccion", "Normal",
                ppr=f'{sc}{kl}<w:spacing w:before="10" w:after="10"/>{_ind(S + 0.7 + 0.7, 0.7)}{izq}', rpr=_rpr(10.5)))
    # leyenda de tabla: sobre la tabla, en tinta, alineada con el texto
    e.append(_p("paragraph", "TableCaption", "Table Caption", "Caption",
                ppr=f'{kn}<w:spacing w:before="220" w:after="80"/>{_ind(S)}{izq}', rpr=_rpr(10, color=TINTA)))
    return e


def _extra_material(sc, kl, kn, izq, jus=None):
    jus = jus or izq
    e = []
    e.append(_p("paragraph", "CabOriginal", "Cab Original", "Normal",
                ppr=f'{kn}{sc}<w:tabs><w:tab w:val="right" w:pos="{ANCHO}"/></w:tabs>'
                    f'<w:spacing w:before="0" w:after="140" w:line="240" w:lineRule="auto"/>{_ind(AIRE, der=AIRE)}'
                    f'{_borde("bottom", "single", 11, TINTA, 4)}'))
    e.append(_p("character", "CabTitulo", "Cab Titulo", "DefaultParagraphFont", rpr=_rpr(14.5, True)))
    e.append(_p("character", "CabFecha", "Cab Fecha", "DefaultParagraphFont", rpr=_rpr(11, True)))
    e.append(_p("paragraph", "CabOriginalDato", "Cab Original Dato", "Normal",
                ppr=f'{sc}<w:spacing w:before="0" w:after="140"/>{izq}', rpr=_rpr(11, True)))
    e.append(_p("paragraph", "Consigna", "Consigna", "Normal",
                ppr=f'{kl}{sc}<w:spacing w:before="40" w:after="240"/>'
                    f'{_ind(AIRE, der=AIRE)}<w:pBdr><w:top w:val="single" w:sz="5" w:space="4" w:color="{LAPIZ}"/>'
                    f'<w:bottom w:val="single" w:sz="5" w:space="4" w:color="{LAPIZ}"/></w:pBdr>{izq}',
                rpr=_rpr(10.4, True)))
    e.append(_p("paragraph", "Subtitulo", "Subtitulo", "Normal", "BodyText", custom=False,
                ppr=f'{sc}<w:spacing w:before="0" w:after="240"/>{_ind(AIRE, der=AIRE)}{_borde("bottom", "single", 11, TINTA, 5)}{izq}',
                rpr=_rpr(10.6, color=LAPIZ)))
    e.append(_p("paragraph", "EjercicioN", "Ejercicio N", "Normal",
                ppr=f'{kn}{sc}<w:spacing w:before="0" w:after="0"/>{izq}', rpr=_rpr(12.8, True)))
    e.append(_p("paragraph", "EjercicioP", "Ejercicio P", "BodyText",
                ppr=f'<w:spacing w:before="0" w:after="60" w:line="322" w:lineRule="auto"/>{_ind()}{jus}'))
    e.append(_p("paragraph", "Resultado", "Resultado", "BodyText",
                ppr=f'{kl}{sc}<w:spacing w:before="60" w:after="120"/>{_ind()}{jus}',
                rpr=_rpr(None, True, color=VERDE)))
    e.append(_p("paragraph", "Supuesto", "Supuesto", "BodyText",
                ppr=f'<w:spacing w:before="40" w:after="100"/>{_ind()}{jus}', rpr=_rpr(10.4, False, True, LAPIZ)))
    e.append(_p("paragraph", "Errata", "Errata", "BodyText",
                ppr=f'<w:spacing w:before="40" w:after="100"/>{_ind()}{jus}', rpr=_rpr(10.4, color=ROJO)))
    e.append(_p("paragraph", "Datos", "Datos", "BodyText",
                ppr=f'<w:spacing w:before="60" w:after="60"/>{_ind()}{jus}'))
    e.append(_p("paragraph", "EpigrafeMaterial", "Epigrafe Material", "Normal",
                ppr=f'{sc}<w:spacing w:before="20" w:after="80"/>{izq}', rpr=_rpr(9.3, color=LAPIZ)))
    return e


# ---------------------------------------------------------------------------
# Encabezado, pie y seccion
# ---------------------------------------------------------------------------
def _campo(instr, texto="1", rpr=""):
    r = f"<w:rPr>{rpr}</w:rPr>" if rpr else ""
    return (f'<w:r>{r}<w:fldChar w:fldCharType="begin"/></w:r><w:r>{r}<w:instrText xml:space="preserve"> {instr} '
            f'</w:instrText></w:r><w:r>{r}<w:fldChar w:fldCharType="separate"/></w:r><w:r>{r}<w:t>{texto}</w:t></w:r>'
            f'<w:r>{r}<w:fldChar w:fldCharType="end"/></w:r>')


def _hoja(rpr=""):
    r = f"<w:rPr>{rpr}</w:rPr>" if rpr else ""
    return (f'<w:r>{r}<w:t xml:space="preserve">Hoja </w:t></w:r>' + _campo("PAGE", "1", rpr) +
            f'<w:r>{r}<w:t xml:space="preserve"> de </w:t></w:r>' + _campo("NUMPAGES", "1", rpr))


def _hoja_n(rpr=""):
    """"n de N" sin la palabra Hoja (el rotulo del material la pone como etiqueta)."""
    r = f"<w:rPr>{rpr}</w:rPr>" if rpr else ""
    return _campo("PAGE", "1", rpr) + f'<w:r>{r}<w:t xml:space="preserve"> de </w:t></w:r>' + _campo("NUMPAGES", "1", rpr)


def cabecera_xml(par=False, perfil="tp", primera=False):
    """Cabeza de hoja en el margen superior: "Hoja n de N" del lado exterior y, del lado
    interior, el trabajo (tp, sin la asignatura) o la
    seccion vigente (resumen: campo STYLEREF al estilo de caracter TituloSec, que lleva
    el texto de cada titulo de seccion; la primera hoja no la lleva, como la Hoja A4);
    el material impreso lleva el rotulo tipo plano en una sola linea ("materia | tema", lado
    interior, marcador ROT_LINEA que reemplaza el post-proceso) y "Hoja n de N" del exterior.
    Impar: exterior a la derecha."""
    tab = "<w:r><w:tab/></w:r>"
    if perfil == "tp":
        trab = '<w:r><w:t xml:space="preserve">«CABECERA_TRABAJO»</w:t></w:r>'
        cuerpo = (_hoja() + tab + trab) if par else (trab + tab + _hoja())
    else:
        hoja = _hoja(f'<w:color w:val="{TINTA}"/>')
        if perfil == "resumen" and not primera:
            sec = _campo("STYLEREF TituloSec", "", '<w:i/><w:iCs/><w:sz w:val="17"/><w:szCs w:val="17"/>')
            cuerpo = (hoja + tab + sec) if par else (sec + tab + hoja)
        elif perfil == "material":
            lin = f'<w:r><w:rPr><w:color w:val="{TINTA}"/></w:rPr><w:t xml:space="preserve">«ROT_LINEA»</w:t></w:r>'
            cuerpo = (hoja + tab + lin) if par else (lin + tab + hoja)
        else:
            cuerpo = hoja if par else (tab + hoja)
    return DECL + f'<w:hdr {NSDECL}><w:p><w:pPr><w:pStyle w:val="Header"/></w:pPr>{cuerpo}</w:p></w:hdr>'


def seccion_xml(con_cabecera=True, perfil="tp"):
    refs = ""
    if con_cabecera:
        refs = ('<w:headerReference w:type="default" r:id="rIdCabV4"/>'
                '<w:headerReference w:type="even" r:id="rIdCabParV4"/>')
        if perfil == "resumen":
            refs += '<w:headerReference w:type="first" r:id="rIdCabPrimV4"/>'
    titulo = "<w:titlePg/>" if (con_cabecera and perfil == "resumen") else ""
    # Con w:mirrorMargins (settings.xml) left = interior y right = exterior.
    return (f"<w:sectPr>{refs}<w:footnotePr><w:numRestart w:val=\"eachSect\"/></w:footnotePr>"
            f'<w:pgSz w:w="{A4_W}" w:h="{A4_H}"/>'
            f'<w:pgMar w:top="{tw(MARGEN["arr"])}" w:right="{tw(MARGEN["ext"])}" w:bottom="{tw(MARGEN["aba"])}" '
            f'w:left="{tw(MARGEN["int"])}" w:header="{tw(MARGEN["cab"])}" w:footer="0" w:gutter="0"/>'
            f'<w:cols w:space="708"/>{titulo}</w:sectPr>')


# ---------------------------------------------------------------------------
# reference-*.docx (uno por perfil)
# ---------------------------------------------------------------------------
def referencia(perfil="tp", destino=None):
    """Arma el reference.docx del perfil a partir del de Pandoc, con los estilos v4."""
    destino = destino or os.path.join(AQUI, PERFILES[perfil]["ref"])
    with tempfile.TemporaryDirectory() as tmp:
        base = os.path.join(tmp, "base.docx")
        subprocess.run([PANDOC, "-o", base, "--print-default-data-file", "reference.docx"], check=True)
        zin = zipfile.ZipFile(base)
        partes = {n: zin.read(n) for n in zin.namelist()}
        zin.close()
    partes["word/styles.xml"] = estilos_xml(perfil).encode("utf-8")
    partes["word/header1.xml"] = cabecera_xml(False, perfil).encode("utf-8")
    partes["word/header2.xml"] = cabecera_xml(True, perfil).encode("utf-8")
    cab = [("rIdCabV4", "header1.xml"), ("rIdCabParV4", "header2.xml")]
    if perfil == "resumen":
        partes["word/header3.xml"] = cabecera_xml(False, perfil, primera=True).encode("utf-8")
        cab.append(("rIdCabPrimV4", "header3.xml"))
    pie = []
    # documento de muestra minimo con la seccion A4 y los margenes de carpeta
    partes["word/document.xml"] = (
        DECL + f"<w:document {NSDECL}><w:body><w:p><w:pPr><w:pStyle w:val=\"BodyText\"/></w:pPr>"
        "<w:r><w:t>Plantilla del sistema visual v4 (construir_docx.py).</w:t></w:r></w:p>"
        + seccion_xml(True, perfil) + "</w:body></w:document>").encode("utf-8")
    rels = partes["word/_rels/document.xml.rels"].decode("utf-8")
    rels = re.sub(r'<Relationship [^>]*hyperlink[^>]*/>', "", rels)
    nuevos = "".join(f'<Relationship Id="{i}" Type="{REL_CAB}" Target="{t}"/>' for i, t in cab)
    nuevos += "".join(f'<Relationship Id="{i}" Type="{REL_PIE}" Target="{t}"/>' for i, t in pie)
    partes["word/_rels/document.xml.rels"] = rels.replace("</Relationships>", nuevos + "</Relationships>").encode("utf-8")
    ct = partes["[Content_Types].xml"].decode("utf-8")
    ov = "".join(f'<Override PartName="/word/{t}" ContentType="{CT_CAB}"/>' for _, t in cab)
    ov += "".join(f'<Override PartName="/word/{t}" ContentType="{CT_PIE}"/>' for _, t in pie)
    partes["[Content_Types].xml"] = ct.replace("</Types>", ov + "</Types>").encode("utf-8")
    partes["word/theme/theme1.xml"] = tema(partes["word/theme/theme1.xml"])
    partes["word/settings.xml"] = ajustes(partes["word/settings.xml"], con_fuentes=False)
    escribir_zip(destino, partes)
    return destino


def tema(xml):
    """Fuentes del tema (mayor y menor) = Estudio Sans, para que nada caiga en Aptos."""
    t = xml.decode("utf-8")
    t = re.sub(r'(<a:(?:majorFont|minorFont)>\s*<a:latin typeface=")[^"]*"', r'\g<1>' + FAMILIA + '"', t)
    return t.encode("utf-8")


def ajustes(xml, con_fuentes=True):
    """settings.xml: fuente de formulas, separacion silabica, incrustar fuentes."""
    s = etree.fromstring(xml)
    mp = s.find(M + "mathPr")
    if mp is None:
        # Pandoc no copia m:mathPr de la referencia: sin esto Word usa Cambria Math
        mp = etree.fromstring(
            f'<m:mathPr xmlns:m="{NS["m"]}"><m:mathFont m:val="{MATE}"/><m:brkBin m:val="before"/>'
            '<m:brkBinSub m:val="--"/><m:smallFrac m:val="0"/><m:dispDef/><m:lMargin m:val="0"/>'
            '<m:rMargin m:val="0"/><m:defJc m:val="centerGroup"/><m:wrapIndent m:val="1440"/>'
            '<m:intLim m:val="subSup"/><m:naryLim m:val="undOvr"/></m:mathPr>')
        # orden del esquema: ... rsids, m:mathPr, attachedSchema, themeFontLang ...
        ancla = s.find(W + "rsids")
        if ancla is not None:
            ancla.addnext(mp)
        else:
            sig = s.find(W + "themeFontLang")
            (sig.addprevious(mp) if sig is not None else s.append(mp))
    # Modo de compatibilidad 15 (Word 2013 o mas): sin esto Word usa el diseno de tablas heredado, en el que el
    # borde izquierdo de la tabla queda desplazado hacia afuera el margen de celda (margen + sangria - 1,94 mm), y
    # las tablas sobresalian del margen de 10 mm (regla 22). Con el modo 15 el borde queda en margen +
    # sangria. Va antes de rsids, segun el orden del esquema de settings.
    compat = s.find(W + "compat")
    if compat is None:
        compat = etree.fromstring(
            f'<w:compat xmlns:w="{NS["w"]}"><w:compatSetting w:name="compatibilityMode" '
            'w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat>')
        for nombre in ("docVars", "rsids"):
            ancla = s.find(W + nombre)
            if ancla is not None:
                ancla.addprevious(compat)
                break
        else:
            s.find(M + "mathPr").addprevious(compat)
    # si ya habia un w:compat (por ejemplo de una plantilla con modo 12), se fuerza el valor 15
    modo = next((e for e in compat.findall(W + "compatSetting")
                 if e.get(W + "name") == "compatibilityMode" and e.get(W + "uri") == "http://schemas.microsoft.com/office/word"), None)
    if modo is None:
        modo = etree.SubElement(compat, W + "compatSetting")
        modo.set(W + "name", "compatibilityMode")
        modo.set(W + "uri", "http://schemas.microsoft.com/office/word")
    modo.set(W + "val", "15")
    mf = mp.find(M + "mathFont")
    if mf is None:
        mf = etree.Element(M + "mathFont")
        mp.insert(0, mf)
    mf.set(M + "val", MATE)
    tfl = s.find(W + "themeFontLang")
    if tfl is not None:
        tfl.set(W + "val", "es-AR")
    # orden del esquema: ... zoom, ..., embedTrueTypeFonts, embedSystemFonts, saveSubsetFonts ...
    if con_fuentes and s.find(W + "embedTrueTypeFonts") is None:
        ancla = s.find(W + "embedSystemFonts")
        nuevo = etree.Element(W + "embedTrueTypeFonts")
        if ancla is not None:
            ancla.addprevious(nuevo)
        else:
            zoom = s.find(W + "zoom")
            (zoom.addnext(nuevo) if zoom is not None else s.insert(0, nuevo))
    # doble faz: margenes espejados (despues de embedSystemFonts / saveSubsetFonts)
    if s.find(W + "mirrorMargins") is None:
        ancla = s.find(W + "saveSubsetFonts")
        if ancla is None:
            ancla = s.find(W + "embedSystemFonts")
        if ancla is None:
            ancla = s.find(W + "embedTrueTypeFonts")
        if ancla is None:
            ancla = s.find(W + "zoom")
        mm = etree.Element(W + "mirrorMargins")
        (ancla.addnext(mm) if ancla is not None else s.insert(0, mm))
    if s.find(W + "autoHyphenation") is None:
        dts = s.find(W + "defaultTabStop")
        if dts is not None:
            ah = etree.Element(W + "autoHyphenation")
            dts.addnext(ah)
            ah.addnext(etree.Element(W + "doNotHyphenateCaps"))
    # cabeza de hoja distinta en pares e impares (despues de doNotHyphenateCaps)
    if s.find(W + "evenAndOddHeaders") is None:
        ancla = s.find(W + "doNotHyphenateCaps")
        if ancla is None:
            ancla = s.find(W + "defaultTabStop")
        eo = etree.Element(W + "evenAndOddHeaders")
        (ancla.addnext(eo) if ancla is not None else s.append(eo))
    for tag, val in (("decimalSymbol", ","), ("listSeparator", ";")):
        el = s.find(W + tag)
        if el is not None:
            el.set(W + "val", val)
    return etree.tostring(s, xml_declaration=True, encoding="UTF-8", standalone=True)


def escribir_zip(destino, partes):
    orden = ["[Content_Types].xml", "_rels/.rels"] + [n for n in partes if n not in ("[Content_Types].xml", "_rels/.rels")]
    tmp = destino + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for n in orden:
            z.writestr(n, partes[n])
    os.replace(tmp, destino)


# ---------------------------------------------------------------------------
# Caratula (modelo habitual de carátula; editable)
# ---------------------------------------------------------------------------
CARATULA_DEFECTO = {
    "encabezado": "Trabajo Práctico de laboratorio",   # texto fiel del modelo
    "numero": "",
    "titulo": "",
    "materia": "",
    "anio": "",
    "curso": "",
    "integrantes": [],       # [{"nombre": "...", "legajo": "..."}]; sin lista: dos filas vacias
    "institucion": [],       # opcional: el modelo habitual no lo trae 
    "extra": [],             # opcional: [["Fecha de entrega", "..."]]
}


def _run(texto, estilo=None, negrita=False):
    rpr = ""
    if estilo or negrita:
        rpr = "<w:rPr>" + (f'<w:rStyle w:val="{estilo}"/>' if estilo else "") + ("<w:b/><w:bCs/>" if negrita else "") + "</w:rPr>"
    return f'<w:r>{rpr}<w:t xml:space="preserve">{esc(texto)}</w:t></w:r>'


TABR = "<w:r><w:tab/></w:r>"


def integrantes_xml(lista, rotulo_id="Legajo"):
    """Tabla de integrantes de la caratula: "Apellido y nombre" y el identificador (por defecto "Legajo"; se
    cambia con caratula.rotulo_id del JSON), una fila por integrante (sin limite fijo); sin lista, dos filas
    vacias para completar a mano."""
    filas = [(str(i.get("nombre", "")), str(i.get("legajo", ""))) for i in (lista or [])
             if str(i.get("nombre", "")).strip() or str(i.get("legajo", "")).strip()]
    filas = filas or [("", ""), ("", "")]
    w1 = round((ANCHO - 240) * 0.70)
    w2 = ANCHO - 240 - w1
    lin = lambda v, sz: f'<w:{v} w:val="single" w:sz="{sz}" w:space="0" w:color="{TINTA}"/>'  # noqa: E731
    bordes = ("<w:tblBorders>" + lin("top", 12) + lin("left", 6) + lin("bottom", 12) + lin("right", 6)
              + lin("insideH", 4) + lin("insideV", 4) + "</w:tblBorders>")

    def celda(ancho, texto, negrita=False):
        return (f'<w:tc><w:tcPr><w:tcW w:w="{ancho}" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>'
                '<w:p><w:pPr><w:spacing w:before="40" w:after="40"/></w:pPr>'
                + (_run(texto, negrita=negrita) if texto.strip() else "") + "</w:p></w:tc>")

    def fila(a, b, cab=False):
        alto = 340 if cab else 620
        enc = "<w:tblHeader/>" if cab else ""
        return (f'<w:tr><w:trPr><w:cantSplit/><w:trHeight w:val="{alto}" w:hRule="atLeast"/>{enc}</w:trPr>'
                + celda(w1, a, cab or False) + celda(w2, b, cab or False) + "</w:tr>")

    cuerpo = fila("Apellido y nombre", rotulo_id, True) + "".join(fila(n, l) for n, l in filas)
    aire = 120    # el filete se dibuja medio trazo hacia afuera: la tabla entra para no invadir el margen
    return ('<w:tbl><w:tblPr><w:tblW w:w="' + str(ANCHO - 2 * aire) + f'" w:type="dxa"/><w:tblInd w:w="{aire}" w:type="dxa"/>' + bordes +
            '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="100" w:type="dxa"/>'
            '<w:right w:w="100" w:type="dxa"/></w:tblCellMar></w:tblPr>'
            f'<w:tblGrid><w:gridCol w:w="{w1}"/><w:gridCol w:w="{w2}"/></w:tblGrid>{cuerpo}</w:tbl>'
            '<w:p><w:pPr><w:spacing w:before="0" w:after="0"/></w:pPr></w:p>')


def caratula_xml(d, logo_alto_cm=0.0):
    """logo_alto_cm: si la caratula lleva logo (parrafo que inserta docx.lua antes de este XML),
    el espacio sobre el encabezado se reduce en esa altura para no correr el resto de la hoja."""
    c = dict(CARATULA_DEFECTO, **(d or {}))
    x = []
    for linea in c["institucion"]:
        x.append(f'<w:p><w:pPr><w:pStyle w:val="CaratulaMarco"/></w:pPr>{_run(linea)}</w:p>')
    antes = tw(max(5.2 if not c["institucion"] else 3.6, 0) - (logo_alto_cm + 0.4 if logo_alto_cm else 0))
    # "Trabajo Practico de laboratorio N°XX" (numero en azul; vacio = renglon)
    num = _run(str(c["numero"]), "Numero") if str(c["numero"]).strip() else TABR
    x.append(f'<w:p><w:pPr><w:pStyle w:val="CaratulaTP"/><w:tabs><w:tab w:val="left" w:leader="underscore" '
             f'w:pos="{tw(10.5)}"/></w:tabs><w:spacing w:before="{antes}"/></w:pPr>'
             f'{_run(c["encabezado"] + " N° ")}{num}</w:p>')
    # "Titulo del practico"
    tit = _run(c["titulo"]) if c["titulo"].strip() else TABR
    x.append(f'<w:p><w:pPr><w:pStyle w:val="CaratulaTitulo"/><w:tabs><w:tab w:val="left" w:leader="underscore" '
             f'w:pos="{ANCHO}"/></w:tabs></w:pPr>{tit}</w:p>')
    campos = [("Materia:", c["materia"]), ("Año:", c["anio"]), ("Curso:", c["curso"])]
    campos += [(f"{k}:", v) for k, v in c["extra"]]
    for i, (etq, val) in enumerate(campos):
        esp = f'<w:spacing w:before="{tw(7.0)}"/>' if i == 0 else ""
        valor = (_run(str(val), negrita=True) if str(val).strip() else TABR)
        x.append(f'<w:p><w:pPr><w:pStyle w:val="CaratulaCampo"/>{esp}</w:pPr>{_run(etq)}{TABR}{valor}</w:p>')
    x.append(integrantes_xml(c["integrantes"], str(c.get("rotulo_id") or "Legajo")))
    # fin de la seccion de la caratula: sin encabezado ni pie
    x.append(f"<w:p><w:pPr>{seccion_xml(con_cabecera=False)}</w:pPr></w:p>")
    return "".join(x)


# ---------------------------------------------------------------------------
# Fuentes incrustadas
# ---------------------------------------------------------------------------
def fuentes_docx(trabajo):
    """Copias de fonts/graficos con familia "Estudio Sans" (4 estilos) + Noto Sans Math."""
    from fontTools.ttLib import TTFont
    salida = []
    for estilo, archivo, embed in ESTILOS_FUENTE:
        destino = os.path.join(trabajo, "EstudioSans-" + estilo.replace(" ", "") + ".ttf")
        t = TTFont(os.path.join(F_PDF, archivo))
        nt = t["name"]
        for pid, eid, lid in ((3, 1, 0x409), (1, 0, 0)):
            nt.setName(FAMILIA, 1, pid, eid, lid)
            nt.setName(estilo, 2, pid, eid, lid)
            nt.setName(f"{FAMILIA} {estilo}" if estilo != "Regular" else FAMILIA, 4, pid, eid, lid)
            nt.setName("EstudioSans-" + estilo.replace(" ", ""), 6, pid, eid, lid)
        for i in (16, 17, 21, 22):
            nt.removeNames(nameID=i)
        t.save(destino)
        salida.append((FAMILIA, embed, destino))
    salida.append((MATE, "embedRegular", os.path.join(F_ORIG, "NotoSansMath-Regular.ttf")))
    salida.append((MARCAS, "embedRegular", fuente_marcas(trabajo)))
    return salida


def fuente_marcas(trabajo):
    """Subconjunto de Noto Sans Symbols 2 con solo el visto, el aspa y el asterisco de los
    resumenes (U+2713, U+2717, U+2731), como familia "Estudio Marcas" (igual que en el HTML)."""
    from fontTools import subset
    from fontTools.ttLib import TTFont
    destino = os.path.join(trabajo, "EstudioMarcas.ttf")
    op = subset.Options()
    op.layout_features = []
    op.name_IDs = [1, 2, 3, 4, 5, 6]
    op.notdef_outline = True
    f = subset.load_font(os.path.join(F_ORIG, "NotoSansSymbols2-Regular.ttf"), op)
    sb = subset.Subsetter(op)
    sb.populate(unicodes=[0x2713, 0x2717, 0x2731, 0x20])
    sb.subset(f)
    nt = f["name"]
    for pid, eid, lid in ((3, 1, 0x409), (1, 0, 0)):
        nt.setName(MARCAS, 1, pid, eid, lid)
        nt.setName("Regular", 2, pid, eid, lid)
        nt.setName(MARCAS, 4, pid, eid, lid)
        nt.setName("EstudioMarcas-Regular", 6, pid, eid, lid)
    # metricas de linea como las de Alegreya Sans: Noto Symbols 2 tiene ascenso y descenso enormes
    # y una sola aspa agrandaria todo el renglon
    ref = TTFont(os.path.join(F_PDF, "EstudioSansPDF-Regular.ttf"))
    f["hhea"].ascent, f["hhea"].descent, f["hhea"].lineGap = ref["hhea"].ascent, ref["hhea"].descent, 0
    for k in ("sTypoAscender", "sTypoDescender", "sTypoLineGap", "usWinAscent", "usWinDescent"):
        setattr(f["OS/2"], k, getattr(ref["OS/2"], k))
    subset.save_font(f, destino, op)
    return destino


def _clave(nombre):
    return "{" + str(uuid.uuid5(uuid.NAMESPACE_URL, "estudio-docx/" + nombre)).upper() + "}"


def ofuscar(datos, clave):
    """ECMA-376 parte 1, 17.8.1: XOR de los primeros 32 bytes con la clave GUID invertida."""
    k = bytes.fromhex(clave.strip("{}").replace("-", ""))[::-1]
    b = bytearray(datos)
    for i in range(32):
        b[i] ^= k[i % 16]
    return bytes(b)


def _firma(ttf):
    from fontTools.ttLib import TTFont
    t = TTFont(ttf, lazy=True)
    o = t["OS/2"]
    p = o.panose
    panose = "".join(f"{v:02X}" for v in (p.bFamilyType, p.bSerifStyle, p.bWeight, p.bProportion, p.bContrast,
                                            p.bStrokeVariation, p.bArmStyle, p.bLetterForm, p.bMidline, p.bXHeight))
    sig = (f'<w:sig w:usb0="{o.ulUnicodeRange1:08X}" w:usb1="{o.ulUnicodeRange2:08X}" '
           f'w:usb2="{o.ulUnicodeRange3:08X}" w:usb3="{o.ulUnicodeRange4:08X}" '
           f'w:csb0="{o.ulCodePageRange1:08X}" w:csb1="{o.ulCodePageRange2:08X}"/>')
    return panose, sig, o.fsType


def incrustar(partes, trabajo):
    fuentes = fuentes_docx(trabajo)
    por_familia, rels = {}, []
    for i, (fam, embed, ruta) in enumerate(fuentes, 1):
        panose, sig, fs = _firma(ruta)
        if fs & 0x000E == 0x0002:
            raise SystemExit(f"{ruta}: la licencia de la fuente no permite incrustarla (fsType={fs})")
        clave = _clave(os.path.basename(ruta))
        nombre = f"fonts/font{i}.odttf"
        partes["word/" + nombre] = ofuscar(open(ruta, "rb").read(), clave)
        rid = f"rIdFuente{i}"
        rels.append(f'<Relationship Id="{rid}" Type="{REL_FUENTE}" Target="{nombre}"/>')
        d = por_familia.setdefault(fam, {"panose": panose, "sig": sig, "embeds": []})
        d["embeds"].append(f'<w:{embed} r:id="{rid}" w:fontKey="{clave}"/>')
    orden = {"embedRegular": 0, "embedBold": 1, "embedItalic": 2, "embedBoldItalic": 3}
    fx = [DECL, f'<w:fonts {NSDECL}>']
    for fam, d in por_familia.items():
        embeds = sorted(d["embeds"], key=lambda e: orden[re.match(r"<w:(\w+)", e).group(1)])
        fx.append(f'<w:font w:name="{fam}"><w:panose1 w:val="{d["panose"]}"/><w:charset w:val="00"/>'
                  f'<w:family w:val="swiss"/><w:pitch w:val="variable"/>{d["sig"]}{"".join(embeds)}</w:font>')
    fx.append(f'<w:font w:name="{CODIGO}"><w:panose1 w:val="020B0609020204030204"/><w:charset w:val="00"/>'
              '<w:family w:val="modern"/><w:pitch w:val="fixed"/></w:font>')
    fx.append("</w:fonts>")
    partes["word/fontTable.xml"] = "".join(fx).encode("utf-8")
    partes["word/_rels/fontTable.xml.rels"] = (
        DECL + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + "".join(rels) + "</Relationships>").encode("utf-8")
    ct = partes["[Content_Types].xml"].decode("utf-8")
    if 'Extension="odttf"' not in ct:
        ct = ct.replace("<Default ", f'<Default Extension="odttf" ContentType="{CT_ODTTF}"/><Default ', 1)
    partes["[Content_Types].xml"] = ct.encode("utf-8")
    partes["word/settings.xml"] = ajustes(partes["word/settings.xml"], con_fuentes=True)
    return [(f, e, os.path.basename(r)) for f, e, r in fuentes]


# ---------------------------------------------------------------------------
# Post-proceso del documento
# ---------------------------------------------------------------------------
DIGITOS = re.compile(r"^[0-9]+$")
# cuerpo de letra (pt) de los estilos de parrafo que pueden llevar formulas
TAM_ESTILO = {"Caption": 10, "ImageCaption": 10, "TableCaption": 10, "Supuesto": 10.5, "FootnoteText": 10}
TAM_PERFIL = {
    "tp": TAM_ESTILO,
    "resumen": {"TablaTexto": 9.5, "EpigrafeFigura": 9.5, "NotaMargen": 9.5, "TableCaption": 10, "Sintesis": 11.5,
                "SintesisCont": 11.5, "GlosarioT": 11, "GlosarioD": 11, "EcuacionP": 13, "EcNum": 11.5,
                "Colgado": 9.6},
    "material": {"TablaTexto": 10.5, "Supuesto": 10.4, "Errata": 10.4, "EpigrafeMaterial": 9.3, "Consigna": 10.4},
}
# color y negrita de las formulas segun el estilo del parrafo (verde solo en "Resultado")
COLOR_ESTILO = {"Resultado": (VERDE, True), "Errata": (ROJO, False)}


def listas(xml, base=0.6):
    """numbering.xml de Pandoc: vinetas en Symbol y sin fuente fija. Se pasan a
    la letra del sistema, con la raya corta de los resumenes y sangria menor."""
    n = etree.fromstring(xml)
    for lvl in n.iter(W + "lvl"):
        il = int(lvl.get(W + "ilvl"))
        fmt = lvl.find(W + "numFmt")
        txt = lvl.find(W + "lvlText")
        if fmt is not None and fmt.get(W + "val") == "bullet" and txt is not None:
            txt.set(W + "val", "–")          # igual que los resumenes HTML (list-style "– ")
        ppr = lvl.find(W + "pPr")
        if ppr is None:
            ppr = etree.SubElement(lvl, W + "pPr")
        ind = ppr.find(W + "ind")
        if ind is None:
            ind = etree.SubElement(ppr, W + "ind")
        ind.set(W + "left", tw(base + 0.6 * il + 0.5))
        ind.set(W + "hanging", tw(0.5))
        rpr = lvl.find(W + "rPr")
        if rpr is None:
            rpr = etree.SubElement(lvl, W + "rPr")
        for f in rpr.findall(W + "rFonts"):
            rpr.remove(f)
        f = etree.Element(W + "rFonts")
        for at in ("ascii", "hAnsi", "cs", "eastAsia"):
            f.set(W + at, FAMILIA)
        f.set(W + "hint", "default")
        rpr.insert(0, f)
    return etree.tostring(n, xml_declaration=True, encoding="UTF-8", standalone=True)


def _texto_r(r):
    t = r.find(M + "t")
    return t.text if t is not None and t.text is not None else None


def formulas(doc, avisos, perfil="tp"):
    """Letra recta en todas las corridas matematicas, cocientes apilados,
    decimales con coma en una sola corrida, fuente de formulas."""
    n = 0
    for om in doc.iter(M + "oMath"):
        n += 1
    # 1) numeros decimales "3" "," "1" -> "3,1" (Word agrega espacio despues de la coma)
    for padre in {r.getparent() for r in doc.iter(M + "r")}:
        hijos = list(padre)
        i = 0
        while i < len(hijos) - 2:
            a, b, c = hijos[i:i + 3]
            if all(x.tag == M + "r" for x in (a, b, c)):
                ta, tb, tc = _texto_r(a), _texto_r(b), _texto_r(c)
                if ta and tc and DIGITOS.match(ta.split(",")[-1]) and tb == "," and DIGITOS.match(tc):
                    a.find(M + "t").text = ta + "," + tc
                    padre.remove(b)
                    padre.remove(c)
                    hijos = list(padre)
                    continue
            i += 1
    # 1b) varias formulas por renglon en un `aligned` (`a &= b & c &= d`): Word, como LaTeX, no
    #     deja espacio entre pares de columnas (el HTML si). Un cuadratin antes de cada marcador
    #     de alineacion par (el 2.o, el 4.o...) los separa.
    for fila in doc.iter(M + "eqArr"):
        for e in fila.findall(M + "e"):
            marcas = [r for r in e.findall(M + "r") if _texto_r(r) == "&"]
            for k, marca in enumerate(marcas, 1):
                if k % 2 == 0:
                    sp = etree.Element(M + "r")
                    t = etree.SubElement(sp, M + "t")
                    t.text = " "
                    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
                    marca.addprevious(sp)
    # 2) letra recta, fuente matematica y cuerpo en cada corrida. Noto Sans Math
    #    tiene la altura de x mas grande que Alegreya Sans: va un 9 % mas chica
    #    que el texto del parrafo para que se vean del mismo tamano.
    for r in doc.iter(M + "r"):
        p = next(r.iterancestors(W + "p"), None)
        est = p.find(W + "pPr/" + W + "pStyle") if p is not None else None
        nombre_est = est.get(W + "val") if est is not None else ""
        tam = TAM_PERFIL[perfil].get(nombre_est, 12)
        mrpr = r.find(M + "rPr")
        if mrpr is None:
            mrpr = etree.Element(M + "rPr")
            r.insert(0, mrpr)
        if mrpr.find(M + "sty") is None and mrpr.find(M + "nor") is None:
            etree.SubElement(mrpr, M + "sty").set(M + "val", "p")
        wrpr = r.find(W + "rPr")
        if wrpr is None:
            wrpr = etree.Element(W + "rPr")
            mrpr.addnext(wrpr)
        f = wrpr.find(W + "rFonts")
        if f is None:
            f = etree.Element(W + "rFonts")
            wrpr.insert(0, f)
        for at in ("ascii", "hAnsi", "cs", "eastAsia"):
            f.set(W + at, MATE)
        for tag in ("sz", "szCs"):
            el = wrpr.find(W + tag)
            if el is None:
                el = etree.SubElement(wrpr, W + tag)
            el.set(W + "val", str(round(tam * 0.91 * 2)))
        if perfil != "tp" and nombre_est in COLOR_ESTILO:
            col, neg = COLOR_ESTILO[nombre_est]
            poner_rpr(wrpr, color=col, negrita=neg)
        t = _texto_r(r)
        if t and "/" in t and not any("cociente en linea" in a for a in avisos):
            avisos.append(f"cociente en linea «{t}» (y quiza otros) en una formula: escribir \\frac{{..}}{{..}}")
    # 3) cocientes siempre apilados
    for tipo in doc.iter(M + "type"):
        if tipo.getparent().tag == M + "fPr" and tipo.get(M + "val") in ("lin", "skw", "noBar"):
            if tipo.get(M + "val") != "noBar":
                tipo.set(M + "val", "bar")
    return n


def tablas(doc):
    n = 0
    for tbl in doc.iter(W + "tbl"):
        n += 1
        # columnas separadas por filetes verticales finos y aire a los lados del texto
        if tbl.find(W + "tblPr/" + W + "tblBorders") is None or True:
            lin = lambda v, sz, col: f'<w:{v} w:val="single" w:sz="{sz}" w:space="0" w:color="{col}"/>'  # noqa: E731
            tblpr(tbl, tblBorders="<w:tblBorders>" + lin("top", 8, TINTA) + lin("bottom", 8, TINTA)
                  + lin("insideH", 4, FILETE) + lin("insideV", 4, FILETE) + "</w:tblBorders>",
                  tblCellMar='<w:tblCellMar><w:top w:w="30" w:type="dxa"/><w:left w:w="110" w:type="dxa"/>'
                             '<w:bottom w:w="30" w:type="dxa"/><w:right w:w="110" w:type="dxa"/></w:tblCellMar>')
        tpr = tbl.find(W + "tblPr")
        lay = tpr.find(W + "tblLayout")
        if lay is None:
            lay = etree.SubElement(tpr, W + "tblLayout")
            # orden del esquema: tblLayout va antes de tblCellMar y tblLook
            look = tpr.find(W + "tblLook")
            if look is not None:
                look.addprevious(lay)
        lay.set(W + "type", "autofit")
        w = tpr.find(W + "tblW")
        if w is not None:
            w.set(W + "type", "auto")
            w.set(W + "w", "0")
        for tr in tbl.findall(W + "tr"):
            trpr = tr.find(W + "trPr")
            if trpr is None:
                trpr = etree.Element(W + "trPr")
                tr.insert(0, trpr)
            if trpr.find(W + "cantSplit") is None:
                trpr.insert(0, etree.Element(W + "cantSplit"))
        filas = tbl.findall(W + "tr")
        if len(filas) <= 25:  # tabla que cabe en una hoja: cada fila con la siguiente, para que no se parta entre hojas
            for tr in filas[:-1]:
                for p in tr.iter(W + "p"):
                    ppr(p, keepNext="<w:keepNext/>")
        # sin w:caps en ninguna celda (bug de autoajuste conocido)
        for caps in tbl.iter(W + "caps"):
            caps.getparent().remove(caps)
    # un item de lista (por ejemplo cada entrada de la bibliografia) no se parte entre hojas
    for p in doc.iter(W + "p"):
        pr = p.find(W + "pPr")
        if pr is not None and pr.find(W + "numPr") is not None:
            ppr(p, keepLines="<w:keepLines/>")
        # un parrafo que termina en «:» va con lo que introduce (ecuacion, lista o tabla)
        if p.getparent() is not None and p.getparent().tag == W + "body":
            txt = "".join(p.itertext()).rstrip()
            if txt.endswith(":"):
                ppr(p, keepNext="<w:keepNext/>")
    return n



ORDEN_TBLPR = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize", "tblStyleColBandSize", "tblW",
               "jc", "tblCellSpacing", "tblInd", "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook"]
ORDEN_TCPR = ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap", "tcMar", "textDirection",
              "tcFitText", "vAlign", "hideMark"]
ORDEN_RPR = ["rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike", "dstrike", "outline", "shadow",
             "emboss", "imprint", "noProof", "snapToGrid", "vanish", "webHidden", "color", "spacing", "w", "kern",
             "position", "sz", "szCs", "highlight", "u", "effect", "bdr", "shd", "fitText", "vertAlign"]
ORDEN_PPR = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr",
             "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap", "overflowPunct",
             "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind",
             "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc", "textDirection", "textAlignment",
             "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr", "pPrChange"]


def _el(xml):
    return etree.fromstring(f"<r {NSDECL}>{xml}</r>")[0]


def _reordenar(pr, orden, cambios):
    hijos = {etree.QName(h).localname: h for h in pr}
    for k, v in cambios.items():
        if v is None:
            hijos.pop(k, None)
        else:
            hijos[k] = _el(v)
    for h in list(pr):
        pr.remove(h)
    for k in orden:
        if k in hijos:
            pr.append(hijos.pop(k))
    for h in hijos.values():
        pr.append(h)


def tblpr(tbl, **c):
    _reordenar(tbl.find(W + "tblPr"), ORDEN_TBLPR, c)


def tcpr(tc, **c):
    pr = tc.find(W + "tcPr")
    if pr is None:
        pr = etree.Element(W + "tcPr")
        tc.insert(0, pr)
    _reordenar(pr, ORDEN_TCPR, c)


def ppr_de(p):
    pr = p.find(W + "pPr")
    if pr is None:
        pr = etree.Element(W + "pPr")
        p.insert(0, pr)
    return pr


def ppr(p, **c):
    _reordenar(ppr_de(p), ORDEN_PPR, c)


def poner_rpr(rpr, color=None, negrita=False):
    cambios = {}
    if negrita:
        cambios["b"] = "<w:b/>"
        cambios["bCs"] = "<w:bCs/>"
    if color:
        cambios["color"] = f'<w:color w:val="{color}"/>'
    _reordenar(rpr, ORDEN_RPR, cambios)


def formato_celda(tc, negrita=False, color=None):
    """Negrita y/o color en todas las corridas de la celda (texto y formulas)."""
    for r in tc.iter(W + "r", M + "r"):
        rpr = r.find(W + "rPr")
        if rpr is None:
            rpr = etree.Element(W + "rPr")
            (r.find(M + "rPr").addnext(rpr) if r.find(M + "rPr") is not None else r.insert(0, rpr))
        poner_rpr(rpr, color=color, negrita=negrita)


def estilo_p(p):
    e = p.find(W + "pPr/" + W + "pStyle")
    return e.get(W + "val") if e is not None else ""


def poner_estilo(p, nombre):
    pr = ppr_de(p)
    e = pr.find(W + "pStyle")
    if e is None:
        e = etree.Element(W + "pStyle")
        pr.insert(0, e)
    e.set(W + "val", nombre)


def anchos_tabla(tbl, anchos):
    grid = tbl.find(W + "tblGrid")
    for g in list(grid):
        grid.remove(g)
    for a in anchos:
        grid.append(_el(f'<w:gridCol w:w="{a}"/>'))
    for tr in tbl.findall(W + "tr"):
        col = 0
        for tc in tr.findall(W + "tc"):
            pr = tc.find(W + "tcPr")
            gs = pr.find(W + "gridSpan") if pr is not None else None
            span = int(gs.get(W + "val")) if gs is not None else 1
            tcpr(tc, tcW=f'<w:tcW w:w="{sum(anchos[col:col + span])}" w:type="dxa"/>')
            col += span


def sin_partir(tbl):
    for tr in tbl.findall(W + "tr"):
        trpr = tr.find(W + "trPr")
        if trpr is None:
            trpr = etree.Element(W + "trPr")
            tr.insert(0, trpr)
        if trpr.find(W + "cantSplit") is None:
            trpr.insert(0, etree.Element(W + "cantSplit"))


def fijar(tbl, anchos, ind, **extra):
    tblpr(tbl, tblW=f'<w:tblW w:w="{sum(anchos)}" w:type="dxa"/>', tblInd=f'<w:tblInd w:w="{ind}" w:type="dxa"/>',
          tblLayout='<w:tblLayout w:type="fixed"/>', **extra)
    anchos_tabla(tbl, anchos)


def _texto_celda(tc):
    return "".join((t.text or "") for t in tc.iter(W + "t", M + "t"))


def repartir(tbl, total):
    """Anchos de columna de una tabla de datos, a partir del texto: ancho natural de cada
    columna (el renglon mas largo, acotado) y el total repartido en proporcion."""
    n = len(tbl.find(W + "tblGrid"))
    nat = [1.4] * n
    for tr in tbl.findall(W + "tr"):
        col = 0
        for tc in tr.findall(W + "tc"):
            pr = tc.find(W + "tcPr")
            gs = pr.find(W + "gridSpan") if pr is not None else None
            span = int(gs.get(W + "val")) if gs is not None else 1
            if span == 1 and col < n:
                nat[col] = max(nat[col], min(len(_texto_celda(tc)) * 0.2 + 0.7, 7.5))
            col += span
    k = total / sum(nat)                                    # twips por cm natural
    anchos = [max(twi(1.3), round(a * k)) for a in nat]
    sobra = total - sum(anchos)
    anchos[anchos.index(max(anchos))] += sobra
    return anchos


def libro(doc, perfil):
    """Resumen y material: traduce las tablas de diseno que armaron los filtros (notas al
    margen, figuras, ecuaciones, ejercicios, glosario) y ajusta las tablas de datos, la
    sangria de los parrafos como en el HTML (p + p) y los espacios entre bloques."""
    body = doc.find(W + "body")
    S = round(PERFILES[perfil]["sangria"] * CM)
    util = ANCHO - S
    n = 0
    for tbl in list(doc.iter(W + "tbl")):
        if any(a.tag == W + "tc" for a in tbl.iterancestors()):
            continue                                        # anidada: la deja como esta
        n += 1
        e = tbl.find(W + "tblPr/" + W + "tblStyle")
        est = e.get(W + "val") if e is not None else "Table"
        filas = tbl.findall(W + "tr")
        if est in ("TablaNota", "TablaFigura"):
            a1 = round(util * 0.72)
            fijar(tbl, [a1, util - a1], S)
            sin_partir(tbl)
            celdas = filas[0].findall(W + "tc")
            tcpr(celdas[0], tcMar=f'<w:tcMar><w:right w:w="{tw(0.5)}" w:type="dxa"/></w:tcMar>',
                 vAlign='<w:vAlign w:val="bottom"/>' if est == "TablaFigura" else None)
            tcpr(celdas[1], vAlign=f'<w:vAlign w:val="{"bottom" if est == "TablaFigura" else "top"}"/>')
        elif est in ("TablaEcuacion", "TablaClave"):
            num = twi(1.5)
            if est == "TablaClave":
                b = lambda v: f'<w:{v} w:val="single" w:sz="13" w:space="0" w:color="{TINTA}"/>'  # noqa: E731
                # Word dibuja el filete medio trazo hacia afuera: sangria y ancho compensan
                fijar(tbl, [util - 2 * twi(0.1) - num, num], S + twi(0.1),
                      tblBorders='<w:tblBorders>' + b("top") + b("left") + b("bottom") + b("right") + '</w:tblBorders>',
                      tblCellMar='<w:tblCellMar><w:top w:w="60" w:type="dxa"/><w:left w:w="140" w:type="dxa"/>'
                                 '<w:bottom w:w="60" w:type="dxa"/><w:right w:w="140" w:type="dxa"/></w:tblCellMar>')
            else:
                fijar(tbl, [util - num, num], S)
            sin_partir(tbl)
            for tc in filas[0].findall(W + "tc"):
                tcpr(tc, vAlign='<w:vAlign w:val="center"/>')
        elif est == "TablaGlosario":
            a1 = round(util * 0.27)
            fijar(tbl, [a1, util - a1], S)
            sin_partir(tbl)
            for tr in filas:
                tcpr(tr.findall(W + "tc")[0], tcMar=f'<w:tcMar><w:right w:w="{tw(0.3)}" w:type="dxa"/></w:tcMar>')
        elif est in ("TablaEjercicio", "TablaEjercicioLibre"):
            a1 = twi(0.95)
            fijar(tbl, [a1, ANCHO - S - a1], S)
            if est == "TablaEjercicio":
                sin_partir(tbl)
        else:
            # tabla de datos (incluye TablaResultados): ancho completo, columnas segun el texto
            ind = S + twi(0.1)
            if est == "TablaResultados":
                fijas = [twi(1.7), twi(1.5), twi(8.4)]
                anchos = fijas + [ANCHO - S - twi(0.2) - sum(fijas)]
            else:
                anchos = repartir(tbl, util - twi(0.2))
            fijar(tbl, anchos, ind)
            sin_partir(tbl)
            for p in tbl.iter(W + "p"):
                if estilo_p(p) in ("Compact", "BodyText", "FirstParagraph", ""):
                    poner_estilo(p, "TablaTexto")
            if est == "TablaResultados":
                for tr in filas:
                    if tr.find(W + "trPr/" + W + "tblHeader") is not None:
                        continue
                    celdas = tr.findall(W + "tc")
                    for k, tc in enumerate(celdas):
                        if k < 2:
                            formato_celda(tc, negrita=True)
                        elif k == len(celdas) - 1:
                            formato_celda(tc, negrita=True, color=VERDE)
    base = PERFILES[perfil]["sangria"]
    for p in doc.iter(W + "p"):
        if estilo_p(p) not in ("Compact", "BodyText", "FirstParagraph", "TablaTexto", ""):
            num = p.find(W + "pPr/" + W + "numPr")
            if num is not None and num.find(W + "numId").get(W + "val") == "1000":
                il = int(num.find(W + "ilvl").get(W + "val"))
                num.getparent().remove(num)
                ppr(p, ind=f'<w:ind w:left="{tw(base + 0.6 * il + 0.5)}" w:firstLine="0"/>')
    # ---- parrafos del cuerpo: sangria entre parrafos seguidos, espacios entre bloques
    hijos = list(body)
    prev = None
    for i, el in enumerate(hijos):
        if el.tag != W + "p":
            prev = "otro"
            continue
        est = estilo_p(el)
        mate = el.find(M + "oMathPara") is not None
        if est in ("BodyText", "FirstParagraph"):
            poner_estilo(el, "FirstParagraph" if (mate or prev != "cuerpo") else "BodyText")
            prev = "otro" if mate else "cuerpo"
        elif est == "Enunciado":
            ppr(el, spacing=f'<w:spacing w:before="{60 if prev == "enun" else 140}"/>')
            prev = "enun"
        else:
            prev = "otro"
        if mate:
            ppr(el, spacing='<w:spacing w:before="120" w:after="120"/>')
    # listas: aire antes y despues del bloque
    lista = [el.tag == W + "p" and el.find(W + "pPr/" + W + "numPr") is not None for el in hijos]
    for i, el in enumerate(hijos):
        if not lista[i]:
            continue
        if i == 0 or not lista[i - 1]:
            ppr(el, spacing='<w:spacing w:before="100" w:after="30"/>')
        if i == len(hijos) - 1 or not lista[i + 1]:
            sp = el.find(W + "pPr/" + W + "spacing")
            antes = sp.get(W + "before") if sp is not None and sp.get(W + "before") else "30"
            ppr(el, spacing=f'<w:spacing w:before="{antes}" w:after="100"/>')
    # espacio despues de cada tabla del nivel del cuerpo (y nunca dos tablas pegadas: Word las fundiria)
    for el in list(body):
        if el.tag == W + "tbl":
            sig = el.getnext()
            if sig is None or sig.tag != W + "p" or estilo_p(sig) in ("BodyText", "FirstParagraph", "Enunciado", "Heading2", "Heading3"):
                alto = 220 if (el.find(W + "tblPr/" + W + "tblStyle") is None or
                               el.find(W + "tblPr/" + W + "tblStyle").get(W + "val") in ("Table", "TablaResultados")) else 120
                el.addnext(_el(f'<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="{alto}" w:lineRule="exact"/>'
                               '<w:rPr><w:sz w:val="2"/></w:rPr></w:pPr></w:p>'))
    return n


LADO_TEXTO, LADO_OBJETO, LADO_FIN = "@@LADO-TEXTO@@", "@@LADO-OBJETO@@", "@@LADO-FIN@@"
ANCHO_LADO = 4650   # twips: 8,2 cm, columna derecha de los objetos angostos
ANCHOS_LADO = {3: [850, 1814, 1985], 4: [567, 1077, 1474, 1531]}


def lados(doc, ancho_total=10206):
    """Pone un objeto angosto (tabla o grafico, con su epigrafe) en una columna a la derecha del texto al que
    pertenece. En el Markdown: un parrafo @@LADO-TEXTO@@, el texto (puede llevar un grafico),
    un parrafo @@LADO-OBJETO@@, el objeto y un parrafo @@LADO-FIN@@. Se arma una tabla de dos columnas sin bordes
    y de una sola fila, que no se parte entre hojas y no se superpone con nada."""
    body = doc.find(W + "body")
    hijos = list(body)
    texto = lambda e: "".join(e.itertext()).strip()  # noqa: E731
    sin_bordes = ("<w:tblBorders>" + "".join(f'<w:{k} w:val="nil"/>' for k in
                                              ("top", "left", "bottom", "right", "insideH", "insideV")) + "</w:tblBorders>")
    ancho_izq = ancho_total - ANCHO_LADO
    n = 0
    i = 0
    while i < len(hijos):
        if hijos[i].tag == W + "p" and texto(hijos[i]) == LADO_TEXTO:
            ini = i
            med = next(k for k in range(i, len(hijos)) if hijos[k].tag == W + "p" and texto(hijos[k]) == LADO_OBJETO)
            fin = next(k for k in range(med, len(hijos)) if hijos[k].tag == W + "p" and texto(hijos[k]) == LADO_FIN)
            izq, der = hijos[ini + 1:med], hijos[med + 1:fin]
            for e in der:
                if e.tag == W + "tbl":
                    cols = len(e.findall(W + "tblGrid/" + W + "gridCol"))
                    fijar(e, ANCHOS_LADO.get(cols) or [ANCHO_LADO // cols] * cols, 0)
            tbl = _el(
                f'<w:tbl><w:tblPr><w:tblW w:w="{ancho_total}" w:type="dxa"/>{sin_bordes}<w:tblLayout w:type="fixed"/>'
                '<w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="0" w:type="dxa"/>'
                '<w:bottom w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tblCellMar>'
                '<w:tblLook w:val="0000"/></w:tblPr>'
                f'<w:tblGrid><w:gridCol w:w="{ancho_izq}"/><w:gridCol w:w="{ANCHO_LADO}"/></w:tblGrid>'
                '<w:tr><w:trPr><w:cantSplit/></w:trPr>'
                f'<w:tc><w:tcPr><w:tcW w:w="{ancho_izq}" w:type="dxa"/>'
                '<w:tcMar><w:right w:w="227" w:type="dxa"/></w:tcMar></w:tcPr></w:tc>'
                f'<w:tc><w:tcPr><w:tcW w:w="{ANCHO_LADO}" w:type="dxa"/></w:tcPr></w:tc></w:tr></w:tbl>')
            tcs = tbl.findall(W + "tr/" + W + "tc")
            for tc, bloque in zip(tcs, (izq, der)):
                for e in bloque:
                    tc.append(e)
                if not bloque or bloque[-1].tag != W + "p":   # una celda termina siempre con un parrafo
                    tc.append(_el('<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/></w:pPr></w:p>'))
            hijos[ini].addprevious(tbl)
            for e in hijos[ini:fin + 1]:
                if e.getparent() is body:
                    body.remove(e)
            n += 1
            i = fin + 1
        else:
            i += 1
    return n


def postproceso(ruta, cabecera, trabajo, perfil="tp", rot=None):
    zin = zipfile.ZipFile(ruta)
    partes = {n: zin.read(n) for n in zin.namelist()}
    zin.close()
    avisos = []
    doc = etree.fromstring(partes["word/document.xml"])
    n_t = tablas(doc) if perfil == "tp" else libro(doc, perfil)     # antes: fija el estilo de cada celda
    n_f = formulas(doc, avisos, perfil)
    if perfil == "tp":
        lados(doc)
    if perfil in ("tp", "material"):   # listas del cuerpo justificadas como el resto del texto
        for p in doc.find(W + "body").findall(W + "p"):
            if p.find(W + "pPr/" + W + "numPr") is not None:
                ppr(p, jc='<w:jc w:val="both"/>')
    for caps in list(doc.iter(W + "caps")):
        caps.getparent().remove(caps)
    partes["word/document.xml"] = etree.tostring(doc, xml_declaration=True, encoding="UTF-8", standalone=True)
    for n in [p for p in partes if re.match(r"word/(header|footer)\d*\.xml$", p)]:
        x = partes[n].decode("utf-8")
        x = x.replace("«CABECERA_MATERIA»", esc(cabecera[0])).replace("«CABECERA_TRABAJO»", esc(cabecera[1]))
        if rot is not None:
            x = x.replace("«ROT_LINEA»", esc(rot.get("materia", "") + " | " + rot.get("tema", "")))
        partes[n] = x.encode("utf-8")
    if "word/numbering.xml" in partes:
        partes["word/numbering.xml"] = listas(partes["word/numbering.xml"], 0.6 if perfil == "tp" else PERFILES[perfil]["sangria"])
    incrustadas = incrustar(partes, trabajo)
    # propiedades: sin autor ni datos personales
    if "docProps/core.xml" in partes:
        c = partes["docProps/core.xml"].decode("utf-8")
        c = re.sub(r"<dc:creator>.*?</dc:creator>", "<dc:creator></dc:creator>", c, flags=re.S)
        partes["docProps/core.xml"] = c.encode("utf-8")
    escribir_zip(ruta, partes)
    return n_f, n_t, incrustadas, avisos


def chequeo(ruta):
    """Chequeo rapido del resultado (no reemplaza abrirlo en Word)."""
    z = zipfile.ZipFile(ruta)
    d = z.read("word/document.xml").decode("utf-8")
    ft = z.read("word/fontTable.xml").decode("utf-8")
    st = z.read("word/styles.xml").decode("utf-8")
    z.close()
    cursiva = len(re.findall(r"<m:r>(?!<m:rPr>)", d))
    return {
        "formulas": d.count("<m:oMath>"),
        "corridas matematicas sin letra recta": cursiva + d.count('m:val="i"'),
        "cocientes apilados": d.count('<m:type m:val="bar"/>'),
        "fuentes incrustadas": len(re.findall(r"<w:embed(Regular|Bold|Italic|BoldItalic) ", ft)),
        "Arial en estilos": st.count("Arial"),
        "w:caps": d.count("<w:caps") + st.count("<w:caps"),
    }


# ---------------------------------------------------------------------------
# Figuras: SVG del Markdown -> PNG de alta resolucion (Word no dibuja SVG con CSS)
# ---------------------------------------------------------------------------
PNG_ANCHO = 2400                     # px; a 11,4 cm de ancho son unos 535 ppp


def svg_a_png(ff, svg, png, trabajo, ancho=PNG_ANCHO):
    """Dibuja el SVG con navegador sin interfaz (ver herramientas/navegador.py),
    con la letra y los colores de la pagina (currentColor, var(--azul), Alegreya Sans con
    cifras de caja alta), y guarda la captura del elemento <svg> sobre fondo blanco."""
    import base64
    import pathlib
    import time
    txt = open(svg, encoding="utf-8").read()
    m = re.search(r'viewBox="\s*([-\d.]+)[ ,]+([-\d.]+)[ ,]+([\d.]+)[ ,]+([\d.]+)\s*"', txt)
    if not m:
        raise SystemExit(f"{svg}: el SVG no tiene viewBox")
    vw, vh = float(m.group(3)), float(m.group(4))
    alto = round(ancho * vh / vw)
    limpio = re.sub(r"<\?xml.*?\?>|<!DOCTYPE[^>]*>|<!--.*?-->", "", txt, flags=re.S)
    fuentes = open(os.path.join(RAIZ, "incluir", "fuentes.html"), encoding="utf-8").read()
    html = ('<!doctype html><html><head><meta charset="utf-8">' + fuentes +
            f'<style>:root{{--tinta:#{TINTA};--azul:#{AZUL};--lapiz:#{LAPIZ};--rojo:#{ROJO};--verde:#{VERDE};'
            '--filete:#C9CCD1;--papel:#fff}'
            f'html,body{{margin:0;padding:0;background:#fff;color:#{TINTA};font-family:"Estudio Sans",sans-serif;'
            'font-variant-numeric:lining-nums proportional-nums}'
            f'svg{{display:block;width:{ancho}px;height:{alto}px;color:#{TINTA};font-family:"Estudio Sans",sans-serif}}'
            '</style></head><body>' + limpio + '</body></html>')
    pagina = os.path.join(trabajo, os.path.basename(png) + ".html")
    with open(pagina, "w", encoding="utf-8") as f:
        f.write(html)
    ff.ventana(ancho + 60, alto + 260)
    ff.ir(pathlib.Path(pagina).as_uri())
    ff.esperar("document.readyState=='complete'")
    ff.js("return document.fonts.ready.then(function(){return 1});")
    time.sleep(.6)
    # pagina completa (el elemento es mas alto que la ventana) y recorte exacto al <svg>
    from PIL import Image
    import io
    im = Image.open(io.BytesIO(ff.captura(completa=True))).convert("RGB")
    if im.size[0] < ancho or im.size[1] < alto:
        raise SystemExit(f"{svg}: la captura salio de {im.size} y hacen falta {ancho}x{alto}")
    im.crop((0, 0, ancho, alto)).save(png)
    return png


def preparar_md(md, trabajo):
    """Copia del Markdown con cada imagen .svg apuntando a su PNG (en la carpeta temporal)."""
    base = os.path.dirname(md)
    texto = open(md, encoding="utf-8").read()
    rutas = []
    for m in re.finditer(r"\]\(([^)\s]+\.svg)\)", texto):
        r = os.path.normpath(os.path.join(base, m.group(1)))
        if r not in rutas:
            rutas.append(r)
    if not rutas:
        return md, 0
    sys.path.insert(0, os.path.join(RAIZ, "herramientas"))
    import captura_espera
    hechos = {}
    with captura_espera.Navegador() as ff:
        for r in rutas:
            hechos[r] = svg_a_png(ff, r, os.path.join(trabajo, f"figura-{len(hechos) + 1}.png"), trabajo)
    nuevo = re.sub(r"\]\(([^)\s]+\.svg)\)",
                   lambda m: "](" + hechos[os.path.normpath(os.path.join(base, m.group(1)))].replace("\\", "/") + ")", texto)
    destino = os.path.join(trabajo, os.path.basename(md))
    with open(destino, "w", encoding="utf-8") as f:
        f.write(nuevo)
    return destino, len(hechos)


def leer_meta(md):
    """Encabezado YAML simple del Markdown (clave: valor)."""
    t = open(md, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", t, re.S)
    meta = {}
    if m:
        for linea in m.group(1).splitlines():
            k, _, v = linea.partition(":")
            if _:
                meta[k.strip()] = v.strip().strip('"')
    return meta


def sin_guiones(docx):
    """Texto de los TP sin separacion silabica: se quita w:autoHyphenation."""
    with zipfile.ZipFile(docx) as z:
        partes = {n: z.read(n) for n in z.namelist()}
    s = etree.fromstring(partes["word/settings.xml"])
    for tag in ("autoHyphenation", "doNotHyphenateCaps"):
        for el in s.findall(W + tag):
            s.remove(el)
    partes["word/settings.xml"] = etree.tostring(s, xml_declaration=True, encoding="UTF-8", standalone=True)
    escribir_zip(docx, partes)


def sin_espejo(docx):
    """Documento solo digital (no se imprime): margenes iguales en todas las hojas (izquierdo = interior,
    derecho = exterior) y la cabeza de hoja siempre del mismo lado, sin w:mirrorMargins ni
    w:evenAndOddHeaders."""
    with zipfile.ZipFile(docx) as z:
        partes = {n: z.read(n) for n in z.namelist()}
    s = etree.fromstring(partes["word/settings.xml"])
    for tag in ("mirrorMargins", "evenAndOddHeaders"):
        for el in s.findall(W + tag):
            s.remove(el)
    partes["word/settings.xml"] = etree.tostring(s, xml_declaration=True, encoding="UTF-8", standalone=True)
    escribir_zip(docx, partes)


def construir(md, salida=None, datos=None, trabajo=None, tipo="tp", modo="extenso", indice=False, practica=False,
              espejo=True):
    md = os.path.abspath(md)
    salida = os.path.abspath(salida or os.path.splitext(md)[0] + ".docx")
    perfil = TIPOS[tipo]
    d = {}
    if datos:
        with open(datos, encoding="utf-8") as f:
            d = json.load(f)
    meta = leer_meta(md)
    car = dict(CARATULA_DEFECTO, **d.get("caratula", {})) if ("caratula" in d and tipo == "tp") else None
    cab = d.get("cabecera", {})
    materia = cab.get("materia") or (car and car["materia"]) or meta.get("materia", "")
    num = (car and str(car["numero"]).strip()) or ""
    trabajo_txt = cab.get("trabajo") or (("Trabajo Práctico N° " + num) if num else ("Trabajo Práctico" if car else ""))
    rot = None
    if perfil == "material":
        rot = {"materia": materia, "tema": cab.get("tema") or meta.get("tema", "")}
    ref = os.path.join(AQUI, PERFILES[perfil]["ref"])
    if not os.path.exists(ref):
        referencia(perfil)
    filtro = os.path.join(AQUI, PERFILES[perfil]["filtro"])
    propio = trabajo is None
    trabajo = trabajo or tempfile.mkdtemp(prefix="estudio_docx_")
    try:
        entrada, n_fig = preparar_md(md, trabajo)
        cmd = [PANDOC, entrada, "-o", salida, "--reference-doc=" + ref, "--lua-filter=" + filtro,
               "--resource-path=" + os.path.dirname(md), "-M", "lang=es-AR"]
        if perfil == "resumen":
            cmd += ["-M", "modo=" + modo]
            if indice:
                cmd += ["-M", "indice=true"]
            if practica:
                cmd += ["-M", "practica=true"]
        if car:
            sys.path.insert(0, os.path.join(RAIZ, "herramientas"))
            import logo as _logo
            lg = _logo.preparar(datos, trabajo)
            ruta_car = os.path.join(trabajo, "caratula.xml")
            with open(ruta_car, "w", encoding="utf-8") as f:
                f.write(caratula_xml(car, lg["alto_cm"] if lg else 0.0))
            cmd += ["-M", "caratula_xml=" + ruta_car]
            if lg:
                cmd += ["-M", "caratula_logo=" + lg["ruta"], "-M", f"caratula_logo_ancho={lg['ancho_cm']:.2f}cm"]
        p = subprocess.run(cmd, cwd=os.path.dirname(md), capture_output=True, text=True, encoding="utf-8")
        if p.returncode:
            raise SystemExit("pandoc: " + p.stderr)
        if p.stderr.strip():
            print(p.stderr.strip())
        n_f, n_t, inc, avisos = postproceso(salida, (materia, trabajo_txt), trabajo, perfil, rot)
        if not espejo:
            sin_espejo(salida)
        if perfil in ("tp", "resumen", "material"):     # sin guionado, como los TP
            sin_guiones(salida)
    finally:
        if propio:
            shutil.rmtree(trabajo, ignore_errors=True)
    for a in avisos:
        print("AVISO:", a)
    print(f"{os.path.basename(salida)}: tipo {tipo}, {n_f} formulas, {n_t} tablas, {n_fig} figuras, "
          f"{len(inc)} archivos de fuente incrustados ({', '.join(sorted({f for f, _, _ in inc}))})")
    return salida


def main():
    ap = argparse.ArgumentParser(description="Markdown -> .docx con el sistema visual v4")
    ap.add_argument("md", nargs="?")
    ap.add_argument("-o", "--salida")
    ap.add_argument("--tipo", choices=sorted(TIPOS), default="tp", help="tp (por defecto), resumen, parcial o soluciones")
    ap.add_argument("--modo", choices=("extenso", "corto"), default="extenso", help="solo resumen")
    ap.add_argument("--datos", help="JSON con la caratula (tp) y/o la cabecera: materia, tema, trabajo")
    ap.add_argument("--indice", action="store_true", help="resumen extenso con indice")
    ap.add_argument("--practica", action="store_true", help="activa los componentes de practica (practica: true)")
    ap.add_argument("--sin-espejo", action="store_true",
                    help="documento solo digital: margenes iguales en todas las hojas (sin doble faz)")
    ap.add_argument("--referencia", action="store_true", help="regenera los reference-*.docx")
    ap.add_argument("--chequeo", action="store_true", help="muestra el chequeo rapido del .docx")
    a = ap.parse_args()
    if a.referencia:
        for perfil in PERFILES:
            print("referencia:", referencia(perfil))
    if a.md:
        s = construir(a.md, a.salida, a.datos, tipo=a.tipo, modo=a.modo, indice=a.indice, practica=a.practica,
                      espejo=not a.sin_espejo)
        if a.chequeo:
            for k, v in chequeo(s).items():
                print(f"  {k}: {v}")
    elif not a.referencia:
        ap.print_help()


if __name__ == "__main__":
    main()
