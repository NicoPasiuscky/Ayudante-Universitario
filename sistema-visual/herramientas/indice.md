---
pagetitle: "Sistema visual de estudio v4"
lang: es
materia: "Sistema visual de estudio, versión 4"
practica: true
---

# Resúmenes, cuestionarios y parciales con una sola identidad {.unnumbered}

::: margen
*Cómo se arma esta página.* Con el mismo sistema que muestra: Pandoc, el filtro `estudio.lua` y las hojas del formato «HTML completo». Se regenera con `python construir.py`.
:::

Una página de libro de cátedra: la columna de texto en el centro, una sangría a la izquierda donde cuelgan los números, los rótulos y las marcas de error, y un margen a la derecha que trabaja con notas, supuestos y epígrafes. Un solo acento, el azul de la birome; el rojo queda para la corrección. La letra es una sola, Alegreya Sans, diseñada en Buenos Aires por Huerta Tipográfica.

## Las demostraciones {-}

Todo con contenido de ejemplo, inventado para el sistema: una unidad de «Variación y tasa de cambio» de una «Materia de ejemplo», un parcial de demostración y un trabajo práctico de demostración. Los resúmenes salen en tres formatos (HTML completo, hoja A4, diapositivas) y dos modos (extenso y explicativo, corto y rápido): seis combinaciones de la misma unidad.

| Pieza | Archivo | Qué mirar |
|---|---|---|
| Resumen extenso, HTML completo | [resumen-extenso-completo.html](demo/resumen-extenso-completo.html) | Índice con enlaces, botón de modo oscuro, plegables, vista de celular |
| Resumen extenso, hoja A4 | [resumen-extenso-a4.html](demo/resumen-extenso-a4.html) | Hojas reales, doble faz, índice sin enlaces |
| Resumen extenso, diapositivas | [resumen-extenso-diapositivas.html](demo/resumen-extenso-diapositivas.html) | Teclas, deslizamiento, vista general, modo claro y oscuro; solo pantalla, no se imprimen |
| Resumen corto, HTML completo | [resumen-corto-completo.html](demo/resumen-corto-completo.html) | Definición en una línea, fórmula clave, «Ojo» y mini ejemplo |
| Resumen corto, hoja A4 | [resumen-corto-a4.html](demo/resumen-corto-a4.html) | Más corto que el extenso (en la demo, 2 hojas; sin tope fijo) |
| Resumen corto, diapositivas | [resumen-corto-diapositivas.html](demo/resumen-corto-diapositivas.html) | Unas diez diapositivas en la demo (orientativo, sin tope) |
| Resumen con práctica | [resumen-extenso-completo-con-practica.html](demo/resumen-extenso-completo-con-practica.html) | Componentes opcionales, activados con `practica: true` |
| Cuestionario | [cuestionario.html](demo/cuestionario.html) | Siempre oscuro; nota sobre 10 y repaso por tipo de error |
| Parcial digitalizado, hoja A4 | [parcial.html](demo/parcial.html) | Encabezado fiel, rótulo tipo plano, figura en vector, espacio para responder |
| Soluciones: resultados, hoja A4 | [soluciones-resultados.html](demo/soluciones-resultados.html) | Solo los resultados finales |
| Soluciones: resolución, hoja A4 | [soluciones-resolucion.html](demo/soluciones-resolucion.html) | Paso a paso, con supuestos y erratas |
| Trabajo práctico, hoja A4 | [tp.html](demo/tp.html) | Carátula con tabla de integrantes, cabeza de hoja con el trabajo, figuras y tablas numeradas; el mismo Markdown que el Word |

<div class="miniaturas">
![](miniaturas/resumen-completo.jpg){width=23%} ![](miniaturas/resumen-a4.jpg){width=23%} ![](miniaturas/diapositivas.jpg){width=23%} ![](miniaturas/cuestionario.jpg){width=23%}
</div>

## Color {-}

El color codifica un significado fijo en las tres piezas y nunca va solo: siempre lo acompaña un signo o una palabra. No hay color por materia; la materia se reconoce por la sigla y el encabezado.

| Rol | Claro | Oscuro | Contraste | Gris | Uso |
|---|---|---|---|---|---|
| Tinta | <span class="muestra" style="--m:#1D1F23"></span> `#1D1F23` | `#E4E6EA` | 16,5 y 14,2 | 14 | Texto |
| Lápiz | <span class="muestra" style="--m:#55585E"></span> `#55585E` | `#A3A8B1` | 7,1 y 7,4 | 35 | Epígrafes, rótulos colgados |
| Azul birome | <span class="muestra" style="--m:#1C3F94"></span> `#1C3F94` | `#8DB0F5` | 9,6 y 8,2 | 28 | Lo tuyo y el acento: números, referencias, lo que marcaste |
| Rojo | <span class="muestra" style="--m:#C8373D"></span> `#C8373D` | `#F08A8A` | 5,2 y 7,4 | 43 | Corrección y error, siempre con ✗ o con la palabra |
| Verde | <span class="muestra" style="--m:#1E6B3A"></span> `#1E6B3A` | `#7FCB98` | 6,5 y 9,2 | 37 | Correcto, solo en cuestionario y soluciones, con ✓ |

Contraste contra el papel blanco y contra el fondo oscuro `#15181E`. Gris: claridad al pasar a escala de grises, de 0 (negro) a 100 (blanco). El rojo y el verde tienen grises parecidos, por eso nunca se distinguen solo por color.

## Letra {-}

<p class="especimen grande">Variación y tasa de cambio</p>
<p class="especimen">Aa Bb Ññ ¿Qué? ¡Sí! áéíóú ü, Δx, α β γ π σ ω, ± × ÷ ≤ ≥ ≈ ≠ √ ∞ °, 0123456789</p>
<p class="especimen italica">La tasa promedio tiene signo; la tasa total, no.</p>

Alegreya Sans, OFL 1.1, en siete pesos y estilos, para todo el texto y los títulos, en pantalla y en papel. Cifras de caja alta siempre: en HTML con `font-variant-numeric`, en Matplotlib y Word con una copia de la fuente que ya las trae por defecto. JetBrains Mono solo para código:

```python
tasa = (y_f - y_i) / (t_f - t_i)
```

## Componentes del resumen {-}

::: {.definicion titulo="componente"}
Cada bloque se escribe en Markdown con una clase de Pandoc; el filtro `estudio.lua` le pone número, rótulo y lugar. Esta misma definición es un `::: {.definicion titulo="..."}`.
:::

::: clave
::: ecuacion
$$\bar{r} = \frac{\Delta y}{\Delta t}$$
:::
:::

La fórmula clave va en el único recuadro del sistema (`::: clave`); las demás ecuaciones se numeran a la derecha sin caja.^[Una nota al margen numerada se escribe como nota al pie de Markdown y queda pegada a su párrafo: en la hoja A4 nunca pasa sola a otra hoja.]

::: {.ejemplo titulo="plegable"}
Un ejemplo resuelto muestra el enunciado y pliega la resolución, para intentar antes de mirar.

::: resolucion
En pantalla se abre con un clic; en la hoja A4 y al imprimir, va abierta.
:::
:::

::: errores
- Los errores frecuentes llevan un aspa roja colgada en la sangría, y solo se escriben los que son reales.
:::

::: ojo
En el modo corto, el error típico va en «Ojo», una o dos líneas con la misma aspa.
:::

::: sintesis
Cada sección cierra con un resumen breve, con el rótulo colgado a la izquierda. Está activado por defecto.
:::

::: proba
1. Las preguntas previas y «Probá sin mirar» solo aparecen si se pide `practica: true`, separadas del texto del resumen y marcadas como material de práctica.
:::

## Cuestionario y parcial {-}

El cuestionario conserva toda la mecánica de la versión anterior (sorteo, orden aleatorio de opciones, navegador, borrado, teclas, confirmación, mejor resultado y repetición espaciada) con el lenguaje nuevo: número de pregunta colgado en azul, la opción elegida encerrada como con birome, la nota sobre 10 en rojo y el repaso agrupado por tipo de error, con la corrección al margen.

El parcial digitalizado respeta el encabezado del original (sin los renglones de legajo, apellido y nombre, curso ni la fecha, que son datos personales) y lleva en el margen superior una sola línea de rótulo con materia y tema del lado interior y «Hoja n de N» del exterior; los márgenes se espejan para imprimir a doble faz y el interior es más ancho para perforar. Todo el material impreso (parcial, soluciones, TP) es HTML en hoja A4; el PDF es ese mismo HTML impreso con Firefox sin interfaz, y se pregunta la salida: solo HTML, HTML más PDF o solo PDF. Las soluciones van en dos hojas aparte: resultados y resolución completa.

## Reglas y adopción {-}

El detalle de las decisiones, el uso de cada clase, el cumplimiento de las 20 reglas contra el aspecto de IA y los cambios para adoptar el sistema están en `LEEME.md`; la comprobación automática, en `herramientas/verificar_reglas.py`.
