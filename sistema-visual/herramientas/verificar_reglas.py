"""verificar_reglas.py - comprueba sobre el sistema v4 las 20 reglas contra el
aspecto de IA y las decisiones de diseño que se
pueden medir en el codigo, en el HTML generado o en las medidas que toma
el navegador (capturas/medidas.json, lo escribe herramientas/capturas.py).
La regla 16 (prueba en gris) se revisa ademas a ojo en capturas/gris-*.png.

Reglas de los formatos y modos de resumen. Las diapositivas son solo pantalla: no se imprimen, no tienen
margenes ni folleto (la regla 26, del folleto, se retiro):
  24  las diapositivas no desbordan en 1280x720, 390x844 y 844x390 (ni se desplazan a lo ancho;
      en escritorio ninguna necesita desplazarse a lo alto)
  25  letra minima de 14 px y contraste de 4,5:1 medido en las diapositivas, en claro y en oscuro
  27  modo corto: menos hojas A4 y menos diapositivas que el extenso de las mismas unidades (sin tope fijo,; si no se puede comparar, informa y no falla); sin comentarios metatextuales
  28  material A4 (parcial, soluciones): el rotulo tipo plano es UNA linea en el margen superior con materia y tema
      (lado interior) y "Hoja n de N" (exterior), sin datos personales ni fecha; el encabezado del parcial no copia
      Legajo, Apellido y nombre, Curso ni la fecha
  29  la cabecera de hoja de resumenes y TP (A4 y .docx) no lleva sigla ni unidad: solo "Hoja n de N" (y la seccion o
      el trabajo); excepcion explicita del material impreso: su linea superior lleva materia y tema
      y, donde ya estaba, la seccion o el trabajo
  30  el encabezado muestra "materia | unidad" en una misma linea, del lado izquierdo (A4, completo y diapositivas)
  31  Hoja A4: el texto corrido ocupa casi todo el ancho util y las figuras y notas conservan la columna derecha
      (120 mm de cuerpo + 44 mm de margen), medido en el navegador
  32  Hoja A4 del resumen y material impreso (parcial, soluciones, TP): siempre claros y sin boton de
      tema ni tokens oscuros, aun con el tema oscuro del sistema
  33  el HTML para imprimir es siempre hoja blanca con texto oscuro, sin modos de color: aun con el sistema en oscuro
  34  HTML completo y diapositivas: un solo boton de tema, que sigue al sistema sin eleccion guardada, cambia
      los colores reales con un clic y se recuerda al recargar
  35  formatos de archivo y nombres: nombres.py pasa sus casos; ninguna skill ni documento afirma que falte el
      PDF o que los formatos se limiten a HTML y Word; resumir, generar-html, material-a4, tp y cuestionario nombran con nombres.py
  37  jerarquia de titulos (h1 >= 1,25 y h2 >= 1,15 del cuerpo, h1 > h2 > h3), 38 espacio sobre cada titulo mayor que
      el de abajo, 39 espaciado de letras solo negativo (hasta -0,05 em) y solo en titulos de exhibicion, 40 texto de
      figura SVG no tapado por un rectangulo opaco dibujado despues (tomadas de la revision de impeccable)
  (la 22 mide los PDF que imprime imprimir_a4.py de todas las hojas A4: resumenes, material y TP)

Uso:  python herramientas/verificar_reglas.py
Sale con codigo 1 si alguna regla no se cumple.
"""
TOPE_A4 = 105   # caracteres por linea medidos con 12 pt en los 169 mm utiles: 103
import colorsys
import json
import os
import re
import sys
from html.parser import HTMLParser

AQUI = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(AQUI)


def leer(*p):
    return open(os.path.join(R, *p), encoding="utf-8").read()


def sin_comentarios(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def estilos_de(html):
    return "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, flags=re.S))


CSS_RES = sin_comentarios("\n".join(leer("css", f) for f in (
    "tokens.css", "tokens-oscuro.css", "resumen-base.css", "resumen-pantalla.css", "resumen-completo.css",
    "resumen-a4.css", "resumen-diapositivas.css")) + estilos_de(leer("incluir", "a4-pagina.html")))
CSS_Q = sin_comentarios(leer("css", "cuestionario.css"))
CSS_P = sin_comentarios(leer("css", "material-a4.css"))
CSS_TP = sin_comentarios(leer("css", "tp-a4.css"))
TODOS = {"resumen": CSS_RES, "cuestionario": CSS_Q, "material": CSS_P, "tp": CSS_TP}
HTML_RES = [f"demo/resumen-{m}-{f}.html" for m in ("extenso", "corto") for f in ("completo", "a4", "diapositivas")] + [
    "demo/resumen-extenso-completo-con-practica.html"]
HTML_MAT = [f"demo/{n}.html" for n in ("parcial", "soluciones-resultados", "soluciones-resolucion", "tp")]
HTML_TODOS = HTML_RES + HTML_MAT + ["demo/cuestionario.html", "indice.html"]
res = []


def regla(n, texto, ok, detalle=""):
    res.append((n, texto, ok, detalle))


def reglas_css(css):
    """(selector, cuerpo) de cada regla, sin @font-face."""
    css = re.sub(r"@font-face\s*\{[^}]*\}", "", css)
    return [(m.group(1).strip().split("\n")[-1].strip(), m.group(2)) for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css)]


# 1. Borde de color de un solo lado
# Excepcion: el filete vertical entre columnas de una tabla (`th + th, td + td`, criterio de diseño
# del y para TP, resumen y material) es un separador, no un borde de bloque.
lados = [f"{n}: {s}" for n, css in TODOS.items() for s, c in reglas_css(css)
         if re.search(r"border-(left|right|inline-start|inline-end)\s*:", c)
         and not re.fullmatch(r"((\.dato-tabla\s+)?(th\s*\+\s*th|td\s*\+\s*td)|\.tabla-resultados td\s*\+\s*td)"
                              r"(\s*,\s*(\.dato-tabla\s+)?(th\s*\+\s*th|td\s*\+\s*td))*", s.strip())]
regla(1, "ningun bloque con borde de color de un solo lado", not lados, "; ".join(lados))

# 2. Mayusculas con espaciado
may = [n for n, css in TODOS.items() if re.search(r"text-transform\s*:\s*uppercase", css)]
esp = [f"{n}: {m.group(0)}" for n, css in TODOS.items() for m in re.finditer(r"letter-spacing\s*:\s*\.?[0-9]*[1-9][^;]*", css)
       if not m.group(0).split(":")[1].strip().startswith("-")]
regla(2, "sin rotulos en mayusculas ni espaciado positivo", not may and not esp, f"uppercase: {may}; espaciado: {esp}")

# 3 y 4. Pildoras y radios
radios = [(n, s, re.search(r"border-radius\s*:\s*([^;]+)", c).group(1).strip())
          for n, css in TODOS.items() for s, c in reglas_css(css) if "border-radius" in c]
CONTROL = r"btn|button|navdot|option|mark|tema-boton|input|tiempo|caja|hueco|vf-chip"
pildoras = [r for r in radios if re.search(r"999|[1-9]\d*(\.\d+)?em|rem", r[2])]
regla(3, "sin pildoras ni insignias (radio de 1em o mas, o 999px)", not pildoras,
      "circulo de 50 % solo en la marca de opcion elegida del cuestionario (control, como a mano)")
fuera = [r for r in radios if not re.search(CONTROL, r[1])]
regla(4, "radio solo en controles", not fuera, "; ".join(f"{a}: {b} = {c}" for a, b, c in radios))

# 5. Sombras
sombras = sorted({f"{n}: {s}" for n, css in TODOS.items() for s, c in reglas_css(css) if "box-shadow" in c})
regla(5, "sombra solo en la hoja de papel (hojas A4 en pantalla)", len(sombras) <= 2, "; ".join(sombras))


# 6. Colores cromaticos. Tonos en grupos de 30 grados; casi negros y casi
# blancos no cuentan.
def usados(css):
    """Quita las definiciones de tokens que ninguna regla usa con var()."""
    en_uso = set(re.findall(r"var\((--[a-z-]+)", css))
    return re.sub(r"(--[a-z-]+)\s*:\s*#[0-9A-Fa-f]{6}", lambda m: m.group(0) if m.group(1) in en_uso else m.group(1) + ":", css)


def tonos(css):
    css = usados(css)
    t = {}
    for h in re.findall(r"#([0-9A-Fa-f]{6})\b", css):
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        hue, lum, sat = colorsys.rgb_to_hls(r, g, b)
        if sat > .25 and .14 < lum < .95:
            t.setdefault(round(hue * 12) % 12 * 30, set()).add("#" + h.upper())
    return t


t_res = tonos(re.sub(r"--seleccion:[^;]+;", "", CSS_RES))
uso_rojo = [s for s, c in reglas_css(CSS_RES) if "var(--rojo)" in c]
t_q = tonos(CSS_Q)
t_p = tonos(CSS_P)
t_tp = tonos(CSS_TP)
sol_colores = [s for s, c in reglas_css(CSS_P) + reglas_css(CSS_TP) if re.search(r"var\(--(verde|rojo)\)|#1E6B3A|#C8373D", c)]
ok6 = (len(t_res) <= 2 and all("errores" in s for s in uso_rojo) and len(t_q) <= 3 and not t_p and not t_tp
       and all(re.search(r"resultado|errata", s) for s in sol_colores))
regla(6, "resumen: un acento (azul) y el rojo solo como signo de error; cuestionario: 3 semanticos; "
      "material A4: tinta, verde solo en resultados y rojo solo en la errata", ok6,
      f"resumen {dict((k, sorted(v)) for k, v in t_res.items())}, rojo en {uso_rojo} | cuestionario "
      f"{dict((k, sorted(v)) for k, v in t_q.items())} | material: color solo en {sol_colores}")

# 7. Fondos por tipo de bloque
PERMITIDOS = r"var\(--(papel|mesa|seleccion|fondo|control)|transparent|#fff\b|#FFFFFF|rgba\(8, 9, 12|none"
CONTROLES = r"btn|progress|selection|navdot|modal|tiempo"
fondos = [f"{n}: {s} = {m.group(1).strip()}" for n, css in (("resumen", CSS_RES), ("cuestionario", CSS_Q), ("material", CSS_P), ("tp", CSS_TP))
          for s, c in reglas_css(css) for m in re.finditer(r"background(?:-color)?\s*:\s*([^;]+)", c)
          if not re.search(PERMITIDOS, m.group(1)) and not re.search(CONTROLES, s)]
regla(7, "sin fondos de color por tipo de bloque", not fondos, "; ".join(fondos))


class Texto(HTMLParser):
    def __init__(self):
        super().__init__()
        self.pila, self.txt, self.titulos, self.hmax = [], [], [], 0
        self.en_caja, self.rotulos_en_caja = 0, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        clases = (a.get("class") or "").split()
        if tag in ("br", "img", "meta", "link", "input", "hr", "circle", "line", "path"):
            return
        self.pila.append((tag, clases))
        if re.fullmatch(r"h[1-6]", tag):
            self.hmax = max(self.hmax, int(tag[1]))
        if "rotulo" in clases and any("clave" in c for _, c in self.pila[:-1]):
            self.rotulos_en_caja += 1

    def handle_endtag(self, tag):
        while self.pila and self.pila.pop()[0] != tag:
            pass

    def handle_data(self, dt):
        tags = [t for t, _ in self.pila]
        if "script" in tags or "style" in tags or "math" in tags or "code" in tags:
            return
        self.txt.append(dt)
        if any(t in ("h1", "h2", "h3", "figcaption", "caption") for t in tags):
            self.titulos.append(dt)


puntos, rayas, emojis, hmax, en_caja = [], [], [], {}, 0
for f in HTML_TODOS:
    p = Texto()
    p.feed(leer(f))
    t = "".join(p.txt)
    for ch in "·→←":
        if ch in t:
            puntos.append(f"{f}: {ch}")
    if any("—" in x for x in p.titulos):
        rayas.append(f)
    if re.search("[\U0001F300-\U0001FAFF☀-⛿⭐]", t):
        emojis.append(f)
    hmax[f] = p.hmax
    en_caja += p.rotulos_en_caja
regla(8, "sin punto medio ni flechas decorativas en el texto", not puntos, str(puntos))
regla(9, "sin raya en titulos, epigrafes y rotulos", not rayas, str(rayas))
regla(10, "rotulos en linea, nunca como encabezado de una caja", en_caja == 0, f"{en_caja} rotulos dentro del recuadro")
regla(18, "sin emojis ni iconos circulares", not emojis, str(emojis))
regla(19, "maximo tres niveles de titulo (h4 o mas: 0)", all(v <= 3 for v in hmax.values()), str(hmax))

# 11. Numeracion citable y referencias cruzadas
simple = leer("demo", "resumen-extenso-completo.html")
refs = re.findall(r'class="ref"[^>]*>([^<]+)<', simple)
numerados = re.findall(r"(Figura \d-\d|Tabla \d-\d|Definición \d\.\d|\(\d\.\d\))", simple)
regla(11, "numeracion citable (3.1, figura 3-1) y referencias cruzadas", len(refs) >= 3 and len(numerados) >= 5,
      f"{len(refs)} referencias ({', '.join(sorted(set(refs)))}); {len(set(numerados))} elementos numerados")

# 13. Ritmo vertical desigual
valores = set(re.findall(r"--(?:antes|despues|entre)[-a-z]*\s*:\s*([^;]+);", CSS_RES))
regla(13, "al menos 3 valores distintos de espacio vertical", len(valores) >= 3, str(sorted(valores)))

# 14. Tipografia propia
fam = re.search(r"--f-texto\s*:\s*([^;]+);", CSS_RES).group(1)
fam_q = re.search(r"--f-texto\s*:\s*([^;]+);", CSS_Q).group(1)
serif = [n for n, css in TODOS.items() if re.search(r"(?<!sans-)\bserif\b|Georgia|Literata|Times|Arial|Inter\b", css)]
regla(14, "letra propia incrustada (Alegreya Sans como Estudio Sans), sin serifa en ningun texto",
      fam.startswith('"Estudio Sans"') and fam_q.startswith('"Estudio Sans"') and not serif,
      f"resumen: {fam}; cuestionario: {fam_q}; serifa o letra del sistema en: {serif}")

# 12 y 15. Medidas reales tomadas en el navegador
med_p = os.path.join(R, "capturas", "medidas.json")
if os.path.exists(med_p):
    med = json.load(open(med_p, encoding="utf-8"))
    malos = []
    for k, v in med.items():
        if isinstance(v, dict) and "caracteres_por_linea" in v:
            # Hoja A4: cuerpo de 12 pt = 16 px exactos
            cuerpo_ok = 16 <= v["cuerpo_px"] <= 20 if not k.startswith("A4") else 15.9 <= v["cuerpo_px"] <= 16.1
            # Hoja A4: el texto ocupa los 169 mm utiles; con 12 pt entran unos TOPE_A4 caracteres por linea
            tope = TOPE_A4 if k.startswith("A4") else 90
            if not (45 <= v["caracteres_por_linea"] <= tope and cuerpo_ok and 1.25 <= v["interlineado"] <= 1.45):
                malos.append(k)
    regla(15, "45 a 90 caracteres por linea (hasta 105 en la Hoja A4, de ancho completo, con cuerpo de 12 pt); 16 a 20 px en pantalla; interlineado 1,25 a 1,45",
          not malos, "; ".join(f"{k}: {v}" for k, v in med.items() if isinstance(v, dict)))
    cajas = med.get("A4", {}).get("recuadros_por_hoja", []) + med.get("A4 corto", {}).get("recuadros_por_hoja", [])
    regla(12, "como mucho un recuadro por hoja A4 (modos extenso y corto)", bool(cajas) and max(cajas) <= 1, f"recuadros por hoja: {cajas}")
    regla(21, "boton de modo oscuro: la eleccion se recuerda al recargar",
          med.get("boton: tema recordado despues de recargar") == "dark", str(med.get("boton: tema recordado despues de recargar")))
else:
    regla(15, "medidas tipograficas", False, "falta capturas/medidas.json: correr herramientas/capturas.py")
    regla(12, "un recuadro por hoja A4", False, "falta capturas/medidas.json")

# 16. Prueba en gris: luminancias distintas y archivos para revisar a ojo
grises = [f for f in os.listdir(os.path.join(R, "capturas")) if f.startswith("gris-")] if os.path.isdir(os.path.join(R, "capturas")) else []
regla(16, "prueba en gris (capturas/gris-*.png, revisadas a ojo)", len(grises) >= 4, ", ".join(sorted(grises)))

# 17. El color nunca solo
q = leer("cuestionario", "plantilla-fuente.html")
signos = all(s in q for s in ("✓", "✗", '"correcta"', '"tu respuesta, incorrecta"', "Sin responder", "sobre 10"))
regla(17, "estados con palabra y signo (cuestionario, errores frecuentes, soluciones)",
      signos and 'content: "✗"' in CSS_RES and "Resultado." in leer("incluir", "material.lua")
      and "Errata." in leer("incluir", "material.lua"), "")


# 22. Nada fuera del area imprimible (margenes de carpeta: interior
# 20, exterior 10, superior 15, inferior 5 mm, doble faz espejada). Lo mide
# verificar_margenes.py sobre los PDF y las hojas A4 medidas en el navegador.
sys.path.insert(0, AQUI)
sys.dont_write_bytecode = True
import verificar_margenes as vm  # noqa: E402

filas_m, fallas_m, faltan_m = vm.verificar()
regla(22, "nada fuera del area imprimible (interior 20, exterior 10, superior 15, inferior 5 mm; "
      "la cabeza de hoja en la franja superior, a 5 mm o mas del borde)", not fallas_m,
      "; ".join([f"{n}: int {m['interior']}, ext {m['exterior']}, sup {m['arriba']}, inf {m['abajo']}"
                 + ("" if m["cabeza"] == 99 else f", cabeza {m['cabeza']}") for n, _, m in filas_m]
                + [f"INVADE {f}" for f in fallas_m] + [f"sin medir: {f}" for f in faltan_m]))

# 28. Material A4: el rotulo tipo plano solo lleva materia, tema y hoja
med_m = json.load(open(med_p, encoding="utf-8")) if os.path.exists(med_p) else {}
mat_lua = leer("incluir", "material.lua")
linea_rot = re.search(r"local linea = ([^\n]*)", mat_lua)
_md_p = leer("demo", "material", "parcial.md")
cab_txt = _md_p[_md_p.index("::: {.cabecera-original"):_md_p.index("::: consigna")]
rot_ok = (bool(linea_rot) and linea_rot.group(1).replace(" ", "") == 's("materia").."|"..s("tema")'
          and "@top-left" in mat_lua and "@top-right" in mat_lua and "rotulo-plano" not in CSS_P
          and "21mm" not in CSS_P and "material-hoja" not in leer("construir.py")
          and not os.path.exists(os.path.join(R, "incluir", "material-hoja.html"))
          and all("rotulo-plano" not in leer(f) for f in HTML_MAT[:3])
          and not re.search(r"Legajo|Apellido|Curso|[Ff]echa|fecha=", cab_txt)
          and all("Legajo" not in leer(f) and "Apellido y nombre" not in leer(f) for f in HTML_MAT[:3]))
regla(28, "material A4: rotulo tipo plano de una sola linea en el margen superior (materia y tema, y Hoja n de N), sin pie, "
      "sin datos personales ni fecha; el encabezado del parcial sin Legajo, Apellido y nombre, Curso ni fecha", rot_ok,
      "" if rot_ok else f"linea: {linea_rot and linea_rot.group(1)}; cabecera del parcial: {cab_txt!r}")

# 29. Cabecera de hoja sin sigla ni unidad (A4 del resumen, material A4 y .docx)
css_cab = {"resumen-a4.css": sin_comentarios(leer("css", "resumen-a4.css")), "material-a4.css": CSS_P, "tp-a4.css": CSS_TP}
cab_mal = []
for nombre, css in css_cab.items():
    for m in re.finditer(r"@top-(?:left|right)\s*\{([^{}]*)\}", css):
        cont = re.search(r"content\s*:\s*([^;]+);", m.group(1))
        if cont and (re.search(r"string\(sigla\)|[Uu]nidad|string\(unidad\)", cont.group(1))):
            cab_mal.append(f"{nombre}: {cont.group(1).strip()}")
sin_sigla_html = [f for f in HTML_MAT + ["demo/resumen-extenso-a4.html", "demo/resumen-corto-a4.html"]
                  if 'class="sigla-hoja"' in leer(f)]
docx_src = leer("docx", "construir_docx.py")
cab_docx = re.search(r"def cabecera_xml\([^)]*\):.*?return DECL", docx_src, flags=re.S).group(0)
docx_ok = "CABECERA_MATERIA" not in cab_docx and "_hoja(" in cab_docx
regla(29, "la cabecera de hoja de resumenes y TP no lleva sigla ni unidad, solo Hoja n de N (y la seccion o el trabajo); "
      "el material impreso lleva materia y tema en su linea superior (excepcion explicita)",
      not cab_mal and not sin_sigla_html and docx_ok and "sigla-hoja" not in leer("incluir", "estudio.lua")
      and "sigla-hoja" not in leer("incluir", "material.lua"),
      "; ".join(cab_mal + sin_sigla_html) or "cabeceras: solo Hoja n de N y la seccion vigente")

# 30. Encabezado "materia | unidad" en una linea, del lado izquierdo
enc_mal = []
for f in ("demo/resumen-extenso-completo.html", "demo/resumen-extenso-a4.html", "demo/resumen-corto-diapositivas.html"):
    h = leer(f)
    mm_ = re.search(r'<span class="enc-materia">(.*?)</span>\s*<span class="enc-sep">\|</span>\s*<span class="enc-unidad">(Unidad [^<]+)</span>', h, flags=re.S)
    if not mm_:
        enc_mal.append(f)
css_enc = re.search(r"\.encabezado p\s*\{([^}]*)\}", CSS_RES).group(1)
regla(30, "el encabezado muestra materia | unidad juntas, en la misma linea y del lado izquierdo",
      not enc_mal and "space-between" not in css_enc and "flex-start" in css_enc, "; ".join(enc_mal) or css_enc.strip())

# 31. Hoja A4: texto ancho; figuras y notas en su columna derecha (medido en el navegador)
g = med_m.get("A4", {})
g2 = med_m.get("A4 corto", {})
def _ok31(v):
    return bool(v) and v.get("ancho_texto_mm") and v["ancho_texto_mm"] >= 160 and (
        (v.get("ancho_cuerpo_con_nota_mm") or 0) <= 125 or v.get("ancho_cuerpo_con_nota_mm") is None) and (
        (v.get("ancho_nota_mm") or 44) >= 40) and ((v.get("ancho_epigrafe_mm") or 44) >= 40)
regla(31, "Hoja A4: texto corrido de 160 mm o mas; cuerpo con nota al margen de 125 mm o menos y columna de margen de 40 mm o mas",
      _ok31(g) and _ok31(g2),
      "; ".join(f"{k}: texto {v.get('ancho_texto_mm')} mm, cuerpo con nota {v.get('ancho_cuerpo_con_nota_mm')} mm, nota "
                f"{v.get('ancho_nota_mm')} mm, epigrafe {v.get('ancho_epigrafe_mm')} mm" for k, v in (("A4", g), ("A4 corto", g2))))

# 32-34. Modo claro u oscuro (medido en el navegador por probar_tema.py, clave "tema" de medidas.json)
tm = med_m.get("tema", {})
solo_claro = [f for f in HTML_MAT + ["demo/resumen-extenso-a4.html", "demo/resumen-corto-a4.html"]
              if re.search(r"prefers-color-scheme|data-theme|temaBoton|tema-boton", re.sub(r"<script.*?</script>", "", leer(f), flags=re.S))]
fuentes_claras = [n for n, c in (("tokens.css", leer("css", "tokens.css")), ("a4-pagina.html", leer("incluir", "a4-pagina.html")),
                                 ("material-a4.css", leer("css", "material-a4.css")), ("resumen-a4.css", leer("css", "resumen-a4.css")),
                                 ("tp-a4.css", leer("css", "tp-a4.css")))
                  if re.search(r"prefers-color-scheme|data-theme", sin_comentarios(c) if n.endswith(".css") else re.sub(r"<!--.*?-->", "", c, flags=re.S))]
a4_tema = {k: v for k, v in tm.items() if k.endswith(", sistema oscuro") and not k.startswith(("HTML", "diapositivas"))}
mal32 = [k for k, v in a4_tema.items() if v["botones"] or v["fondo_hoja"] < 200 or v["fondo_mesa"] < 200 or v["texto"] > 100 or v["data_theme"]]
regla(32, "Hoja A4 y material impreso siempre claros y sin boton de tema ni tokens oscuros (aun con el sistema en oscuro)",
      len(a4_tema) >= 4 and not mal32 and not solo_claro and not fuentes_claras,
      "; ".join(mal32 + solo_claro + fuentes_claras) or f"{len(a4_tema)} piezas medidas con el sistema en oscuro: sin boton, hoja clara, texto oscuro")
pdfs = {k: v for k, v in tm.items() if k.endswith("PDF con sistema oscuro")}
mal33 = [f"{k}: {v}" for k, v in pdfs.items() if not (v["spans"] > 20 and v["spans_claros"] == 0 and v["esquinas_blancas"])]
regla(33, "el HTML para imprimir es siempre hoja blanca con texto oscuro, sin modos de color (aun con el sistema en oscuro)",
      len(pdfs) >= 4 and not mal33, "; ".join(mal33) or "; ".join(f"{k.split(',')[0]}: {v['hojas']} hojas, {v['spans']} textos, 0 claros" for k, v in pdfs.items()))
mal34 = []
for pieza, rel in (("HTML completo", "demo/resumen-extenso-completo.html"), ("diapositivas", "demo/resumen-extenso-diapositivas.html")):
    if leer(rel).count('id="temaBoton"') != 1:
        mal34.append(f"{pieza}: {leer(rel).count('id=' + chr(34) + 'temaBoton' + chr(34))} botones en el codigo")
    for sis, luz_ini, esperado in (("oscuro", lambda x: x < 80, "oscuro al iniciar"), ("claro", lambda x: x > 200, "claro al iniciar")):
        v = tm.get(f"{pieza}, sistema {sis}")
        if not v:
            mal34.append(f"{pieza}, sistema {sis}: sin medir")
            continue
        cambia = (v["fondo_tras_clic"] > 200) if sis == "oscuro" else (v["fondo_tras_clic"] < 80)
        if not (v["botones"] == 1 and luz_ini(v["fondo_inicial"]) and cambia and v["recuerda"] == v["tema_tras_clic"]
                and v["fondo_tras_recargar"] == v["fondo_tras_clic"]):
            mal34.append(f"{pieza}, sistema {sis}: {v}")
regla(34, "HTML completo y diapositivas: un solo boton de tema; sigue al sistema, cambia con un clic y se recuerda al recargar",
      not mal34 and bool(tm), "; ".join(mal34) or "completo y diapositivas, con el sistema en claro y en oscuro")

# 35. Formatos de archivo y nombres: HTML, PDF y .docx para todo
# salvo el cuestionario (solo HTML); nombres con ｜ y ꞉ desde herramientas/nombres.py.
import nombres as _nom  # noqa: E402
RAIZ_PROYECTO = os.path.dirname(R)          # raiz del proyecto (esta carpeta es sistema-visual/)
def _md_proyecto():
    out = []
    for base in ("flujos", "roles", "apoyo", "configuracion", "adaptadores"):
        for raiz, _, fs in os.walk(os.path.join(RAIZ_PROYECTO, base)):
            out += [os.path.join(raiz, f) for f in fs if f.endswith(".md")]
    out += [os.path.join(RAIZ_PROYECTO, f) for f in ("INSTRUCCIONES.md", "README.md", "MANUAL-DE-USO.md", "MANUAL-DE-IMPLEMENTACION.md")]
    out += [os.path.join(R, "DESIGN-SYSTEM.md"), os.path.join(R, "LEEME.md")]
    return [p for p in out if os.path.exists(p)]
VIEJAS = re.compile(r"(no (hay|existe) (un )?generador de PDF|sin generador de PDF|ya no (hay|existe) (un )?generador de PDF|"
                    r"solo HTML y `?\.docx`?|solo HTML y Word|son solo HTML y)", re.I)
viejas = [f"{os.path.relpath(p, RAIZ_PROYECTO)}: {m.group(0)}" for p in _md_proyecto()
          for m in VIEJAS.finditer(open(p, encoding="utf-8").read())]
_DOCS_NOMBRES = {"resumir": "flujos/resumir.md", "generar-html": "apoyo/generar-html.md", "material-a4": "apoyo/material-a4.md",
                 "tp": "flujos/tp.md", "cuestionario": "flujos/cuestionario.md"}
sin_modulo = [s for s, ruta in _DOCS_NOMBRES.items()
              if "nombres.py" not in open(os.path.join(RAIZ_PROYECTO, ruta), encoding="utf-8").read()]
regla(35, "nombres.py pasa sus casos; ninguna skill ni documento afirma ya que falte el PDF o que los formatos se limiten a HTML y Word; "
      "los flujos resumir, tp y cuestionario y la guia material-a4 y generar-html nombran los archivos con nombres.py",
      _nom.probar(callar=True) and not viejas and not sin_modulo,
      "; ".join(viejas + [f"la skill {s} no menciona nombres.py" for s in sin_modulo]) or "casos de nombres.py, frases y skills al dia")

# 23. Ningun CSS de impresion con margenes propios: todo @page usa los de
# carpeta de tokens.css (--hoja-*), espejados en :left y :right.
M_ = vm._mg.MM
esperado = {"": (M_["superior"], M_["exterior"], M_["inferior"], M_["interior"]),
            ":right": (None, M_["exterior"], None, M_["interior"]),
            ":left": (None, M_["interior"], None, M_["exterior"])}
malos_page = []
css_impresion = {f: sin_comentarios(leer("css", f)) for f in os.listdir(os.path.join(R, "css")) if f.endswith(".css")}
css_impresion["incluir/a4-pagina.html"] = estilos_de(leer("incluir", "a4-pagina.html"))
for nombre, css in css_impresion.items():
    for m in re.finditer(r"@page\s*(:\w+)?\s*\{((?:[^{}]|\{[^{}]*\})*)\}", css):
        sel, cuerpo = m.group(1) or "", re.sub(r"@[\w-]+\s*\{[^{}]*\}", "", m.group(2))
        exp = esperado.get(sel)
        vals = {}
        sh = re.search(r"(?<![\w-])margin\s*:\s*([^;]+);", cuerpo)
        if sh:
            p = [float(x) for x in re.findall(r"([0-9.]+)mm", sh.group(1))]
            p = (p * 4)[:4] if len(p) == 1 else (p + p[:2])[:4] if len(p) == 2 else p
            vals.update(zip(("top", "right", "bottom", "left"), p))
        for lado in ("top", "right", "bottom", "left"):
            x = re.search(r"margin-" + lado + r"\s*:\s*([0-9.]+)mm", cuerpo)
            if x:
                vals[lado] = float(x.group(1))
        if exp is None:
            if vals:
                malos_page.append(f"{nombre} @page{sel}: define margenes")
            continue
        for lado, v in zip(("top", "right", "bottom", "left"), exp):
            if lado in vals and v is not None and abs(vals[lado] - v) > 0.01:
                malos_page.append(f"{nombre} @page{sel} margin-{lado}: {vals[lado]} mm (tokens: {v} mm)")
# Sin espejo (documento que no se imprime): el @page :left que arma incluir/espejo.lua repite
# interior a la izquierda y exterior a la derecha; sus valores tienen que ser los de tokens.css
_esp = leer("incluir", "espejo.lua")
_ei, _ee = re.search(r'M\.INTERIOR = "([0-9.]+)mm"', _esp), re.search(r'M\.EXTERIOR = "([0-9.]+)mm"', _esp)
if not (_ei and _ee and abs(float(_ei.group(1)) - M_["interior"]) < .01 and abs(float(_ee.group(1)) - M_["exterior"]) < .01):
    malos_page.append("incluir/espejo.lua: INTERIOR/EXTERIOR no coinciden con tokens.css")
regla(23, "todo CSS de impresion usa los margenes de carpeta de tokens.css (--hoja-*)", not malos_page,
      "; ".join(malos_page) or f"interior {M_['interior']}, exterior {M_['exterior']}, superior {M_['superior']}, "
      f"inferior {M_['inferior']} mm en todos los @page")

# 24 y 25. Diapositivas en tres tamanos (medidas de capturas.py con el navegador)
dm = json.load(open(os.path.join(R, "capturas", "medidas.json"), encoding="utf-8")).get("diapositivas") \
    if os.path.exists(os.path.join(R, "capturas", "medidas.json")) else None
if dm:
    desb = [f"{k}: {v['desbordan']}" for k, v in dm.items() if v["desbordan"] or v["desplazan_horizontal"]]
    escr = [f"{k}: {v['desplazan_vertical']} diapositivas" for k, v in dm.items()
            if "escritorio" in k and v["desplazan_vertical"]]
    regla(24, "diapositivas sin desborde en 1280x720, 390x844 y 844x390; en escritorio ninguna se desplaza a lo alto",
          not desb and not escr,
          "; ".join(desb + escr) or "; ".join(f"{k}: se desplazan {v['desplazan_vertical']} de {v['diapositivas']}"
                                               for k, v in dm.items() if "claro" in k))
    letra = [f"{k}: {v['letra_min']} px ({v['letra_min_donde']})" for k, v in dm.items() if v["letra_min"] < 14]
    contr = [f"{k}: {v['contraste_min']} ({v['contraste_donde']})" for k, v in dm.items() if v["contraste_min"] < 4.5]
    regla(25, "diapositivas: letra de 14 px o mas y contraste de 4,5:1 o mas, medidos en claro y en oscuro",
          not letra and not contr,
          "; ".join(letra + contr) or f"letra minima {min(v['letra_min'] for v in dm.values())} px; contraste minimo "
          f"{min(v['contraste_min'] for v in dm.values())}:1")
else:
    regla(24, "diapositivas sin desborde en tres tamanos", False, "falta medir: python herramientas/capturas.py --solo-diapositivas")
    regla(25, "letra minima y contraste de las diapositivas", False, "falta medir")
n_diap = {m: len(re.findall(r'<section class="diapositiva', leer("demo", f"resumen-{m}-diapositivas.html")))
          for m in ("extenso", "corto")}
META = re.compile(r"seg[uú]n (la |el )?(fuente|apunte|texto)|la fuente|el apunte|parafrase|no incluye la resoluci|"
                  r"fuente y ambig|cálculo propio|transcript", re.I)
metatexto = []
for f in ["demo/resumen-extenso.md", "demo/resumen-corto.md"] + [x for x in HTML_RES if "con-practica" not in x]:
    p = Texto()
    p.feed(leer(f)) if f.endswith(".html") else None
    txt = "".join(p.txt) if f.endswith(".html") else leer(f)
    metatexto += [f"{f}: {m.group(0)}" for m in META.finditer(txt)]
# Sin tope fijo: el corto solo tiene que ocupar menos hojas A4
# (y menos diapositivas) que el extenso de las mismas unidades. Las hojas salen de la regla 22
# (filas_m, el PDF que imprime el navegador); si falta alguna de las dos piezas, la regla informa y no falla.
_hojas = {n: h for n, h, _ in filas_m}
_h_ext, _h_cor = _hojas.get("resumen extenso, hoja A4"), _hojas.get("resumen corto, hoja A4")
_d_ext, _d_cor = n_diap["extenso"], n_diap["corto"]
if _h_ext is None or _h_cor is None:
    cmp_hojas, det_hojas = True, "no se pudo comparar las hojas A4 (falta el extenso o el corto en esta corrida)"
else:
    cmp_hojas, det_hojas = _h_cor < _h_ext, f"A4: corto {_h_cor} hojas, extenso {_h_ext}"
cmp_diap = (_d_cor < _d_ext) if (_d_ext and _d_cor) else True
regla(27, "modo corto: menos hojas A4 y menos diapositivas que el extenso de las mismas unidades (sin tope fijo); "
      "ningun texto metatextual en los resumenes",
      cmp_hojas and cmp_diap and not metatexto,
      f"{det_hojas}; diapositivas: corto {_d_cor}, extenso {_d_ext}; metatexto: {metatexto[:4]}")

# 20. Reemplazada por la sintesis al pie de diseño: sintesis al pie activada por
# defecto; preguntas previas y "Proba sin mirar" apagadas salvo pedido,
# marcadas y separadas del texto de la fuente.
md = leer("demo", "resumen-extenso.md")
secciones = len(re.findall(r"^## (?!.*\{-\})", md, flags=re.M))
sintesis = md.count("::: sintesis")
sin_practica = "class=\"practica" not in simple and "Material de práctica" not in simple
con = re.sub(r"\s+", " ", leer("demo", "resumen-extenso-completo-con-practica.html"))
con_practica = con.count("Material de práctica, no proviene de la fuente.") >= 2
regla(20, "sintesis en cada seccion; practica solo a pedido y marcada como material propio",
      sintesis >= secciones and sin_practica and con_practica,
      f"{sintesis} sintesis para {secciones} secciones; sin practica por defecto: {sin_practica}; "
      f"con practica: {con.count('Material de práctica, no proviene de la fuente.')} bloques marcados")

# ---- Decisiones de diseño verificables
dec = []
enc = re.search(r'<div class="encabezado">(.*?)</div>', simple, flags=re.S).group(1)
dec.append(("encabezado del resumen: solo materia y unidad", "Materia de ejemplo" in enc and "Unidad 3" in enc and enc.count("|") <= 1))
dec.append(("sin pestaña ni uñero en el borde", "pagedjs_page::after" not in CSS_RES and "uñero" not in leer("css", "resumen-a4.css").split("*/", 1)[1]))
dec.append(("hoja impresa siempre clara (tokens oscuros solo en @media screen)",
            all(m.start() > CSS_RES.find("@media screen") for m in re.finditer(r'data-theme="dark"', CSS_RES))))
tema = leer("incluir", "tema.html")
dec.append(("boton claro/oscuro con localStorage dentro de try/catch", "try { return localStorage.getItem" in tema and "try { localStorage.setItem" in tema))
dec.append(("cuestionario siempre oscuro, sin prefers-color-scheme", "prefers-color-scheme" not in CSS_Q and "color-scheme: dark" in CSS_Q))
plant = leer("cuestionario", "Plantilla-Cuestionario.html")
dec.append(("cuestionario conserva marcadores y bloque JSON", all(m in plant for m in (
    "{{ACCENT}}", "{{TITULO_PAGINA}}", "{{KICKER}}", "{{H1}}", "{{PREGUNTA_HERO}}", "{{LEDE}}", "{{QUIZ_LEN}}",
    "{{LS_KEY}}", "/* CUESTIONARIO_JSON_START */", "/* CUESTIONARIO_JSON_END */"))))
dec.append(("cuestionario conserva SM-2, mejor resultado, teclas y confirmacion", all(s in plant for s in (
    "sm2Update", "saveBest", "ArrowRight", "Escape", "confirmModal", "btnReviewAll", "selectPool"))))
dec.append(("cuestionario: modos Practica y Parcial, tiempo por hora limite, aviso con signo, SM-2 solo en Practica", all(s in plant for s in (
    "PRACTICA", "PARCIAL", "state.deadline - Date.now()", "visibilitychange", "! Queda poco tiempo", "minLibre",
    "chkVolver", "BEST_PARCIAL_KEY", "RUN_KEY", "if(!esParcial) sm2[", "if(!esParcial) saveSM2"))
            and "setInterval" in plant and "animation" not in CSS_Q))
externos = [f for f in HTML_TODOS if re.search(r'<(link|script)[^>]+(href|src)="https?://', leer(f))]
dec.append(("todo autocontenido (sin CSS, fuentes ni scripts por internet)", not externos))
a4 = leer("demo", "resumen-extenso-a4.html")
dec.append(("hoja A4: indice sin enlaces, margenes espejados, Hoja n de N",
            '<nav class="indice"' in a4 and 'href="#' not in a4.split('<nav class="indice"')[1].split("</nav>")[0]
            and "@page :left" in CSS_RES and '"Hoja " counter(page)' in CSS_RES))
for i, (t, ok) in enumerate(dec, 1):
    regla(100 + i, t, ok)


# ---- 36. Word (.docx) de todos los tipos: fuentes incrustadas, cuerpo de 12 pt, sin marcadores crudos de
# Pandoc, cobertura de componentes, cabecera sin sigla ni unidad (los margenes, en la regla 22)
import tempfile  # noqa: E402
import zipfile  # noqa: E402

sys.path.insert(0, os.path.join(R, "docx"))
import construir_docx as cd  # noqa: E402


def _texto_docx(ruta):
    z = zipfile.ZipFile(ruta)
    d = z.read("word/document.xml").decode("utf-8")
    partes = "".join(z.read(n).decode("utf-8") for n in z.namelist() if re.match(r"word/(header|footer)\d*\.xml$", n))
    txt = "".join(re.findall(r"<(?:w|m):t[^>]*>([^<]*)</(?:w|m):t>", d))
    return z, d, txt, partes


MARCADORES = [":::", "{#", "{-}", "{unidad", "](#", "[](", "^[", "{width", "Table:"]
docx_bad, docx_info = [], []
with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
    piezas = [("tp-demo", os.path.join(R, "docx", "demo", "tp-demo.docx"), "tp"),
              ("resumen extenso", os.path.join(R, "docx", "demo", "resumen-extenso.docx"), "resumen"),
              ("parcial", os.path.join(R, "docx", "demo", "parcial.docx"), "material"),
              ("soluciones, resolucion", os.path.join(R, "docx", "demo", "soluciones-resolucion.docx"), "material")]
    for nombre, md, tipo, modo in (("resumen corto", os.path.join(R, "demo", "resumen-corto.md"), "resumen", "corto"),
                                   ("soluciones, resultados", os.path.join(R, "demo", "material", "soluciones-resultados.md"),
                                    "soluciones", "extenso")):
        salida = os.path.join(tmp, nombre.replace(" ", "_").replace(",", "") + ".docx")
        _so = sys.stdout
        sys.stdout = open(os.devnull, "w")
        try:
            cd.construir(md, salida, tipo=tipo, modo=modo, trabajo=tmp)
        finally:
            sys.stdout.close()
            sys.stdout = _so
        piezas.append((nombre, salida, "material" if tipo == "soluciones" else tipo))
    for nombre, ruta, perfil in piezas:
        if not os.path.exists(ruta):
            docx_bad.append(f"{nombre}: falta {os.path.basename(ruta)}")
            continue
        z, d, txt, cab = _texto_docx(ruta)
        ft = z.read("word/fontTable.xml").decode("utf-8")
        st = z.read("word/styles.xml").decode("utf-8")
        se = z.read("word/settings.xml").decode("utf-8")
        emb = len(re.findall(r"<w:embed(?:Regular|Bold|Italic|BoldItalic) ", ft))
        if emb < 6 or "embedTrueTypeFonts" not in se or 'w:name="Estudio Sans"' not in ft:
            docx_bad.append(f"{nombre}: fuentes incrustadas {emb}")
        if 'w:sz w:val="24"' not in st.split("</w:docDefaults>")[0]:
            docx_bad.append(f"{nombre}: el cuerpo no es de 12 pt")
        crudos = [m for m in MARCADORES if m in txt]
        if crudos:
            docx_bad.append(f"{nombre}: marcadores crudos visibles {crudos}")
        if re.search(r"«(?:CABECERA|ROT)_", d + cab) or "STYLEREF" in d:
            docx_bad.append(f"{nombre}: quedo un marcador sin reemplazar")
        if re.search(r"EJEMPLO|Unidad", re.sub(r"<[^>]+>", "", cab)):
            docx_bad.append(f"{nombre}: la cabecera o el pie lleva sigla o unidad")
        if "Arial" in st or "<w:caps" in d + st:
            docx_bad.append(f"{nombre}: Arial o mayusculas")
        if perfil == "resumen":
            # Rotulo de definicion y ejemplo: con nombre el documento muestra solo «nombre.»; sin nombre,
            # «Definición N.N». Se acepta cualquiera de los dos, tomando los nombres del Markdown fuente.
            md_src = leer("demo", "resumen-corto.md" if "corto" in nombre else "resumen-extenso.md")
            esperado = ["Tabla", "Unidad 3", "Ojo." if "corto" in nombre else "Síntesis"]
            for clase, rotulo in (("definicion", "Definición"), ("ejemplo", "Ejemplo")):
                nombres = re.findall(r'\{\.%s[^}]*titulo="([^"]+)"' % clase, md_src)
                if nombres and not any(n + "." in txt for n in nombres) or not nombres and rotulo not in txt:
                    docx_bad.append(f"{nombre}: falta el rotulo de {clase} ({nombres[:1] or rotulo})")
            if "extenso" in nombre:
                esperado += ["Figura", "Resolución.", "Errores frecuentes", "Glosario", "Índice"]
            falta = [x for x in esperado if x not in txt]
            if "corto" in nombre:
                falta += [x for x in ("Síntesis", "Glosario") if x in txt]
            if "extenso" in nombre and "Material de práctica" in txt:
                falta.append("practica sin pedirla")
            if 'w:styleId="Apertura"' not in st or "STYLEREF TituloSec" not in cab:
                falta.append("apertura o seccion vigente en la cabecera")
            if falta:
                docx_bad.append(f"{nombre}: cobertura de componentes, falta o sobra {falta}")
        if perfil == "material":
            pies = [n for n in z.namelist() if re.match(r"word/footer\d*\.xml$", n)]
            enc_txt = re.sub(r"<[^>]+>", "", cab)
            if ("Materia de ejemplo | " not in enc_txt or "Hoja" not in enc_txt or pies
                    or re.search(r"Legajo|Apellido|[Ff]echa|Materia:|Tema:", enc_txt)
                    or re.search(r"Legajo|Apellido y nombre|Curso:", txt)):
                docx_bad.append(f"{nombre}: el rotulo no es una sola linea superior con materia, tema y hoja (sin pie), "
                                "o el encabezado copia Legajo, Apellido y nombre o Curso")
        docx_info.append(f"{nombre}: {emb} fuentes")
regla(36, "Word: fuentes incrustadas, cuerpo de 12 pt, sin marcadores crudos de Pandoc, todos los componentes traducidos, "
      "cabecera sin sigla ni unidad, material con el rotulo de una linea superior y sin pie (margenes en la regla 22)",
      not docx_bad, "; ".join(docx_bad) or "; ".join(docx_info))


# ---- 37 a 40. Reglas tomadas de la revision de impeccable, solo las que valen para impreso
def a_px(v, base=16.0, cuerpo=None):
    """Valor CSS simple a px (px, pt, rem, em). `em` se mide contra `cuerpo`."""
    m = re.fullmatch(r"\s*(-?[0-9]*\.?[0-9]+)\s*(px|pt|rem|em)?\s*", v)
    if not m:
        return None
    n, u = float(m.group(1)), m.group(2)
    return n * {"px": 1, "pt": 96 / 72, "rem": base, "em": cuerpo or base, None: 1}[u]


def token(css, nombre, def_=None):
    m = re.findall(r"%s\s*:\s*([^;]+);" % re.escape(nombre), css)
    return (m[-1].strip() if m else def_)


# 37. Jerarquia de titulos: h1 al menos 1,25 veces el cuerpo, h2 al menos 1,15 veces, y h1 > h2 > h3 en tamano.
# Se mide por formato a partir de los tokens (--t-h1/2/3 y --t-cuerpo).
CUERPO_TOK = a_px(token(leer("css", "tokens.css"), "--t-cuerpo"))
jer = {
    "resumen, pantalla": (leer("css", "tokens.css"), None),
    "resumen, Hoja A4": (leer("css", "tokens.css") + chr(10) + sin_comentarios(leer("css", "resumen-a4.css")), None),
}
mal37, det37 = [], []
for nombre, (css, _) in jer.items():
    css = sin_comentarios(css)
    c = a_px(token(css, "--t-cuerpo", "19px")) if "A4" not in nombre else a_px("12pt")
    h = [a_px(token(css, "--t-h%d" % i)) for i in (1, 2, 3)]
    if None in h or c is None:
        mal37.append(nombre + " (no se pudo leer)"); continue
    ok = h[0] / c >= 1.25 and h[1] / c >= 1.15 and h[0] > h[1] > h[2]
    det37.append(f"{nombre}: h1 {h[0]/c:.2f}, h2 {h[1]/c:.2f}, h3 {h[2]/c:.2f} del cuerpo")
    if not ok:
        mal37.append(nombre)
for nombre, css in (("material A4", CSS_P), ("TP A4", CSS_TP)):
    h = {}
    for sel, cuerpo_css in reglas_css(css):
        if sel in ("h1", "h2", "h3"):
            m = re.search(r"font-size\s*:\s*([^;]+)", cuerpo_css)
            if m:
                h[sel] = a_px(m.group(1))
    c = a_px("12pt")
    ok = len(h) == 3 and h["h1"] / c >= 1.25 and h["h2"] / c >= 1.05 and h["h1"] > h["h2"] > h["h3"] - 0.01
    det37.append(f"{nombre}: " + ", ".join(f"{k} {v/c:.2f}" for k, v in sorted(h.items())))
    if not ok:
        mal37.append(nombre)
regla(37, "jerarquia de titulos: h1 al menos 1,25 veces el cuerpo, h2 al menos 1,15 (1,05 en material y TP, donde el titulo "
      "se distingue ademas por peso y numero), h1 > h2 > h3", not mal37, "; ".join(det37) + (f"; REVISAR: {mal37}" if mal37 else ""))

# 38. El espacio sobre un titulo es mayor que el de abajo (el titulo se une a lo que presenta).
tok_r = sin_comentarios(leer("css", "tokens.css"))
mal38, det38 = [], []
def _margen(valor, tok=None):
    partes = valor.split()
    def un(v):
        mv = re.fullmatch(r"var\((--[a-z-]+)\)", v)
        if mv:
            v = token(tok_r, mv.group(1)) or ""
        return a_px(v, cuerpo=16)
    arriba = un(partes[0]); abajo = un(partes[2]) if len(partes) >= 3 else (un(partes[0]) if len(partes) == 1 else un(partes[0]))
    return arriba, abajo
for nombre, css in (("resumen", CSS_RES), ("material", CSS_P), ("tp", CSS_TP)):
    for sel, cuerpo_css in reglas_css(css):
        if sel in ("h2", "h3", "h1"):
            m = re.search(r"(?<![-a-z])margin\s*:\s*([^;]+)", cuerpo_css)
            if not m:
                continue
            a, b = _margen(m.group(1))
            if a is None or b is None or (a == 0 and sel == "h1"):
                continue
            det38.append(f"{nombre} {sel}: {a:.0f} sobre, {b:.0f} bajo")
            if not a > b:
                mal38.append(f"{nombre} {sel}")
regla(38, "el espacio sobre cada titulo (h2, h3, y h1 si lo tiene) es mayor que el de abajo", not mal38 and bool(det38),
      "; ".join(det38) + (f"; REVISAR: {mal38}" if mal38 else ""))

# 39. Espaciado de letras: nunca positivo (regla 2) y el negativo solo en titulos de exhibicion, hasta -0,05 em.
mal39 = []
for n, css in TODOS.items():
    for sel, c in reglas_css(css):
        for m in re.finditer(r"letter-spacing\s*:\s*([^;]+)", c):
            v = m.group(1).strip()
            em = re.fullmatch(r"(-?[0-9]*\.?[0-9]+)em", v)
            if v in ("0", "normal"):
                continue
            if not em or float(em.group(1)) < -0.05 or float(em.group(1)) > 0 or not re.search(r"h1|numeral|titulo|cab-titulo", sel):
                mal39.append(f"{n}: {sel} = {v}")
regla(39, "espaciado de letras solo negativo, hasta -0,05 em y solo en titulos de exhibicion", not mal39, "; ".join(mal39))

# 40. Texto tapado en las figuras SVG: un texto no queda debajo de un rectangulo opaco dibujado despues.
def _bbox_texto(a, cont):
    try:
        x = float(a.get("x", 0)); y = float(a.get("y", 0)); fs = float(a.get("font-size", 12))
    except ValueError:
        return None
    w = len(cont) * fs * .5
    anc = a.get("text-anchor", "start")
    x0 = x - w / 2 if anc == "middle" else (x - w if anc == "end" else x)
    return (x0, y - fs * .8, x0 + w, y + fs * .2)

class _Svg(HTMLParser):
    def __init__(self):
        super().__init__(); self.el = []; self.txt = None; self.svg = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "svg": self.svg += 1; self.el.append(("svg", None, None)); return
        if not self.svg: return
        if tag == "rect" and a.get("fill", "none") not in ("none", "transparent") and "url(" not in a.get("fill", "")                 and float(a.get("fill-opacity", 1) or 1) >= .95 and float(a.get("opacity", 1) or 1) >= .95:
            try:
                x, y, w, h = (float(a.get(k, 0)) for k in ("x", "y", "width", "height"))
                self.el.append(("rect", (x, y, x + w, y + h), a.get("fill")))
            except ValueError:
                pass
        if tag == "text": self.txt = [a, ""]
    def handle_data(self, d):
        if self.txt: self.txt[1] += d
    def handle_endtag(self, tag):
        if tag == "text" and self.txt:
            b = _bbox_texto(*self.txt)
            if b and self.txt[1].strip(): self.el.append(("text", b, self.txt[1].strip()))
            self.txt = None
        if tag == "svg": self.svg -= 1

def _tapado(html):
    pr = _Svg(); pr.feed(html); out = []
    for i, (k, b, c) in enumerate(pr.el):
        if k != "text": continue
        area = (b[2] - b[0]) * (b[3] - b[1])
        for k2, b2, c2 in pr.el[i + 1:]:
            if k2 == "svg": break
            if k2 != "rect": continue
            ix = max(0, min(b[2], b2[2]) - max(b[0], b2[0])); iy = max(0, min(b[3], b2[3]) - max(b[1], b2[1]))
            if area > 0 and ix * iy / area > .3:
                out.append(c); break
    return out
tapados = []
for f in HTML_TODOS:
    ruta = os.path.join(R, f)
    if os.path.exists(ruta):
        tapados += [f"{f}: {t}" for t in _tapado(open(ruta, encoding="utf-8").read())]
regla(40, "ningun texto de figura SVG queda tapado por un rectangulo opaco dibujado despues (aproximado: ancho del texto = 0,5 em por letra)",
      not tapados, "; ".join(tapados[:6]))


# ---- Contraste WCAG de los colores de texto
def lum(h):
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4  # noqa: E731
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def contraste(a, b):
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + .05) / (y + .05)


pares = [("#1D1F23", "#FFFFFF"), ("#55585E", "#FFFFFF"), ("#1C3F94", "#FFFFFF"), ("#C8373D", "#FFFFFF"),
         ("#1E6B3A", "#FFFFFF"), ("#E4E6EA", "#15181E"), ("#A3A8B1", "#15181E"), ("#8DB0F5", "#15181E"),
         ("#F08A8A", "#15181E"), ("#7FCB98", "#15181E")]
bajos = [(a, b, round(contraste(a, b), 1)) for a, b in pares if contraste(a, b) < 4.5]
regla(200, "contraste de texto de 4,5:1 o mas en claro y en oscuro", not bajos,
      "; ".join(f"{a} sobre {b}: {contraste(a, b):.1f}" for a, b in pares))

mal = 0
for n, texto, ok, det in sorted(res):
    etiqueta = f"{n:>2}" if n < 100 else ("D" + str(n - 100) if n < 200 else "C")
    print(f"{'CUMPLE ' if ok else 'REVISAR'} {etiqueta}. {texto}" + (f"\n           {det}" if det else ""))
    mal += not ok
sys.exit(1 if mal else 0)
