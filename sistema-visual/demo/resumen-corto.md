---
pagetitle: "Variación y tasa de cambio, Materia de ejemplo, resumen corto"
lang: es
materia: "Materia de ejemplo"
sigla: "EJEMPLO"
unidad: 3
---

# Variación y tasa de cambio {unidad=3}

Se describe cómo cambia una magnitud en el tiempo mirando el valor en cada instante, sin ocuparse de las causas del cambio.

## Valor y variación {#sec:valor}

::: {.definicion #def:valor titulo="valor"}
Lectura de la magnitud en un instante, en una unidad acordada.
:::

::: {.ecuacion #ec:valor}
$$y = y(t)$$
:::

---

::: {.definicion #def:variacion titulo="variación neta"}
Diferencia entre el valor final y el inicial; depende solo de los extremos.
:::

::: {.ecuacion #ec:variacion}
$$\Delta y = y_{f} - y_{i}$$
:::

::: ojo
La variación neta no es todo lo que cambió: si la muestra vuelve al valor de partida, vale cero.
:::

## Tasa de variación promedio {#sec:tasa}

::: {.definicion #def:tasa titulo="tasa de variación promedio"}
Variación neta sobre tiempo; tiene signo, en unidad sobre minuto.
:::

::: clave
::: {.ecuacion #ec:tasa}
$$\bar{r} = \frac{\Delta y}{\Delta t} = \frac{y_{f} - y_{i}}{t_{f} - t_{i}}$$
:::
:::

En la gráfica del valor en función del tiempo es la pendiente de la recta entre dos puntos.

---

::: {.ejemplo #ej:ab titulo="entre A y B"}
Una muestra está a $30\ \text{°C}$ cuando $t = 0$ y a $52\ \text{°C}$ cuando $t = 10\ \text{min}$:

$$\bar{r} = \frac{52\ \text{°C} - 30\ \text{°C}}{10\ \text{min} - 0\ \text{min}} = 2{,}2\ \frac{\text{°C}}{\text{min}}$$
:::

---

::: ojo
El signo importa: una tasa promedio negativa indica que el valor bajó en neto, no que el cambio sea lento.
:::

## Tasa de variación total {#sec:total}

::: {.definicion #def:total titulo="tasa de variación total"}
Suma de cambios absolutos sobre tiempo total; nunca es negativa.
:::

::: {.ecuacion #ec:total}
$$\bar{r}_{T} = \frac{\sum \left|\Delta y_{k}\right|}{\Delta t}$$
:::

---

::: {#tbl:comparacion}
| Magnitud                   | Signo       | Se calcula como                        | Muestra, de A a F                      |
|----------------------------|-------------|----------------------------------------|----------------------------------------|
| Tasa de variación promedio | Con signo   | variación neta sobre tiempo            | $-1{,}7\ \frac{\text{°C}}{\text{min}}$ |
| Tasa de variación total    | Siempre ≥ 0 | suma de cambios absolutos sobre tiempo | $2{,}5\ \frac{\text{°C}}{\text{min}}$  |

Table: Tasa promedio y tasa total para la misma historia.
:::

---

::: ojo
El módulo de la tasa promedio no es la tasa total: en el ejemplo dan 1,7 y 2,5 $\frac{\text{°C}}{\text{min}}$.
:::
