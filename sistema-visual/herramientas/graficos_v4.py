"""graficos_v4.py - estilo del sistema v4 para Matplotlib (graficos de TP,
y cualquier figura que no sea el SVG a mano de un resumen HTML).

  - Letra: Alegreya Sans con cifras de caja alta (copia "Estudio Sans PDF", nombre
    historico, de fonts/graficos; Matplotlib no aplica rasgos OpenType). Formulas de mathtext en
    la misma letra, rectas.
  - Color: tinta #1D1F23 para ejes, texto y curvas; un solo realce en azul
    birome #1C3F94 para la curva o el dato principal. Nunca el ciclo de colores
    de Matplotlib, nunca rojo ni verde (en el sistema significan correccion y
    correcto).
  - Ejes: ejes_examen() da los ejes simples con flecha, tipo examen, para
    funciones; ejes_datos() da ejes convencionales con grilla tenue, para datos
    medidos (la excepcion de la skill graficos-matematicos).
  - Salida: guardar(fig, ruta) escribe PNG a 600 ppp (Word) o SVG con el
    texto como texto si la ruta termina en .svg.

Uso:
    import sys; sys.path.insert(0, "<carpeta del proyecto>/sistema-visual/herramientas")
    import graficos_v4 as g
    fig, ax = g.figura(12, 7)        # ancho y alto en cm, al tamano final
    ax.plot(x, y, color=g.AZUL)
    g.ejes_datos(ax, "m (kg)", "a (m/s²)")
    g.guardar(fig, ruta_png)
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUENTES = os.path.join(RAIZ, "fonts", "graficos")
TINTA = "#1D1F23"
LAPIZ = "#55585E"
FILETE = "#C9CCD1"
AZUL = "#1C3F94"
CM = 1 / 2.54

for _f in ("EstudioSansPDF-Regular.ttf", "EstudioSansPDF-Italic.ttf", "EstudioSansPDF-Bold.ttf",
           "EstudioSansPDF-BoldItalic.ttf"):
    font_manager.fontManager.addfont(os.path.join(FUENTES, _f))

plt.rcParams.update({
    "font.family": "Estudio Sans PDF",
    "font.size": 10,
    "mathtext.fontset": "custom",
    "mathtext.rm": "Estudio Sans PDF",
    "mathtext.it": "Estudio Sans PDF",
    "mathtext.bf": "Estudio Sans PDF:bold",
    "mathtext.default": "rm",
    "mathtext.fallback": "stixsans",
    "text.color": TINTA,
    "axes.edgecolor": TINTA,
    "axes.labelcolor": TINTA,
    "axes.linewidth": 0.8,
    "axes.prop_cycle": plt.cycler(color=[TINTA]),
    "xtick.color": TINTA,
    "ytick.color": TINTA,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "lines.linewidth": 1.4,
    "legend.frameon": False,
    "svg.fonttype": "none",
    "axes.formatter.use_locale": False,
})


def figura(ancho_cm=12, alto_cm=7):
    """Figura al tamano final de la hoja (asi la letra sale a 10 pt reales)."""
    return plt.subplots(figsize=(ancho_cm * CM, alto_cm * CM))


def coma(ax):
    """Separador decimal con coma en las marcas de los ejes."""
    from matplotlib.ticker import FuncFormatter
    f = FuncFormatter(lambda v, _: (f"{v:g}").replace(".", ",").replace("-", "−"))
    ax.xaxis.set_major_formatter(f)
    ax.yaxis.set_major_formatter(f)


def ejes_examen(ax, rotulo_x="", rotulo_y=""):
    """Ejes simples con flecha, que se cruzan en el origen (funciones)."""
    ax.spines["left"].set_position("zero")
    ax.spines["bottom"].set_position("zero")
    ax.spines["right"].set_color("none")
    ax.spines["top"].set_color("none")
    ax.plot(1, 0, ">", color=TINTA, ms=4, transform=ax.get_yaxis_transform(), clip_on=False)
    ax.plot(0, 1, "^", color=TINTA, ms=4, transform=ax.get_xaxis_transform(), clip_on=False)
    ax.grid(False)
    if rotulo_x:
        ax.annotate(rotulo_x, xy=(1, 0), xycoords=("axes fraction", "data"), xytext=(0, -14),
                    textcoords="offset points", ha="right", va="top", style="italic")
    if rotulo_y:
        ax.annotate(rotulo_y, xy=(0, 1), xycoords=("data", "axes fraction"), xytext=(6, 0),
                    textcoords="offset points", ha="left", va="top", style="italic")
    coma(ax)


def ejes_datos(ax, rotulo_x="", rotulo_y=""):
    """Ejes convencionales abiertos, grilla tenue (datos medidos o tablas)."""
    ax.spines["right"].set_color("none")
    ax.spines["top"].set_color("none")
    ax.grid(True, color=FILETE, linewidth=0.5)
    ax.set_axisbelow(True)
    if rotulo_x:
        ax.set_xlabel(rotulo_x)
    if rotulo_y:
        ax.set_ylabel(rotulo_y)
    coma(ax)


def leyenda(ax, **kw):
    """Leyenda debajo del area de trazado, centrada y sin marco: nunca sobre los datos
    ni los rotulos. Usarla en todo grafico con leyenda."""
    kw.setdefault("loc", "upper center")
    kw.setdefault("bbox_to_anchor", (0.5, -0.24))
    kw.setdefault("frameon", False)
    kw.setdefault("fontsize", 9)
    return ax.legend(**kw)


def guardar(fig, ruta, dpi=600):
    """PNG a 600 ppp (o SVG con texto como texto si la ruta es .svg)."""
    os.makedirs(os.path.dirname(os.path.abspath(ruta)), exist_ok=True)
    fig.savefig(ruta, dpi=dpi, bbox_inches="tight", pad_inches=0.03,
                transparent=ruta.lower().endswith(".svg"), facecolor="white")
    plt.close(fig)
    return ruta
