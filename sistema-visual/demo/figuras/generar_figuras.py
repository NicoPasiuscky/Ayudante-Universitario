"""Figuras de la demo, en vector: la grafica temperatura-tiempo de la unidad de
demostracion (datos de la tabla de resumen-extenso.md) y la figura del ejercicio 3
del parcial de demostracion (ej3-parcial.svg).

Se escribe el SVG a mano (no con Matplotlib) para que el texto quede como texto:
insertado en linea por estudio.lua, toma la letra de la pagina y sus colores
(currentColor = tinta; .acento = azul), tambien en modo oscuro.

Uso: python demo/figuras/generar_figuras.py
"""
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
PUNTOS = [("A", 0, 30), ("B", 10, 52), ("C", 20, 38), ("D", 30, 0), ("E", 40, -37), ("F", 50, -53)]

W, H = 558, 318
X0, X1 = 64, 500        # t = 0 .. 50 min
Y0, Y1 = 26, 268        # y = 60 .. -60 grados


def px(t):
    return X0 + (X1 - X0) * t / 50


def py(y):
    return Y0 + (Y1 - Y0) * (60 - y) / 120


def catmull_rom(p):
    """Curva suave que pasa por todos los puntos (Catmull-Rom a Bezier cubica)."""
    pts = [(px(t), py(y)) for _, t, y in p]
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


def svg():
    s = [f'<svg class="grafico" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Temperatura y en grados Celsius en función del tiempo t en minutos, mediciones A a F de la tabla">']
    s.append('<style>.grafico text{font-size:14px;fill:currentColor}.grafico .eje{font-size:13px}'
             '.grafico .suave{stroke:currentColor;opacity:.22}.grafico .acento{color:var(--azul,#1C3F94)}</style>')
    # grilla y ejes
    for t in range(0, 51, 10):
        s.append(f'<line class="suave" x1="{px(t):.1f}" y1="{Y0}" x2="{px(t):.1f}" y2="{Y1}" stroke-width="1"/>')
        s.append(f'<text class="eje" x="{px(t):.1f}" y="{Y1 + 20}" text-anchor="middle">{t}</text>')
    for y in range(-60, 61, 20):
        cls = "" if y == 0 else ' class="suave"'
        sw = "1.1" if y == 0 else "1"
        s.append(f'<line{cls} x1="{X0}" y1="{py(y):.1f}" x2="{X1}" y2="{py(y):.1f}" stroke="currentColor" stroke-width="{sw}"/>')
        etq = f"−{abs(y)}" if y < 0 else str(y)
        s.append(f'<text class="eje" x="{X0 - 9}" y="{py(y) + 4.5:.1f}" text-anchor="end">{etq}</text>')
    s.append(f'<line x1="{X0}" y1="{Y0 - 6}" x2="{X0}" y2="{Y1}" stroke="currentColor" stroke-width="1.3"/>')
    s.append(f'<text x="{X0 - 9}" y="{Y0 - 12}" text-anchor="end" font-style="italic">y (°C)</text>')
    s.append(f'<text x="{X1 + 22}" y="{Y1 + 20}" text-anchor="start" font-style="italic">t (min)</text>')
    # curva
    s.append(f'<path d="{catmull_rom(PUNTOS)}" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>')
    # secante A-B con sus catetos (tasa promedio como pendiente), en azul
    ax, ay, bx, by = px(0), py(30), px(10), py(52)
    s.append('<g class="acento">')
    s.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="currentColor" stroke-width="1.8"/>')
    s.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{ay:.1f}" stroke="currentColor" stroke-width="1.2" stroke-dasharray="4 3"/>')
    s.append(f'<line x1="{bx:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="currentColor" stroke-width="1.2" stroke-dasharray="4 3"/>')
    s.append(f'<text x="{(ax + bx) / 2:.1f}" y="{ay + 17:.1f}" text-anchor="middle" style="fill:currentColor">Δt</text>')
    s.append(f'<text x="{bx + 6:.1f}" y="{(ay + by) / 2 + 5:.1f}" style="fill:currentColor">Δy</text>')
    s.append('</g>')
    # puntos y rotulos
    desplaz = {"A": (10, 24, "start"), "B": (0, -12, "middle"), "C": (8, -8, "start"),
               "D": (9, -6, "start"), "E": (9, -6, "start"), "F": (0, -12, "middle")}
    for n, t, y in PUNTOS:
        dx, dy, anc = desplaz[n]
        s.append(f'<circle cx="{px(t):.1f}" cy="{py(y):.1f}" r="4.2" fill="currentColor"/>')
        s.append(f'<text x="{px(t) + dx:.1f}" y="{py(y) + dy:.1f}" text-anchor="{anc}" font-weight="700">{n}</text>')
    s.append("</svg>")
    return "\n".join(s)


def figura_ej3():
    """Figura del ejercicio 3 del parcial de demostracion: recta de volumen en
    funcion del tiempo con dos puntos marcados, P y Q. Con la letra y la tinta de
    la pagina (currentColor); sin fondos."""
    W3, H3 = 330, 220
    x0, x1, y0, y1 = 44, 310, 14, 186           # t = 0 .. 12 min, V = 0 .. 60 L

    def X(t):
        return x0 + (x1 - x0) * t / 12

    def Y(v):
        return y1 - (y1 - y0) * v / 60

    P, Q = (2.0, 14.0), (10.0, 46.0)
    s = [f'<svg class="fig-ej3" viewBox="0 0 {W3} {H3}" role="img" '
         'aria-label="Volumen V en litros en función del tiempo t en minutos: una recta que pasa por los puntos P y Q">',
         '<style>.fig-ej3 text{font-size:13px;fill:currentColor;font-family:inherit}'
         '.fig-ej3 .l{fill:none;stroke:currentColor;stroke-width:1.3;stroke-linecap:round}'
         '.fig-ej3 .f{fill:none;stroke:currentColor;stroke-width:.8;stroke-dasharray:3 3}</style>']
    # ejes con marcas
    s.append(f'<path class="l" d="M{x0},{y0 - 6} L{x0},{y1} L{x1 + 8},{y1}"/>')
    for t in range(0, 13, 2):
        s.append(f'<line class="l" style="stroke-width:.8" x1="{X(t):.1f}" y1="{y1}" x2="{X(t):.1f}" y2="{y1 + 4}"/>')
        s.append(f'<text x="{X(t):.1f}" y="{y1 + 18}" text-anchor="middle">{t}</text>')
    for v in range(0, 61, 20):
        s.append(f'<line class="l" style="stroke-width:.8" x1="{x0 - 4}" y1="{Y(v):.1f}" x2="{x0}" y2="{Y(v):.1f}"/>')
        s.append(f'<text x="{x0 - 8}" y="{Y(v) + 4.5:.1f}" text-anchor="end">{v}</text>')
    s.append(f'<text x="{x0 + 4}" y="{y0 - 2}" font-style="italic">V (L)</text>')
    s.append(f'<text x="{x1 + 6}" y="{y1 + 18}" font-style="italic">t (min)</text>')
    # recta a trazos guia y recta principal
    a = (Q[1] - P[1]) / (Q[0] - P[0])
    v0 = P[1] - a * P[0]
    s.append(f'<line class="l" style="stroke-width:1.8" x1="{X(0):.1f}" y1="{Y(v0):.1f}" x2="{X(12):.1f}" y2="{Y(v0 + a * 12):.1f}"/>')
    for (t, v), n in ((P, "P"), (Q, "Q")):
        s.append(f'<line class="f" x1="{X(t):.1f}" y1="{Y(v):.1f}" x2="{X(t):.1f}" y2="{y1}"/>')
        s.append(f'<line class="f" x1="{x0}" y1="{Y(v):.1f}" x2="{X(t):.1f}" y2="{Y(v):.1f}"/>')
        s.append(f'<circle cx="{X(t):.1f}" cy="{Y(v):.1f}" r="3.8" fill="currentColor"/>')
        s.append(f'<text x="{X(t) + 8:.1f}" y="{Y(v) + 18:.1f}" font-weight="700">{n}</text>')
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    for nombre, f in (("temperatura-tiempo.svg", svg), ("ej3-parcial.svg", figura_ej3)):
        ruta = os.path.join(AQUI, nombre)
        with open(ruta, "w", encoding="utf-8") as fh:
            fh.write(f())
        print(ruta)
