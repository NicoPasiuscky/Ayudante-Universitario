# Guía: gráficos matemáticos (funciones, superficies y datos)

Genera gráficos reales de funciones, superficies, curvas y datos estadísticos con Python (NumPy, SymPy, Matplotlib), para matemática, física, estadística, análisis numérico y cualquier área que trabaje con funciones o datos. **Nunca reemplazar esto con una «interpretación geométrica» en texto.** Se usa solo si la fuente no trae un gráfico usable para ese concepto (ver `roles/profesor.md`).

## Cuándo usarla
Misma regla de prioridad que los diagramas: si la fuente ya trae el gráfico y es claro, extraerlo (ver `roles/profesor.md`) en vez de generar uno nuevo. Generar solo si no hay gráfico en la fuente, o el que hay es de mala calidad.

## Herramientas
Python con NumPy, SymPy y Matplotlib (`pip install numpy sympy matplotlib`; ver `MANUAL-DE-IMPLEMENTACION.md`).

## Paso obligatorio ANTES de graficar: verificación simbólica con SymPy
Nunca graficar una función sin haber confirmado antes con SymPy: dominio real, asíntotas y discontinuidades, raíces, extremos relevantes al concepto que se está explicando. Un gráfico de una función con el dominio mal calculado (por ejemplo, graficarla donde no está definida) es peor que no poner gráfico.

```python
import sympy as sp
x = sp.symbols('x')
f = ...  # la función de la fuente, tal cual está definida ahí
dominio = sp.calculus.util.continuous_domain(f, x, sp.S.Reals)
# revisar asíntotas, raíces (sp.solve(f, x)), etc. antes de elegir el rango a graficar
```

## Estilo de ejes: simple, tipo examen
**Nunca la caja ni la grilla por defecto de Matplotlib** (el recuadro con los 4 bordes y las líneas de grilla) para gráficos que explican una función o sirven para responder un parcial: usar ejes simples con flecha, como se dibujarían a mano en un examen:

```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.spines['left'].set_position('zero')
ax.spines['bottom'].set_position('zero')
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)  # flecha eje x
ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False)  # flecha eje y
ax.grid(False)
```

Excepción: los gráficos **estadísticos de datos reales** (histogramas, diagramas de dispersión, series de tiempo, diagramas de caja) SÍ pueden llevar grilla, leyenda y ejes convencionales si eso ayuda a leer los valores. La regla de «ejes simples tipo examen» es para gráficos de funciones matemáticas puras, no para visualización de datos.

## Formato de salida: SVG por defecto
`plt.savefig("archivo.svg")`: vectorial, nítido en HTML (formato de salida por defecto). PNG a alta resolución (`dpi=300`) solo si el pedido puntual es `.docx`.

**Archivos:** el script `.py` que genera el gráfico es descartable: trabajarlo en el directorio temporal. A la carpeta de figuras de la materia solo va el `.svg` o `.png` final que el resumen referencia, nunca el `.py`.

## Color y letra (sistema visual v4)
Tinta `#1D1F23` para ejes, texto y curvas; un solo realce en azul birome `#1C3F94` para la curva o el dato principal. Nunca los colores cíclicos por defecto de Matplotlib ni un color por materia (ver `sistema-visual/DESIGN-SYSTEM.md`, sección 3). Texto en Alegreya Sans con cifras de caja alta, usando la copia de `sistema-visual/fonts/graficos` (nombre «Estudio Sans PDF»; el resumen HTML no la necesita) para Matplotlib, que no aplica rasgos OpenType:
```python
import os
from matplotlib import font_manager
import matplotlib.pyplot as plt
F = os.path.join("sistema-visual", "fonts", "graficos")   # ruta del proyecto
for f in ("EstudioSansPDF-Regular.ttf", "EstudioSansPDF-Italic.ttf", "EstudioSansPDF-Bold.ttf"):
    font_manager.fontManager.addfont(os.path.join(F, f))
plt.rcParams.update({"font.family": "Estudio Sans PDF", "mathtext.fontset": "custom",
                     "mathtext.rm": "Estudio Sans PDF", "mathtext.it": "Estudio Sans PDF",
                     "mathtext.default": "rm", "svg.fonttype": "none"})
```
Atajo con todo esto ya configurado (letra, tinta, azul, ejes tipo examen o de datos, coma decimal, PNG a 600 ppp): `sistema-visual/herramientas/graficos_v4.py` (`figura`, `ejes_examen`, `ejes_datos`, `leyenda`, `guardar`). Figuras pensadas para hoja (hoja A4 en HTML, `.docx`): 180 mm de ancho como máximo, el área útil A4 con los márgenes de carpeta (180 x 277 mm; regla general de `INSTRUCCIONES.md`); crearlas al tamaño final para que la letra salga a 10 pt. Con `svg.fonttype: none` el texto queda como texto en el SVG y toma la letra incrustada del resumen. Para gráficos simples de un resumen HTML conviene el SVG escrito desde Python con `currentColor` y la clase `acento` (toma la tinta y el modo oscuro): ejemplo real en `sistema-visual/demo/figuras/generar_figuras.py`. Para material impreso en HTML A4 (ver `apoyo/material-a4.md`) también va el SVG en línea; el PNG a 600 ppp queda para el `.docx`.

## Paso obligatorio después de graficar
Pasar por `apoyo/verificacion-visual.md`: confirmar que el rango elegido muestra la parte relevante de la función (ni tan alejado que se pierda el detalle, ni tan cerca que corte una asíntota o una rama importante).
