# Sistema de diseño v4 (HTML primero)

Sistema visual v4: una sola identidad para resúmenes, cuestionarios y material impreso en HTML A4. Todo vive en `sistema-visual/`: `LEEME.md` (mecánica, reglas contra el aspecto de IA y su verificación) y `construir.py` (reproduce todo, incluidos la muestra `indice.html` y los HTML de `demo/`, que no se versionan, y corre `herramientas/verificar_reglas.py`). La evolución de cada decisión no se registra acá: lo vigente está en este archivo, en `LEEME.md` y en `INSTRUCCIONES.md`.

Hallazgo que sigue vigente: usar siempre MathML (`--math-method=mathml` o `--mathml`, según la versión de Pandoc), nunca `mathjax` (depende de un CDN; sin conexión las fórmulas quedan en blanco sin error visible).

## 1. Motor de generación: Pandoc, Markdown como fuente única
Todo resumen se escribe primero como Markdown (`… ｜ Resumen꞉ Unidad x ｜ <modo>.md`, nombrado con `herramientas/nombres.py` y guardado en la carpeta de resúmenes de la materia, o en `HTML y MD` si se separó; ver `INSTRUCCIONES.md`, «Fuentes y salidas»). Ese Markdown es la única fuente de verdad: el `.html` y el `.docx` son exportaciones de él. El filtro `incluir/estudio.lua` convierte las clases de Pandoc en los componentes del sistema.

Estructura de un resumen:
- Metadatos: `pagetitle`, `lang: es`, `materia`, `unidad` (y `sigla`, dato interno que ya no se muestra). El encabezado muestra solo materia y unidad, juntas del lado izquierdo y separadas por una barra vertical: «Materia | Unidad N».
- Encabezados: dos niveles numerados. `# Título {unidad=N}` abre la unidad (numeral grande en azul); `## Sección {#sec:id}` se numera «N.1»; `### Subtítulo` sin número. Nunca `####`. Sin raya como coma en títulos ni rótulos. `{-}` para secciones sin número (Glosario).
- Conceptos con nombre propio: `::: {.definicion titulo="..." #def:id}` (no la lista de definición de Markdown). También `.ejemplo` y `.propiedad`.

| Escribir en el Markdown | Resultado |
|---|---|
| metadatos `materia`, `unidad` (`sigla` es solo un dato interno) | Encabezado con materia y unidad, juntas y separadas por una barra vertical; la cabeza de hoja no lleva sigla. |
| metadato `indice: true` o `-M indice=true` | Índice después del encabezado; con enlaces en pantalla, lista simple en A4. |
| metadato `practica: true` | Activa los componentes de práctica (apagados por defecto). |
| metadato `sintesis: false` | Oculta las síntesis (activadas por defecto). |
| `# Título {unidad=3}` | Apertura de unidad. `{.unnumbered}` sin numeral. |
| `## Sección {#sec:id}` / `## Sección {-}` | Numerada «3.1» / sin número. |
| `### Subtítulo` | Segundo nivel, sin número. |
| `::: {.definicion titulo="..." #def:id}` | «Definición 3.1 (...).» en línea, sin caja. También `.ejemplo`, `.propiedad`. |
| `::: resolucion` dentro de un ejemplo | Plegable «Ver la resolución»; en A4, abierta. |
| `::: {.demostracion titulo="..."}` | Demostración plegable; en A4, abierta. |
| `::: clave` (con `::: ecuacion` adentro) | Recuadro de fórmula clave, el único recuadro; como mucho uno por hoja. |
| `::: {.ecuacion #ec:id}` + `$$...$$` | Número «(3.1)» a la derecha. |
| `::: sintesis` | Resumen breve al pie de cada sección, rótulo colgado «Síntesis» (modo extenso). |
| `::: errores` + lista | «Errores frecuentes» con aspa roja (modo extenso). Solo errores reales. |
| `::: ojo` | Modo corto: error típico en una o dos líneas, con aspa roja colgada y «Ojo.». |
| `---` o `::: corte` vacío | Solo diapositivas: corta la diapositiva ahí. En los otros formatos se ignora. |
| `## Glosario {-}` + `::: glosario` + lista de definición | Glosario en dos columnas. |
| `::: margen` | Nota al margen sin número, pegada al bloque siguiente. |
| `^[texto]` | Nota al margen numerada, pegada a su párrafo (no salta de hoja). |
| `![epígrafe](x.svg){#fig:id}` | «Figura 3-1.» con el epígrafe al margen; el SVG va en línea (usar `currentColor` y la clase `acento`). |
| `::: {#tbl:id}` + tabla con `Table: ...` | «Tabla 3-1.» |
| `[](#sec:id)`, `[](#fig:id)`, `[](#tbl:id)`, `[](#ec:id)`, `[](#def:id)` | Referencias cruzadas automáticas. |
| `::: previas`, `::: proba`, `::: respuestas-practica` | Solo con `practica: true`: «Antes de leer», «Probá sin mirar» y sus respuestas, marcados «Material de práctica, no proviene de la fuente». |

Otras reglas de Markdown:
- Fórmulas: LaTeX `$...$` o `$$...$$`, siempre en MathML. Nunca aproximar con símbolos Unicode.
- Tablas: sintaxis de tabla de Markdown; el navegador resuelve anchos.
- Imágenes y diagramas: en la carpeta de figuras (`Resúmenes/Figuras`), citados como `../Figuras/<archivo>` si el `.md` está en `HTML y MD` (o `Figuras/<archivo>` si está en `Resúmenes`).

## 2. Tres formatos y dos modos: preguntar cuál, y si lleva índice, antes de generar
Antes de generar, **preguntar siempre**, salvo que ya esté indicado para la materia: el **formato** (HTML completo, Hoja A4, Diapositivas HTML; Word `.docx` como cuarta opción, sin diapositivas), la **salida** si eligió Hoja A4 (solo HTML, HTML + PDF o solo PDF; en material impreso y TP la pregunta de formato es HTML, HTML + PDF, solo PDF o Word), el **modo** (extenso y explicativo, corto y rápido), si quiere índice (solo HTML completo y Hoja A4 en modo extenso) y **si se imprime o es solo digital** (imprime = márgenes espejados a doble faz; solo digital = márgenes iguales, `-M espejo=false`; solo en los formatos A4 y Word). Cualquier combinación de modo y formato es válida; se genera solo lo que se pide. Comando exacto en `apoyo/generar-html.md`; los 6 combos de la demostración se arman con `python construir.py` en `sistema-visual`.

Común a los tres formatos: letra Alegreya Sans incrustada (familia «Estudio Sans»; JetBrains Mono solo para código; Noto Sans Math de respaldo para MathML), `css/tokens.css` + `css/resumen-base.css` + filtro `incluir/estudio.lua` (parámetros `-M formato=` y `-M modo=`), botón «Modo oscuro» / «Modo claro» (sigue al sistema si no hay elección guardada, la elige la persona y `localStorage` en `try/catch` la recuerda) solo en HTML completo y diapositivas: la Hoja A4 y el material impreso en HTML A4 son siempre claros, sin botón ni tokens oscuros (`css/tokens-oscuro.css` solo lo cargan esos dos formatos), un solo archivo autocontenido sin recursos externos.

1. **HTML completo** (`css/resumen-pantalla.css` + `css/resumen-completo.css`): lectura en pantalla, sin aspecto de papel; escritorio con sangría, texto y margen; celular (probado a 390 px) en una columna. Cuerpo de 19 px en pantalla, unos 76 caracteres por línea. Índice con enlaces si se pide.
2. **Hoja A4** (`css/resumen-a4.css` + `incluir/a4-pagina.html` + `incluir/espejo.lua` + `incluir/paged-init.html`): páginas A4 reales en pantalla vía Paged.js (embebido sin conexión, nunca por CDN), **doble faz espejada** con los márgenes de carpeta si se imprime (o márgenes iguales con `-M espejo=false` si es solo digital; sección 5.1), cabeza de hoja en el margen superior con solo «Hoja n de N» del lado exterior (sin sigla ni unidad) y la sección del lado interior. Texto corrido, tablas y fórmula clave a todo el ancho útil (169 mm, unos 103 caracteres por línea); figuras, epígrafes y bloques con nota al margen conservan dos columnas (120 mm de cuerpo + 44 mm de margen). Cuerpo de 12 pt (`--hoja-cuerpo` en `tokens.css`), justificado y sin guionado, con línea vertical entre columnas de tabla (sección 4). Sin fondos de color. Índice, si se pide, como lista simple sin enlaces. Es el resumen para imprimir; su PDF sale de imprimir este HTML con navegador sin interfaz (`imprimir_a4.entregar`) y se pregunta la salida.
3. **Diapositivas HTML** (`css/resumen-diapositivas.css` + `incluir/diapositivas.html`): una `<section class="diapositiva">` por idea (portada, cada `##`, cada `###` y cada corte `---` o `::: corte`). Letra fluida (`--u`, 25,9 px en 1280x720), vista de escritorio y celular (vertical y horizontal), barra con Anterior, Siguiente, «n de N», Vista general, Pantalla completa y modo claro u oscuro, barra de progreso, teclas (flechas, espacio, Inicio, Fin, F, G), deslizamiento y toque en los bordes, `#3` para abrir una diapositiva, región `aria-live`, una sola transición de 120 ms que se apaga con `prefers-reduced-motion`. Una diapositiva larga se desplaza dentro de sí misma. Solo pantalla (compu y celular): las diapositivas no se imprimen, así que no llevan folleto, márgenes de carpeta ni CSS de impresión.

**Modos.** *Extenso y explicativo*: la estructura v4 completa de la sección 1, con conceptos parafraseados y completados con conocimiento propio verificable, algo más corto que la fuente. *Corto y rápido*: por concepto, `::: definicion` en una línea, la fórmula clave, `::: ojo` (error típico) y un mini ejemplo numérico sin resolución plegable; sin síntesis por sección, glosario, demostraciones ni índice; claramente más corto que el extenso (una a dos hojas A4 o 10 a 15 diapositivas por unidad es solo orientativo, no un tope). Ninguno lleva comentarios metatextuales (regla de fuente, `INSTRUCCIONES.md`).

El índice se pide con `-M indice=true` (lo arma el filtro), nunca con `--toc`.

## 3. Color: paleta semántica fija, sin color por materia
| Rol | Claro | Oscuro | Uso |
|---|---|---|---|
| Tinta | `#1D1F23` | `#E4E6EA` | Texto |
| Lápiz | `#55585E` | `#A3A8B1` | Texto secundario, supuestos |
| Azul birome (acento) | `#1C3F94` | `#8DB0F5` | Lo propio: números, referencias, la opción marcada |
| Rojo | `#C8373D` | `#F08A8A` | Corrección y error: aspa de errores frecuentes, nota del cuestionario, errata |
| Verde | `#1E6B3A` | `#7FCB98` | Correcto, solo en cuestionario y soluciones |

- Color siempre acompañado de signo o palabra (✓/✗, «Resultado», «Errata»): todo se tiene que entender en gris.
- **Sin color por materia y sin uñero**: la materia se reconoce por el encabezado («Materia | Unidad N»). Una sola identidad.
- El color va en números, referencias y estados; nunca en títulos, viñetas ni fondos de cabecera de tabla. Sin fondos por tipo de bloque, sin borde de color de un solo lado, sin rótulos en mayúsculas espaciadas, sin píldoras (reglas completas en `LEEME.md`).
- Diagramas y gráficos: tinta `#1D1F23`, un solo realce en azul, texto en Alegreya Sans (ver las guías de diagramas). Un diagrama que deba verse como el resto va en SVG a mano o Graphviz; Mermaid (tema violeta, sin modo oscuro) queda solo para borradores rápidos.
- Para cambiar la paleta (por ejemplo, para otra identidad visual) se editan los tokens de `css/tokens.css` y `css/tokens-oscuro.css`, y se vuelve a correr `python construir.py`: `verificar_reglas.py` comprueba contraste y semántica.

## 4. Tablas: todas las columnas pueden partirse, nunca `nowrap`
Con una tabla real, una columna con `nowrap` y oraciones largas hace reventar el ancho de la hoja. Todas las celdas llevan `overflow-wrap: break-word` y ninguna `nowrap`.

La cabecera de tabla no va en mayúscula, ni centrada, ni con fondo: filetes arriba, abajo y bajo la cabecera, más una línea vertical fina (0,5 pt) entre columnas en todo lo imprimible (Hoja A4 y Word del resumen, material impreso y TP). En pantalla (HTML completo) solo los filetes horizontales.

Formato base de todo lo imprimible (Hoja A4 y Word del resumen, parcial, modelos, soluciones y TP; el parcial digitalizado mantiene el contenido fiel al original pero con este formato): texto justificado y sin guionado; tablas con línea vertical entre columnas; en los gráficos, la leyenda debajo del área de trazado (`graficos_v4.leyenda`), nunca encima de datos ni rótulos.

## 5. `.docx`: todos los tipos de documento
Word tiene su versión del sistema v4 en `docx/` (`construir_docx.py`, tres `reference-*.docx`, filtros `docx*.lua`, guía en `apoyo/generar-docx.md` y estándar de TP en `flujos/tp.md`) y sale para **todos** los tipos, desde el mismo Markdown que el HTML: resumen extenso y corto (no diapositivas), parcial digitalizado o modelo de práctica, soluciones (resultados y resolución) y TP, con `construir_docx.py <md> --tipo resumen|parcial|soluciones|tp`. El TP también sale en HTML A4 y PDF (sección 7). Cuerpo de 12 pt en todos.
- Alegreya Sans incrustada (familia «Estudio Sans», cifras de caja alta), 12 pt justificado con sangría de primera línea; títulos en negrita de tinta con el número en azul; figuras y tablas numeradas con el número en azul; referencias cruzadas en azul.
- Fórmulas nativas de Word (OMML) en letra recta y Noto Sans Math incrustada, cocientes apilados; los operadores los dibuja Word con Cambria Math.
- Carátula desde un JSON; campos sin datos quedan como renglón para completar. Los integrantes van en una tabla de dos columnas, «Apellido y nombre» y «Legajo» (el segundo rótulo se cambia con `rotulo_id`), una fila por integrante (`integrantes` del JSON; sin lista, dos filas vacías), en Word y en HTML A4.
- Márgenes de carpeta (sección 5.1), espejados con `w:mirrorMargins` si se imprime (con `--sin-espejo`, iguales en todas las hojas); cabeza de hoja con «Hoja n de N» del lado exterior y, del interior, el trabajo (TP) o la sección vigente (resumen); el material, el rótulo tipo plano de una sola línea: «materia | tema» del lado interior, sin pie. Resúmenes y TP, sin sigla ni unidad; el material lleva materia y tema.
- `herramientas/captura_docx.py` lo exporta a PDF y PNG para revisarlo (con Word si está, con LibreOffice si no); `verificar_margenes.py` mide los márgenes.

## 5.1 Márgenes de carpeta: todo lo imprimible
Regla general (`INSTRUCCIONES.md`): A4 a doble faz espejada si se imprime, interior 20 mm, exterior 10 mm, superior 15 mm, inferior 5 mm (área útil 180 x 277 mm; pensados para perforar y encarpetar). Si el documento es solo digital: márgenes iguales en todas las hojas con esos mismos valores y «Hoja n de N» siempre a la derecha (`-M espejo=false`, `incluir/espejo.lua`; en Word `--sin-espejo`). Única fuente: `--hoja-*` en `css/tokens.css` (Python: `herramientas/margenes.py`). Valen para la hoja A4 y para el HTML completo y el índice al imprimir (`@page`), el material impreso en HTML A4 y los `.docx`; las diapositivas y el cuestionario (solo pantalla) quedan fuera. La cabeza de hoja va en la franja superior: en HTML su texto termina a unos 11 mm del borde (margen de 15 mm con 3,5 mm de relleno inferior); en Word `w:header` está a 7 mm del borde. En el material impreso comparte esa línea con el rótulo tipo plano y no hay nada al pie; nada decorativo invade los márgenes. Reglas 22 (medición de todo lo visible en los PDF que imprime el navegador de cada hoja A4 y en Word) y 23 (ningún `@page` con otros valores) de `verificar_reglas.py`.

Para usar otros márgenes: cambiar los cuatro valores `--hoja-*` en `css/tokens.css` (y la copia de `incluir/espejo.lua`), correr `python construir.py` y confirmar que la regla 23 pasa.

## 6. Cuestionarios: mismo sistema, siempre oscuro
Plantilla: `cuestionario/Plantilla-Cuestionario.html` (fuente editable `plantilla-fuente.html` y `css/cuestionario.css`; se arma con `cuestionario/construir_plantilla.py`). Mismo lenguaje que el resumen: número de pregunta colgado en azul, opciones (a) (b) con la elegida encerrada en azul, nota sobre 10 en rojo de corrección, repaso agrupado por tipo de error con la corrección al margen. **Siempre oscuro** (confort en sesiones largas): sin variante clara ni `prefers-color-scheme`. `{{ACCENT}}` se conserva por compatibilidad pero ya no cambia el color.

**Modos**: Práctica (sin límite de tiempo, con repetición espaciada) y Parcial (tiempo elegido: 30, 60, 90 o 120 minutos o un valor libre de 1 a 300; temporizador visible y sobrio, aviso «! Queda poco tiempo» con signo y palabra; corrección al final y automática al vencer; interruptor para permitir o no volver atrás). Las opciones de tiempo son botones con relleno al elegir, no solo color.

**Repetición espaciada**: SM-2 (calidad 5 si acierta, 2 si no), solo en Práctica, guardado en `localStorage` del navegador, nunca en la carpeta de la persona. El mejor resultado se guarda como porcentaje y se muestra como nota sobre 10; el del Parcial se guarda aparte.

## 7. Material impreso en HTML A4 (y su PDF)
Parciales digitalizados, modelos de práctica, soluciones y TP salen en HTML en modo Hoja A4, con el mismo mecanismo Paged.js, los mismos tokens y la misma Alegreya Sans del resumen A4: `css/material-a4.css`, filtro `incluir/material.lua` (que también arma el rótulo tipo plano), desde Markdown (`construir.py`, función `material`). El TP usa `incluir/tp.lua` y `css/tp-a4.css` (función `tp`), con el mismo Markdown y JSON de carátula que el Word. Cuerpo de 12 pt. Fórmulas en MathML de Pandoc, rectas y con cocientes apilados; figuras en SVG en línea. Márgenes de carpeta (sección 5.1); el rótulo tipo plano es una sola línea en el margen superior (materia y tema del lado interior, «Hoja n de N» del exterior, sin datos personales ni fecha) y el área de texto ocupa toda la hoja. El encabezado del parcial digitalizado es el del original sin los renglones de legajo, apellido y nombre y curso ni la fecha. Lleva el formato base de la sección 4 (justificado, sin guionado, línea vertical en tablas). Verde solo en «Resultado», rojo solo en «Errata», sin fondos de color. El formato se pregunta: HTML, HTML + PDF, solo PDF o Word (el Word sale de `docx/construir_docx.py`, sección 5); el PDF es el HTML impreso con navegador sin interfaz (`imprimir_a4.entregar`). Reglas en `apoyo/material-a4.md` y `flujos/tp.md`.

## 8. Formatos de archivo y nombres
HTML, PDF y `.docx` están disponibles para todo uso (el Word, con `--tipo` por tipo de documento); el cuestionario es solo HTML, y el HTML completo y las diapositivas de un resumen también. Todo archivo nuevo se nombra con `herramientas/nombres.py`: `[Materia] ｜ [Tipo]꞉ Unidad x`, con la barra vertical de ancho completo ｜ (U+FF5C) y los dos puntos de letra modificadora ꞉ (U+A789) porque Windows y los servicios de nube no admiten `|` ni `:`. Los resúmenes llevan al final el modo y el formato; el resto no lleva sufijo. Tema corto: `Resumen de [tema]` (con sufijo) y `Tabla de fórmulas` (sin sufijo, siempre hoja A4). Detalle en `INSTRUCCIONES.md` y `LEEME.md`.
