"""diagramas_v4.py - diagramas de flujo en SVG a mano para el sistema v4.

Adaptacion de las reglas de `diagram-design` (MIT, © 2025 Cathryn Lavery, github.com/cathrynlavery/diagram-design; aviso en
AVISOS-DE-TERCEROS.md) a v4:
conectores ortogonales, etiqueta con mascara a 8 px del trazo, un solo foco de color, sin sombras
ni fondo punteado. Cambios respecto del original: el SVG se dibuja a 560 unidades (el ancho de
las figuras del resumen; en la Hoja A4 la columna de figura de 120 mm lo reduce a 0,81, asi que
14 unidades = 8,5 pt y 12,5 = 7,7 pt); Alegreya Sans heredada del documento; trazos y texto con
`currentColor`; el foco usa la clase `acento` (azul birome, y se adapta al modo oscuro); etiquetas
de rama en minuscula y sin espaciado; sin leyenda salvo que se pida (la forma ya lleva el tipo).

Uso:
    import sys; sys.path.insert(0, "sistema-visual/herramientas")
    import diagramas_v4 as d
    svg = d.flujo(
        nodos={"a": d.Nodo("inicio", ["Nuevo flujo"], col=0, fila=0),
               "b": d.Nodo("paso", ["Hacerlo a mano una vez"], col=0, fila=1),
               "c": d.Nodo("decision", ["¿Se repite", "más de 3 veces?"], col=0, fila=2),
               "d": d.Nodo("fin", ["Hecho puntual"], ["queda manual"], col=1, fila=2),
               "e": d.Nodo("fin", ["Escribir una skill"], ["reutilizable"], col=0, fila=3, foco=True)},
        aristas=[("a", "b"), ("b", "c"), ("c", "d", "no"), ("c", "e", "sí", True)],
        titulo="...", descripcion="...")
    open("figura.svg", "w", encoding="utf-8").write(svg)   # o pegarlo en el .md como imagen

Otros cuatro tipos (misma base, mismos limites): `secuencia(actores, mensajes, ...)` con mensajes
(de, a, texto[, "llamada" | "retorno"[, foco]]); `er(entidades, relaciones, ...)` con `Entidad(campos=[(nombre, "PK"|"FK"|"")],
col, fila)` y relaciones (a, b, cardinalidad_a, cardinalidad_b[, verbo]); `clases(cls, relaciones, ...)` con `Clase(atributos,
metodos, col, fila, abstracta)` y relaciones (a, b, herencia|composicion|agregacion|asociacion|dirigida|dependencia[, etiqueta
[, mult_a[, mult_b]]]); `estados(sts, transiciones, ...)` con `Estado("inicial"|"estado"|"final", nombre, col, fila, foco)` y
transiciones (a, b, «evento [guarda] / accion»[, foco]). Los conectores toman la primera ruta que no cruza otra caja (recta, codo
o vertical-horizontal-vertical) y si ninguna sirve levantan ValueError. Cada funcion devuelve el SVG en una cadena.

Reglas que hace cumplir (levanta ValueError si no se cumplen): el texto entra en su forma (se mide
con Alegreya Sans), como mucho 9 nodos (mas es dos diagramas o Graphviz), un solo foco por tipo de
camino, ninguna flecha atraviesa un nodo que no es su extremo. La regla 40 de verificar_reglas.py
comprueba despues que ninguna etiqueta quede tapada.
"""
import os
from dataclasses import dataclass, field
from xml.sax.saxutils import escape

from PIL import ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_NEGRITA = os.path.join(RAIZ, "fonts", "originales", "AlegreyaSans-Bold.ttf")
_REGULAR = os.path.join(RAIZ, "fonts", "originales", "AlegreyaSans-Regular.ttf")

ANCHO = 560
T_NODO, T_SUB, T_ETIQ = 14, 12.5, 12.5
ALTO_FILA = 96          # paso vertical entre filas
ALTO_NODO = 44
ALTO_DEC = 76           # el rombo necesita mas alto para dos renglones
MARGEN = 20
BRECHA_ETIQ = 8         # separacion entre etiqueta y trazo (regla 2 de diagram-design: 6 a 10 px)


@dataclass
class Nodo:
    tipo: str                       # inicio | fin | paso | decision
    texto: list
    sub: list = field(default_factory=list)
    col: int = 0
    fila: int = 0
    foco: bool = False


def _ancho_texto(s, tam, negrita=True):
    return ImageFont.truetype(_NEGRITA if negrita else _REGULAR, 200).getlength(s) * tam / 200


def _geom(nodos):
    ncol = max(n.col for n in nodos.values()) + 1
    paso = (ANCHO - 2 * MARGEN) / ncol
    g = {}
    for k, n in nodos.items():
        w = min(paso - 36, 190)
        h = ALTO_DEC if n.tipo == "decision" else ALTO_NODO + (14 if n.sub else 0)
        cx = MARGEN + paso * (n.col + .5)
        cy = MARGEN + ALTO_DEC / 2 + n.fila * ALTO_FILA
        # texto: la forma tiene que contenerlo
        util = w * (.56 if n.tipo == "decision" else .88 if n.tipo in ("inicio", "fin") else .94)
        for lin in n.texto:
            if _ancho_texto(lin, T_NODO) > util:
                raise ValueError(f"nodo {k}: «{lin}» no entra en la forma ({_ancho_texto(lin, T_NODO):.0f} > {util:.0f})")
        for lin in n.sub:
            if _ancho_texto(lin, T_SUB, False) > util:
                raise ValueError(f"nodo {k}: «{lin}» no entra en la forma")
        g[k] = (cx, cy, w, h)
    return g


def _borde(g, k, lado):
    cx, cy, w, h = g[k]
    return {"s": (cx, cy + h / 2), "n": (cx, cy - h / 2), "e": (cx + w / 2, cy), "w": (cx - w / 2, cy)}[lado]


def _camino(g, nodos, a, b):
    """Puntos del conector: recto si comparten columna o fila; con un codo redondeado si no."""
    na, nb = nodos[a], nodos[b]
    if na.col == nb.col:
        p, q = (_borde(g, a, "s"), _borde(g, b, "n")) if nb.fila > na.fila else (_borde(g, a, "n"), _borde(g, b, "s"))
        return [p, q]
    if na.fila == nb.fila:
        p, q = (_borde(g, a, "e"), _borde(g, b, "w")) if nb.col > na.col else (_borde(g, a, "w"), _borde(g, b, "e"))
        return [p, q]
    lado = "e" if nb.col > na.col else "w"
    p = _borde(g, a, lado)
    q = _borde(g, b, "n" if nb.fila > na.fila else "s")
    return [p, (q[0], p[1]), q]


def _atraviesa(g, nodos, pts, a, b):
    """True si algun tramo pasa por dentro de un nodo que no es extremo de la flecha."""
    for k, (cx, cy, w, h) in g.items():
        if k in (a, b):
            continue
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            if min(x1, x2) < cx + w / 2 and max(x1, x2) > cx - w / 2 and min(y1, y2) < cy + h / 2 and max(y1, y2) > cy - h / 2:
                return True
    return False


def flujo(nodos, aristas, titulo, descripcion):
    if len(nodos) > 9:
        raise ValueError("mas de 9 nodos: dividir en dos diagramas o usar Graphviz")
    g = _geom(nodos)
    filas = max(n.fila for n in nodos.values()) + 1
    alto = round(MARGEN * 2 + ALTO_DEC + (filas - 1) * ALTO_FILA)
    focos = [a for a in aristas if len(a) > 3 and a[3]]
    marc = ('<defs><marker id="fl-a" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">'
            '<polygon points="0 0,8 3,0 6" fill="currentColor"/></marker></defs>')
    flechas, etiquetas, formas = [], [], []
    for ar in aristas:
        a, b = ar[0], ar[1]
        et = ar[2] if len(ar) > 2 else ""
        foco = len(ar) > 3 and ar[3]
        pts = _camino(g, nodos, a, b)
        if _atraviesa(g, nodos, pts, a, b):
            raise ValueError(f"la flecha {a}->{b} atraviesa otro nodo: reordenar columnas o filas")
        clase = ' class="acento"' if foco else ""
        sw = 1.5 if foco else 1.2
        if len(pts) == 2:
            d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f} L{pts[1][0]:.1f} {pts[1][1]:.1f}"
        else:
            (x1, y1), (x2, y2), (x3, y3) = pts
            r = 8
            sx = 1 if x2 > x1 else -1
            sy = 1 if y3 > y2 else -1
            d = (f"M{x1:.1f} {y1:.1f} L{x2 - sx * r:.1f} {y2:.1f} Q{x2:.1f} {y2:.1f} {x2:.1f} {y2 + sy * r:.1f} "
                 f"L{x3:.1f} {y3:.1f}")
        col = "var(--azul,#1C3F94)" if foco else "currentColor"
        flechas.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linejoin="round" '
                       f'marker-end="url(#fl-a{"c" if foco else ""})"/>')
        if et:
            (x1, y1), (x2, y2) = pts[0], pts[1]
            w = _ancho_texto(et, T_ETIQ) + 8
            if abs(y1 - y2) < .1:       # tramo horizontal: etiqueta encima del trazo, centrada
                cx, base = (x1 + x2) / 2, y1 - BRECHA_ETIQ
                mx, my = cx - w / 2, base - 11
            else:                         # tramo vertical: etiqueta a la derecha del trazo
                mx, base = x1 + BRECHA_ETIQ, (y1 + y2) / 2 + 4
                my = base - 11
            etiquetas.append(f'<rect x="{mx:.1f}" y="{my:.1f}" width="{w:.1f}" height="14" fill="var(--papel,#fff)"/>'
                             f'<text x="{mx + w / 2:.1f}" y="{base:.1f}" text-anchor="middle" font-size="{T_ETIQ}" '
                             f'{"" if not foco else 'font-weight="700" '}style="fill:{col}">{escape(et)}</text>')
    for k, n in nodos.items():
        cx, cy, w, h = g[k]
        col = ' class="acento"' if n.foco else ""
        trazo = "var(--azul,#1C3F94)" if n.foco else "currentColor"
        sw = 1.5 if n.foco else 1
        if n.tipo in ("inicio", "fin"):
            f = (f'<rect x="{cx - w / 2:.1f}" y="{cy - h / 2:.1f}" width="{w:.1f}" height="{h}" rx="{h / 2}" '
                 f'fill="var(--papel,#fff)" stroke="{trazo}" stroke-width="{sw}"{"" if n.foco else " opacity=\".75\""}/>')
        elif n.tipo == "paso":
            f = (f'<rect x="{cx - w / 2:.1f}" y="{cy - h / 2:.1f}" width="{w:.1f}" height="{h}" '
                 f'fill="var(--papel,#fff)" stroke="{trazo}" stroke-width="{sw}"/>')
        elif n.tipo == "decision":
            f = (f'<polygon points="{cx:.1f},{cy - h / 2:.1f} {cx + w / 2:.1f},{cy:.1f} {cx:.1f},{cy + h / 2:.1f} '
                 f'{cx - w / 2:.1f},{cy:.1f}" fill="var(--papel,#fff)" stroke="{trazo}" stroke-width="{sw}"/>')
        else:
            raise ValueError(f"tipo desconocido: {n.tipo}")
        formas.append(f)
        lineas = [(t, T_NODO, 700, "currentColor") for t in n.texto] + [(t, T_SUB, 400, "currentColor") for t in n.sub]
        total = len(n.texto) * (T_NODO + 2) + len(n.sub) * (T_SUB + 2)
        y = cy - total / 2 + T_NODO - 1
        for t, tam, peso, c in lineas:
            op = ' opacity=".8"' if tam == T_SUB else ""
            formas.append(f'<text x="{cx:.1f}" y="{y:.1f}" text-anchor="middle" font-size="{tam}" font-weight="{peso}"{op}>{escape(t)}</text>')
            y += tam + 2
    marc = marc.replace("</defs>", '<marker id="fl-ac" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">'
                        '<polygon points="0 0,8 3,0 6" fill="var(--azul,#1C3F94)"/></marker></defs>')
    flechas = [f.replace("url(#fl-ac)", "url(#fl-ac)") for f in flechas]
    return (f'<svg class="grafico" viewBox="0 0 {ANCHO} {alto}" role="img" aria-label="{escape(titulo)}: {escape(descripcion)}">'
            f'<title>{escape(titulo)}</title>{marc}'
            '<style>.grafico text{fill:currentColor;font-family:inherit}.grafico .acento{color:var(--azul,#1C3F94)}</style>'
            + "".join(flechas) + "".join(etiquetas) + "".join(formas) + "</svg>")


# ==========================================================================
# Secuencia, entidad-relacion, clases UML y estados.
# Misma base que `flujo`: 560 unidades, currentColor, conectores ortogonales.
# ==========================================================================
T_CAMPO = 13
PAPEL = "var(--papel,#fff)"
AZUL = "var(--azul,#1C3F94)"


def _marcadores():
    m = [
        '<marker id="fl-a" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="currentColor"/></marker>',
        f'<marker id="fl-ac" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="{AZUL}"/></marker>',
        f'<marker id="d-tri" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="14" refX="13" refY="7" orient="auto"><polygon points="1 1,13 7,1 13" fill="{PAPEL}" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></marker>',
        f'<marker id="d-rombo" markerUnits="userSpaceOnUse" markerWidth="20" markerHeight="12" refX="19" refY="6" orient="auto"><polygon points="1 6,10 1,19 6,10 11" fill="{PAPEL}" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></marker>',
        '<marker id="d-rombo-lleno" markerUnits="userSpaceOnUse" markerWidth="20" markerHeight="12" refX="19" refY="6" orient="auto"><polygon points="1 6,10 1,19 6,10 11" fill="currentColor" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></marker>',
        '<marker id="d-abierta" markerUnits="userSpaceOnUse" markerWidth="12" markerHeight="12" refX="11" refY="6" orient="auto"><polyline points="1 1,11 6,1 11" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></marker>',
    ]
    return "<defs>" + "".join(m) + "</defs>"


def _svg(alto, titulo, desc, cuerpo):
    return (f'<svg class="grafico" viewBox="0 0 {ANCHO} {alto}" role="img" aria-label="{escape(titulo)}: {escape(desc)}">'
            f'<title>{escape(titulo)}</title>{_marcadores()}'
            '<style>.grafico text{fill:currentColor;font-family:inherit}.grafico .acento{color:var(--azul,#1C3F94)}</style>'
            + cuerpo + "</svg>")


def _disponer(cajas, hueco_x=44, hueco_y=48):
    """cajas: {id: (ancho, alto, col, fila)} -> ({id: (cx, cy, w, h)}, alto_total). Centra la grilla."""
    ncol = max(c[2] for c in cajas.values()) + 1
    nfil = max(c[3] for c in cajas.values()) + 1
    ancho_col = [max([c[0] for c in cajas.values() if c[2] == i] or [0]) for i in range(ncol)]
    alto_fil = [max([c[1] for c in cajas.values() if c[3] == j] or [0]) for j in range(nfil)]
    total = sum(ancho_col) + hueco_x * (ncol - 1)
    if total > ANCHO - 2 * MARGEN:
        raise ValueError(f"el diagrama no entra en {ANCHO - 2 * MARGEN} unidades de ancho ({total:.0f}): menos columnas o cajas mas angostas")
    x = (ANCHO - total) / 2
    xs = []
    for w in ancho_col:
        xs.append(x + w / 2)
        x += w + hueco_x
    ys, y = [], MARGEN
    for h in alto_fil:
        ys.append(y + h / 2)
        y += h + hueco_y
    g = {k: (xs[c[2]], ys[c[3]], c[0], c[1]) for k, c in cajas.items()}
    return g, round(y - hueco_y + MARGEN)


def _ruta(g, pos, a, b):
    """pos: {id: (col, fila)}. Recto si comparten columna o fila; con un codo si no."""
    (ca, fa), (cb, fb) = pos[a], pos[b]
    if ca == cb:
        p, q = (_borde(g, a, "s"), _borde(g, b, "n")) if fb > fa else (_borde(g, a, "n"), _borde(g, b, "s"))
        return [p, q]
    if fa == fb:
        p, q = (_borde(g, a, "e"), _borde(g, b, "w")) if cb > ca else (_borde(g, a, "w"), _borde(g, b, "e"))
        return [p, q]
    p = _borde(g, a, "e" if cb > ca else "w")
    q = _borde(g, b, "n" if fb > fa else "s")
    return [p, (q[0], p[1]), q]


def _trazo(pts, r=8):
    """Poligonal con las esquinas redondeadas (radio r, menor si el tramo es corto)."""
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(1, len(pts) - 1):
        (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[i + 1]
        l1 = abs(x1 - x0) + abs(y1 - y0)
        l2 = abs(x2 - x1) + abs(y2 - y1)
        rr = min(r, l1 / 2, l2 / 2)
        ax, ay = x1 - rr * (x1 > x0) + rr * (x1 < x0), y1 - rr * (y1 > y0) + rr * (y1 < y0)
        bx, by = x1 + rr * (x2 > x1) - rr * (x2 < x1), y1 + rr * (y2 > y1) - rr * (y2 < y1)
        d += f" L{ax:.1f} {ay:.1f} Q{x1:.1f} {y1:.1f} {bx:.1f} {by:.1f}"
    return d + f" L{pts[-1][0]:.1f} {pts[-1][1]:.1f}"


def _conector(g, pos, a, b):
    """Primera ruta que no cruza otra caja: recta, codo horizontal-vertical, o vertical-horizontal-vertical."""
    (ca, fa), (cb, fb) = pos[a], pos[b]
    ops = [_ruta(g, pos, a, b)]
    if ca != cb and fa != fb:
        p = _borde(g, a, "s" if fb > fa else "n")
        q = _borde(g, b, "n" if fb > fa else "s")
        ym = (p[1] + q[1]) / 2
        ops.append([p, (p[0], ym), (q[0], ym), q])
    for pts in ops:
        if not _atraviesa(g, None, pts, a, b):
            return pts
    raise ValueError(f"{a}->{b} atraviesa otra caja: reordenar columnas o filas")


def _texto(x, y, s, tam=T_CAMPO, peso=400, ancla="start", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{ancla}" font-size="{tam}" font-weight="{peso}"{extra}>{escape(s)}</text>'


def _extremo(p, q, s):
    """Texto de multiplicidad junto al extremo p de un tramo p-q (q es el otro punto del tramo)."""
    (x, y), (x2, y2) = p, q
    if abs(x - x2) < .1:                      # tramo vertical: a la derecha del trazo
        return _texto(x + 8, y + (16 if y2 > y else -8), s, T_ETIQ)
    return _texto(x + (6 if x2 > x else -6), y - 8, s, T_ETIQ, 400, "start" if x2 > x else "end")


def _etiqueta_tramo(pts, et, foco=False):
    """Etiqueta con mascara a 8 px del primer tramo; devuelve mascara y texto."""
    (x1, y1), (x2, y2) = pts[0], pts[1]
    w = _ancho_texto(et, T_ETIQ, False) + 8
    if abs(y1 - y2) < .1:
        if abs(x2 - x1) < w + 12:
            raise ValueError(f"la etiqueta «{et}» no entra en su tramo ({w + 12:.0f} > {abs(x2 - x1):.0f})")
        mx, base = (x1 + x2) / 2 - w / 2, y1 - BRECHA_ETIQ
    else:
        mx, base = x1 + BRECHA_ETIQ, (y1 + y2) / 2 + 4
    col = AZUL if foco else "currentColor"
    return (f'<rect x="{mx:.1f}" y="{base - 11:.1f}" width="{w:.1f}" height="14" fill="{PAPEL}"/>'
            + _texto(mx + w / 2, base, et, T_ETIQ, 700 if foco else 400, "middle", f' style="fill:{col}"'))


# ---- Secuencia -------------------------------------------------------------
def secuencia(actores, mensajes, titulo, descripcion):
    """actores: lista de nombres (izquierda a derecha). mensajes: (de, a, texto[, tipo[, foco]]) en orden,
    tipo 'llamada' (flecha llena, trazo continuo) o 'retorno' (flecha abierta, trazo punteado)."""
    n = len(actores)
    if n < 2 or n > 6:
        raise ValueError("entre 2 y 6 actores")
    colw = (ANCHO - 2 * MARGEN) / n
    x = {a: MARGEN + colw * (i + .5) for i, a in enumerate(actores)}
    hw = min(colw - 14, 130)
    for a in actores:
        if _ancho_texto(a, T_NODO) > hw - 12:
            raise ValueError(f"el actor «{a}» no entra en su cabecera")
    top, hh, paso = MARGEN, 34, 46
    y0 = top + hh + 34
    fin = y0 + (len(mensajes) - 1) * paso + 30
    cuerpo = [f'<line x1="{x[a]:.1f}" y1="{top + hh}" x2="{x[a]:.1f}" y2="{fin}" stroke="currentColor" stroke-width="1" '
              'stroke-dasharray="4 4" opacity=".55"/>' for a in actores]
    etiquetas = []
    for i, m in enumerate(mensajes):
        de, a, tx = m[0], m[1], m[2]
        tipo = m[3] if len(m) > 3 else "llamada"
        foco = len(m) > 4 and m[4]
        if de == a:
            raise ValueError("mensajes a uno mismo: no soportados")
        y = y0 + i * paso
        x1, x2 = x[de], x[a]
        w = _ancho_texto(tx, T_ETIQ, False) + 8
        if w > abs(x2 - x1) - 14:
            raise ValueError(f"el texto «{tx}» no entra entre {de} y {a} ({w:.0f} > {abs(x2 - x1) - 14:.0f})")
        col = AZUL if foco else "currentColor"
        mk = "d-abierta" if tipo == "retorno" else ("fl-ac" if foco else "fl-a")
        dash = ' stroke-dasharray="5 4"' if tipo == "retorno" else ""
        tope = x2 - (5 if x2 > x1 else -5)
        cuerpo.append(f'<line x1="{x1:.1f}" y1="{y}" x2="{tope:.1f}" y2="{y}" stroke="{col}" '
                      f'stroke-width="{1.5 if foco else 1.2}"{dash} marker-end="url(#{mk})"/>')
        cx = (x1 + x2) / 2
        etiquetas.append(f'<rect x="{cx - w / 2:.1f}" y="{y - BRECHA_ETIQ - 11}" width="{w:.1f}" height="14" fill="{PAPEL}"/>'
                         + _texto(cx, y - BRECHA_ETIQ, tx, T_ETIQ, 700 if foco else 400, "middle", f' style="fill:{col}"'))
    cuerpo += etiquetas
    for a in actores:
        cuerpo.append(f'<rect x="{x[a] - hw / 2:.1f}" y="{top}" width="{hw:.1f}" height="{hh}" fill="{PAPEL}" stroke="currentColor" stroke-width="1"/>')
        cuerpo.append(_texto(x[a], top + hh / 2 + 5, a, T_NODO, 700, "middle"))
    return _svg(round(fin + MARGEN), titulo, descripcion, "".join(cuerpo))


# ---- Entidad-relacion ------------------------------------------------------
@dataclass
class Entidad:
    campos: list                    # [(nombre, "PK" | "FK" | "")]
    col: int = 0
    fila: int = 0


def er(entidades, relaciones, titulo, descripcion):
    """relaciones: (a, b, cardinalidad_en_a, cardinalidad_en_b[, verbo]); cardinalidades como «1», «N», «0..1»."""
    FH, CH = 22, 30
    cajas = {}
    for k, e in entidades.items():
        w = max(_ancho_texto(k, T_NODO) + 24,
                max(_ancho_texto(c, T_CAMPO, False) + (38 if cl else 0) for c, cl in e.campos) + 24, 90)
        cajas[k] = (w, CH + FH * len(e.campos) + 6, e.col, e.fila)
    g, alto = _disponer(cajas, hueco_x=84, hueco_y=64)
    pos = {k: (e.col, e.fila) for k, e in entidades.items()}
    flechas, textos, formas = [], [], []
    for r in relaciones:
        a, b, ca, cb = r[:4]
        pts = _conector(g, pos, a, b)
        flechas.append(f'<path d="{_trazo(pts)}" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>')
        textos.append(_extremo(pts[0], pts[1], ca))
        textos.append(_extremo(pts[-1], pts[-2], cb))
        if len(r) > 4 and r[4]:
            textos.append(_etiqueta_tramo(pts, r[4]))
    for k, e in entidades.items():
        cx, cy, w, h = g[k]
        x0, y0 = cx - w / 2, cy - h / 2
        formas.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h}" fill="{PAPEL}" stroke="currentColor" stroke-width="1"/>')
        formas.append(f'<line x1="{x0:.1f}" y1="{y0 + CH:.1f}" x2="{x0 + w:.1f}" y2="{y0 + CH:.1f}" stroke="currentColor" stroke-width="1"/>')
        formas.append(_texto(cx, y0 + CH / 2 + 5, k, T_NODO, 700, "middle"))
        for i, (c, cl) in enumerate(e.campos):
            y = y0 + CH + FH * i + FH / 2 + 7
            formas.append(_texto(x0 + 12, y, c, T_CAMPO, 700 if cl == "PK" else 400, "start",
                                 ' text-decoration="underline"' if cl == "PK" else ""))
            if cl:
                formas.append(_texto(x0 + w - 10, y, cl, 11.5, 700, "end"))
    return _svg(alto, titulo, descripcion, "".join(flechas + textos + formas))


# ---- Clases UML ------------------------------------------------------------
@dataclass
class Clase:
    atributos: list = field(default_factory=list)
    metodos: list = field(default_factory=list)
    col: int = 0
    fila: int = 0
    abstracta: bool = False


def clases(cls, relaciones, titulo, descripcion):
    """relaciones: (a, b, tipo[, etiqueta[, mult_a[, mult_b]]]).
    tipo: herencia (a hereda de b), composicion (a contiene a b, rombo lleno en a), agregacion (rombo vacio en a),
    asociacion (linea), dirigida (flecha a -> b), dependencia (punteada, flecha a -> b)."""
    FH, CH = 20, 30
    cajas = {}
    for k, c in cls.items():
        todas = c.atributos + c.metodos
        w = max(_ancho_texto(k, T_NODO) + 24, max([_ancho_texto(s, T_CAMPO, False) for s in todas] or [0]) + 24, 100)
        h = CH + FH * max(len(c.atributos), 1) + 8 + FH * max(len(c.metodos), 1) + 8
        cajas[k] = (w, h, c.col, c.fila)
    g, alto = _disponer(cajas, hueco_y=56)
    pos = {k: (c.col, c.fila) for k, c in cls.items()}
    flechas, textos, formas = [], [], []
    mk = {"herencia": "d-tri", "composicion": "d-rombo-lleno", "agregacion": "d-rombo", "dirigida": "d-abierta", "dependencia": "d-abierta"}
    for r in relaciones:
        a, b, tipo = r[:3]
        if tipo not in mk and tipo != "asociacion":
            raise ValueError(f"tipo de relacion desconocido: {tipo}")
        et = r[3] if len(r) > 3 else ""
        ma = r[4] if len(r) > 4 else ""
        mb = r[5] if len(r) > 5 else ""
        pts = _conector(g, pos, a, b)
        dib = pts[::-1] if tipo in ("composicion", "agregacion") else pts
        marca = f' marker-end="url(#{mk[tipo]})"' if tipo in mk else ""
        dash = ' stroke-dasharray="5 4"' if tipo == "dependencia" else ""
        flechas.append(f'<path d="{_trazo(dib)}" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"{dash}{marca}/>')
        if ma:
            textos.append(_extremo(pts[0], pts[1], ma))
        if mb:
            textos.append(_extremo(pts[-1], pts[-2], mb))
        if et:
            textos.append(_etiqueta_tramo(pts, et))
    for k, c in cls.items():
        cx, cy, w, h = g[k]
        x0, y0 = cx - w / 2, cy - h / 2
        formas.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{PAPEL}" stroke="currentColor" stroke-width="1"/>')
        ya = y0 + CH
        ym = ya + FH * max(len(c.atributos), 1) + 8
        for y in (ya, ym):
            formas.append(f'<line x1="{x0:.1f}" y1="{y:.1f}" x2="{x0 + w:.1f}" y2="{y:.1f}" stroke="currentColor" stroke-width="1"/>')
        formas.append(_texto(cx, y0 + CH / 2 + 5, k, T_NODO, 700, "middle", ' font-style="italic"' if c.abstracta else ""))
        for i, s in enumerate(c.atributos):
            formas.append(_texto(x0 + 10, ya + 18 + FH * i, s))
        for i, s in enumerate(c.metodos):
            formas.append(_texto(x0 + 10, ym + 18 + FH * i, s))
    return _svg(alto, titulo, descripcion, "".join(flechas + textos + formas))


# ---- Estados ---------------------------------------------------------------
@dataclass
class Estado:
    tipo: str                       # estado | inicial | final
    nombre: str = ""
    col: int = 0
    fila: int = 0
    foco: bool = False


def estados(sts, transiciones, titulo, descripcion):
    """transiciones: (a, b, «evento [guarda] / accion»[, foco]). Sin transiciones de un estado a si mismo."""
    cajas = {}
    for k, s in sts.items():
        if s.tipo == "estado":
            cajas[k] = (max(_ancho_texto(s.nombre, T_NODO) + 28, 100), 40, s.col, s.fila)
        elif s.tipo in ("inicial", "final"):
            cajas[k] = (18, 18, s.col, s.fila)
        else:
            raise ValueError(f"tipo desconocido: {s.tipo}")
    hx = max([70] + [_ancho_texto(t[2], T_ETIQ, False) + 28 for t in transiciones if len(t) > 2 and t[2]])
    g, alto = _disponer(cajas, hueco_x=hx, hueco_y=56)
    pos = {k: (s.col, s.fila) for k, s in sts.items()}
    flechas, textos, formas = [], [], []
    for t in transiciones:
        a, b = t[0], t[1]
        et = t[2] if len(t) > 2 else ""
        foco = len(t) > 3 and t[3]
        if a == b:
            raise ValueError("transicion de un estado a si mismo: no soportada")
        pts = _conector(g, pos, a, b)
        col = AZUL if foco else "currentColor"
        flechas.append(f'<path d="{_trazo(pts)}" fill="none" stroke="{col}" stroke-width="{1.5 if foco else 1.2}" stroke-linejoin="round" '
                       f'marker-end="url(#{"fl-ac" if foco else "fl-a"})"/>')
        if et:
            textos.append(_etiqueta_tramo(pts, et, foco))
    for k, s in sts.items():
        cx, cy, w, h = g[k]
        trazo = AZUL if s.foco else "currentColor"
        if s.tipo == "inicial":
            formas.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="8" fill="currentColor"/>')
        elif s.tipo == "final":
            formas.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="9" fill="{PAPEL}" stroke="currentColor" stroke-width="1.2"/>'
                          f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5" fill="currentColor"/>')
        else:
            formas.append(f'<rect x="{cx - w / 2:.1f}" y="{cy - h / 2:.1f}" width="{w:.1f}" height="{h}" rx="12" fill="{PAPEL}" '
                          f'stroke="{trazo}" stroke-width="{1.5 if s.foco else 1}"/>')
            formas.append(_texto(cx, cy + 5, s.nombre, T_NODO, 700, "middle"))
    return _svg(alto, titulo, descripcion, "".join(flechas + textos + formas))
