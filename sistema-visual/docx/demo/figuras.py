"""figuras.py - figuras del TP de demostracion, en estilo v4 (graficos_v4.py):
tinta, un solo realce azul, Alegreya Sans, PNG a 600 ppp.

  figuras/esquema.png   montaje: tanque con escala graduada
  figuras/grafico.png   nivel en funcion del tiempo, con la recta de ajuste

Uso: python demo/figuras.py
"""
import os
import sys

import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(AQUI)), "herramientas"))
import graficos_v4 as g  # noqa: E402

SAL = os.path.join(AQUI, "figuras")
os.makedirs(SAL, exist_ok=True)
LW = 0.9


def esquema():
    fig, ax = g.figura(11, 5.6)
    # tanque
    ax.add_patch(Rectangle((2.0, 0.4), 3.0, 4.0, fill=False, ec=g.TINTA, lw=LW))
    # agua (nivel actual, en azul)
    ax.add_patch(Rectangle((2.0, 0.4), 3.0, 2.4, fill=False, ec=g.AZUL, lw=1.4, hatch="////"))
    ax.plot([2.0, 5.0], [2.8, 2.8], color=g.AZUL, lw=1.6)
    ax.text(5.25, 2.8, "nivel h", color=g.AZUL, va="center", fontsize=10)
    # escala graduada
    for i in range(0, 21):
        y = 0.4 + i * 0.2
        ax.plot([1.7 if i % 5 else 1.55, 2.0], [y, y], color=g.TINTA, lw=0.6)
    ax.text(1.35, 2.4, "escala (cm)", ha="right", va="center", fontsize=9, color=g.LAPIZ)
    # canilla y chorro
    ax.plot([3.2, 3.2, 3.9], [5.3, 4.9, 4.9], color=g.TINTA, lw=2.2, solid_capstyle="butt")
    ax.add_patch(FancyArrowPatch((3.9, 4.8), (3.9, 3.4), arrowstyle="-|>", mutation_scale=9, color=g.AZUL, lw=1.0))
    ax.text(4.1, 4.15, "caudal constante", fontsize=9, color=g.LAPIZ, va="center")
    ax.set_xlim(0, 7.4)
    ax.set_ylim(0, 5.6)
    ax.set_aspect("equal")
    ax.axis("off")
    return g.guardar(fig, os.path.join(SAL, "esquema.png"))


def grafico():
    t = np.array([0, 2, 4, 6, 8, 10.0])
    h = np.array([10.2, 15.1, 19.8, 25.3, 30.1, 34.9])
    pend, orden = np.polyfit(t, h, 1)
    fig, ax = g.figura(12, 6.4)
    tt = np.linspace(-0.3, 10.3, 50)
    ax.plot(tt, pend * tt + orden, color=g.AZUL, lw=1.6, label="ajuste lineal")
    ax.plot(t, h, "o", color=g.TINTA, ms=4.5, zorder=3, label="mediciones")
    g.ejes_datos(ax, "tiempo, t (min)", "nivel, h (cm)")
    ax.set_xlim(-0.3, 10.5)
    ax.set_ylim(7, 38)
    g.leyenda(ax)
    return g.guardar(fig, os.path.join(SAL, "grafico.png"))


if __name__ == "__main__":
    for f in (esquema, grafico):
        print(os.path.relpath(f(), AQUI))
