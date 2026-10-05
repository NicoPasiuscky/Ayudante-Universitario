# Sistema visual v4 (guía de uso y mecánica)

Una sola identidad para resúmenes, cuestionarios y material impreso (parciales, soluciones, modelos y TP en HTML A4, con PDF y Word disponibles), construida sobre la dirección «Libro de cátedra». `python construir.py` regenera `indice.html` (muestra del sistema hecha con el propio sistema, que enlaza las demostraciones) y los HTML de `demo/`, que no se versionan y se pueden volver a armar en cualquier momento. Requisitos: Python 3.10 o superior, Pandoc 3.8 o superior, un navegador (Firefox, Chrome, Edge, Brave o Chromium) y las bibliotecas de `MANUAL-DE-IMPLEMENTACION.md`; `python herramientas/entorno.py` muestra qué encuentra y qué falta. El contenido de las demostraciones es inventado («Materia de ejemplo»).

Todo se reproduce desde las fuentes con un solo comando:

```
python construir.py              resúmenes, cuestionario, material A4, índice y verificación
python construir.py --pdf        además deja en el directorio temporal el PDF de cada hoja A4 (verificación; el PDF de entrega lo arma `imprimir_a4.entregar`)
python construir.py --fuentes    además regenera las fuentes incrustadas
python construir.py --capturas   además saca todas las capturas del navegador y exporta los .docx a PDF (unos 5 minutos)
```

## Contenido de la carpeta

| Ruta | Qué es |
|---|---|
| `construir.py` | Reproduce todo, paso a paso (docstring con el orden). |
| `indice.html` | Muestra del sistema, autocontenida; no se guarda: la arma `construir.py`. Fuente: `herramientas/indice.md`. |
| `css/tokens.css` | Paleta clara con semántica fija, familias, escala, geometría y ritmo. Sin tokens oscuros. |
| `css/tokens-oscuro.css` | Modo oscuro de pantalla. Solo lo cargan el HTML completo, las diapositivas y el índice. |
| `css/resumen-base.css` | Reglas comunes a los tres formatos y los dos modos de resumen. |
| `css/resumen-pantalla.css` | Compu, tableta y celular del formato HTML completo. |
| `css/resumen-completo.css`, `resumen-a4.css`, `resumen-diapositivas.css` | Uno por formato. |
| `css/cuestionario.css` | Plantilla del cuestionario (se incrusta al armarla). |
| `css/material-a4.css` | Material impreso en HTML A4: parcial digitalizado, modelos de práctica y soluciones (sobre el mecanismo de la hoja A4 del resumen). |
| `css/tp-a4.css` | Trabajo práctico en HTML A4: carátula con tabla de integrantes, títulos numerados, figuras y tablas con epígrafe, enunciado, supuesto y resultado. |
| `css/indice.css` | Solo para `indice.html`. |
| `incluir/estudio.lua` | Filtro de Pandoc (`-M formato=` completo, a4 o diapositivas; `-M modo=` extenso o corto): numeración, rótulos, notas al margen, plegables, práctica, índice, «Ojo» y armado de las diapositivas. |
| `incluir/material.lua` | Filtro de Pandoc del material A4: encabezado fiel del original, ejercicio con número colgado, incisos, datos, figura SVG en línea, espacio para responder, «Resultado.», «Supuesto.» y «Errata.»; además escribe el rótulo tipo plano de una sola línea (materia y tema) en el margen superior. |
| `incluir/tp.lua` | Filtro de Pandoc del TP en HTML A4 (equivalente de `docx/docx.lua`): carátula desde el JSON del `.docx` (`--metadata-file`), numeración de títulos, figuras y tablas, referencias cruzadas, `::: enunciado`, `::: supuesto`, `::: resultado` y `::: salto`. |
| `incluir/espejo.lua` | Módulo común de `estudio.lua` (Hoja A4), `material.lua` y `tp.lua` para el metadato `-M espejo=false` (alias `-M imprime=false`): documento que NO se imprime, con márgenes iguales en todas las hojas (izquierdo 20 mm, derecho 10 mm, «Hoja n de N» siempre a la derecha y el texto de cabeza a la izquierda). Por defecto, espejado (se imprime). Agrega al `<head>` un `<style>` que rehace `@page :left` como `:right` y marca `<html data-espejo="no">`. Sus valores de margen son los de `tokens.css` (regla 23). |
| `incluir/paged-init.html` | Paged.js embebido sin conexión (la Hoja A4, el material y el TP lo incluyen con `--include-in-header`). |
| `incluir/fuentes.html` | `@font-face` con las fuentes en base64 (generado). |
| `incluir/tema.html` | Botón de modo claro u oscuro y apertura de plegables al imprimir. Solo HTML completo y diapositivas. |
| `herramientas/probar_tema.py` | Prueba en el navegador el modo claro u oscuro y la impresión con el sistema en oscuro (reglas 32 a 34). |
| `incluir/diapositivas.html` | Barra de navegación, progreso, vista general y script de las diapositivas. |
| `incluir/a4-pagina.html` | Configuración de Paged.js y hojas sobre la mesa. La Hoja A4 y el material impreso son siempre claros: sin tokens oscuros ni botón. |
| `incluir/formulas-rectas.html` | Letra recta en MathML (el mismo de la v3). |
| `cuestionario/plantilla-fuente.html` | Fuente editable de la plantilla. |
| `cuestionario/Plantilla-Cuestionario.html` | Plantilla final, autocontenida, con los marcadores de siempre. |
| `cuestionario/construir_plantilla.py` | Incrusta fuentes y CSS en la plantilla. |
| `docx/` | Word del sistema para todos los tipos (TP, resumen, parcial, soluciones): `construir_docx.py` (Markdown a .docx con carátula, figuras a PNG, fuentes incrustadas y posproceso), `reference.docx`, `reference-resumen.docx`, `reference-material.docx`, `docx.lua`, `docx-resumen.lua`, `docx-material.lua`, `docx-comun.lua`, `demo/` (el TP de demostración; `construir.py` genera una demostración por tipo). |
| `herramientas/` | `navegador.py` (la sesión del navegador sin interfaz que usan todas las demás herramientas: motor Firefox por Marionette y motor Chromium por el protocolo de depuración, sin dependencias de Python; `python herramientas/navegador.py` lo prueba), `construir_fuentes.py`, `construir_indice.py`, `captura_espera.py` (única herramienta de captura con navegador sin interfaz: espera a Paged.js y a los clics; `--rapida` hace la captura simple de un SVG o HTML estático), `imprimir_a4.py` (HTML A4 a PDF con el navegador: verificación y entrega con `entregar(html, carpeta, base, salida, espejo=None)`, que deja el PDF o el HTML en la carpeta de salida con `/Title` igual al nombre base; `--sin-espejo` y `espejo_de(html)` comprueban que el HTML se armó con márgenes iguales), `nombres.py` (nombre de todo archivo nuevo, con ｜ y ꞉; `--probar` y `--ejemplos`), `capturas.py` (`--solo-impresion` rehace solo lo impreso), `captura_docx.py` (Word o LibreOffice a PDF y PNG), `entorno.py` (dónde están Pandoc, el navegador y LibreOffice), `graficos_v4.py` (estilo de Matplotlib), `margenes.py`, `verificar_margenes.py`, `verificar_reglas.py`, `indice.md`. |
| `demo/` | Markdown y scripts de demostración con contenido inventado (los HTML que salen de ellos los arma `construir.py` junto a ellos y no se versionan); `demo/material/` tiene los Markdown del parcial y las dos hojas de soluciones, y `calculos.py`; el TP en HTML A4 sale del mismo Markdown y JSON que el Word de `docx/demo/`. |
| `fonts/originales`, `fonts/web`, `fonts/graficos` | Descargas oficiales (licencia OFL), subconjuntos para pantalla y variante con cifras de caja alta para Matplotlib y el `.docx`. |

## Decisiones

- **Base A, con más carácter.** Página de libro de cátedra: sangría a la izquierda donde cuelgan números de sección, rótulos («Síntesis», «Práctica») y el aspa de error; columna de texto; margen a la derecha para notas, supuestos y epígrafes. La audacia está concentrada en un solo lugar, la apertura de unidad: numeral gigante en azul que cuelga en la sangría, título en negra extra (800) y un filete grueso de 3 px. Lo demás queda tranquilo.
- **Color con semántica fija, igual en las tres piezas.** Azul birome `#1C3F94` (oscuro `#8DB0F5`) = lo tuyo y el acento: números, referencias, la opción que marcaste. Rojo `#C8373D` (`#F08A8A`) = corrección y error: aspa de los errores frecuentes, nota del cuestionario, errata en soluciones. Verde `#1E6B3A` (`#7FCB98`) = correcto, solo en cuestionario y soluciones. Siempre con signo o palabra. Sin color por materia y sin uñero: la materia se reconoce por el encabezado («Materia | Unidad N»).
- **Letra: Alegreya Sans en todo**, cuerpo y títulos, pantalla y papel; JetBrains Mono solo para código. Es una sans humanista con carácter caligráfico (Huerta Tipográfica); su cero no lleva punto. Se descartaron IBM Plex Sans (más fría, «de manual») y Atkinson Hyperlegible Next (cero con punto). Como su altura de x es chica, el cuerpo es de 19 px en pantalla y 12 pt en A4.
- **Cifras.** Alegreya Sans trae por defecto cifras de estilo antiguo. En HTML se fuerzan las de caja alta con `font-variant-numeric`; Matplotlib y Word no aplican rasgos OpenType, así que `construir_fuentes.py` genera en `fonts/graficos` una copia (familia «Estudio Sans PDF», nombre histórico) cuyo mapa de caracteres ya apunta a las cifras de caja alta; el resumen y el material A4 en HTML no la necesitan.
- **Notas al margen que no saltan de hoja** (problema de la dirección A). El filtro empareja cada nota con su párrafo en un bloque de dos columnas (`.con-nota`) que en A4 no se parte: la nota siempre queda en la misma hoja. En pantallas angostas la nota pasa debajo del párrafo.
- **Formatos y modos de resumen**. Tres formatos (HTML completo, Hoja A4, Diapositivas HTML) y dos modos (extenso y explicativo, corto y rápido), cualquier combinación. `construir.py` arma los 6 combos de la unidad 3 de la materia de ejemplo (`demo/resumen-extenso.md` y `demo/resumen-corto.md`). El modo corto agrega `::: ojo` (aspa roja y «Ojo.»), no lleva síntesis por sección, glosario, demostraciones ni índice y es claramente más corto que el extenso (la demo mide 2 hojas A4 y 10 diapositivas; «una a dos hojas A4 o 10 a 15 diapositivas por unidad» es orientativo, no un tope). Ningún documento lleva comentarios metatextuales (regla 27 lo comprueba en las demostraciones).
- **Diapositivas.** El filtro corta en cada `##`, cada `###` y cada `---` o `::: corte`; la portada es el `#`. Un solo archivo sin recursos externos; letra fluida `--u` (`clamp(17px, min(2.05vw, 3.55vh), 30px)`); una diapositiva larga se desplaza dentro de sí misma. Teclas: flechas izquierda y derecha, AvPág y RePág, espacio (Mayús + espacio retrocede), Inicio, Fin, flechas arriba y abajo para desplazar, F pantalla completa, G vista general (lista de títulos), Escape la cierra. Toque en los bordes y deslizamiento en el celular, `#3` en la dirección, región `aria-live`, transición de 120 ms desactivada con `prefers-reduced-motion`, plegables como botón. Sin JavaScript queda una página común.
- **Las diapositivas no se imprimen** . Son solo pantalla, compu y celular, en claro u oscuro con botón: no tienen folleto, giro de márgenes, CSS de impresión ni regla de hoja horizontal (la regla 26 se retiró).
- **Modo oscuro (solo HTML completo y diapositivas).** Hay un único botón «Modo oscuro» / «Modo claro». Sin elección guardada sigue al sistema; la elección se guarda en `localStorage` dentro de `try/catch` y se recuerda al recargar. Los tokens oscuros viven en `css/tokens-oscuro.css`, que solo cargan esos formatos (y el índice). **La Hoja A4 y el material impreso en HTML A4 son siempre claros y no llevan botón ni tokens oscuros en ningún bloque**: antes, con el sistema en oscuro, salían oscuros en pantalla y el botón se repetía en cada hoja sin funcionar, porque Paged.js clona el contenido. El HTML para imprimir es siempre hoja blanca con texto oscuro, sin modos de color. `herramientas/probar_tema.py` lo prueba en el navegador: botón único y funcional en completo y diapositivas (con el sistema en claro y en oscuro), A4 y material claros sin botón con el sistema en oscuro, y el PDF impreso con el sistema en oscuro, siempre hoja blanca con texto oscuro (reglas 32 a 34).
- **Márgenes de carpeta en todo lo imprimible**: A4 a doble faz espejada si se imprime, interior 20 mm, exterior 10 mm, superior 15 mm, inferior 5 mm; si el documento es solo digital, márgenes iguales en todas las hojas con los mismos valores (`-M espejo=false`, `incluir/espejo.lua`; en Word `--sin-espejo`). Única fuente: `--hoja-*` en `css/tokens.css` (Python: `herramientas/margenes.py`). Los usan la hoja A4, el `@page` del HTML completo, del cuestionario y del índice (las diapositivas no se imprimen y quedan fuera), el material impreso en HTML A4 y el `.docx`. Regla 22: nada visible más cerca del borde que el margen de ese lado; regla 23: ningún `@page` con otros valores.
- **Hoja A4.** Doble faz con los márgenes de carpeta. Con 5 mm abajo no entra un pie: la cabeza de hoja, en el margen superior (su texto termina a unos 11 mm del borde: margen de 15 mm con 3,5 mm de relleno inferior; en Word `w:header` está a 7 mm), lleva solo «Hoja n de N» del lado exterior y la sección vigente del lado interior (sin sigla ni unidad; la unidad va en el encabezado, «Materia | Unidad N», junto a la materia). Caja de texto calculada: 180 mm útiles menos 11 mm de sangría = 169 mm; el texto corrido (párrafos, definiciones, ejemplos, «ojo», listas, tablas, fórmula clave, ecuaciones con el número al extremo derecho) los ocupa enteros, unos 103 caracteres por línea medidos con el cuerpo de 12 pt (`--reserva: 0` en `resumen-a4.css`). Figuras, epígrafes y bloques con nota al margen conservan las dos columnas: 120 mm de cuerpo, 5 mm de hueco y 44 mm de margen. El numeral de apertura lleva 4,6 mm de aire arriba para no asomar al margen superior. Sin fondos de color. Índice, si se pide, como lista simple sin enlaces.
- **Elementos del resumen.** Síntesis al pie de cada sección (activada por defecto; el filtro avisa si falta), numeración citable (3.1, figura 3-1, tabla 3-1, ecuación (3.3)) con referencias cruzadas automáticas, errores frecuentes solo si son reales, un único recuadro para la fórmula clave, glosario al final, ejemplos resueltos con la resolución plegada (abierta en A4 y al imprimir). Preguntas previas y «Probá sin mirar» solo con `practica: true`, separadas por filetes punteados y marcadas «Material de práctica, no proviene de la fuente».
- **Material impreso en HTML A4**. Parcial digitalizado, soluciones y modelos de práctica salen del Markdown con `material.lua` y `material-a4.css`, sobre el mismo mecanismo de la hoja A4 del resumen; el TP, con `tp.lua` y `tp-a4.css`. Parcial: encabezado copiado fiel del original salvo los renglones «Legajo», «Apellido y nombre» y «Curso» y la fecha, que se quitan . **Rótulo tipo plano de una sola línea en el margen superior**, en la línea de la cabeza de hoja: «materia | tema» del lado interior y «Hoja n de N» del exterior, sin datos personales ni fecha y sin nada al pie (el texto ocupa toda la hoja, 277 mm; se liberaron los 21 mm que reservaba el rótulo al pie). Es una excepción explícita a la cabecera sin sigla ni unidad de los resúmenes. El pie original de un parcial (logo o sigla de la institución) no se imprime. `material.lua` escribe la línea con un script que suma el `@page` al `<head>` (como `tp.lua`); `material-a4.css` escribe «Hoja n de N». Espacio en blanco sin líneas después de cada ejercicio, dentro del ejercicio para que viajen juntos. La figura del ejercicio 3 de la demostración es un SVG en línea escrito desde Python (`demo/figuras/generar_figuras.py`); las fórmulas son el MathML de Pandoc, rectas y con cocientes apilados, también en las unidades.
- **Formatos de archivo y salida**: HTML (modo hoja A4), PDF y `.docx` disponibles para todo uso; el cuestionario es solo HTML, y el HTML completo y las diapositivas de un resumen también. El PDF es el mismo HTML A4 impreso con navegador sin interfaz (`herramientas/imprimir_a4.py`), no un generador aparte. Al elegir Hoja A4 se pregunta la salida: solo HTML, HTML + PDF o solo PDF; en todo material impreso y TP la pregunta de formato es HTML, HTML + PDF, solo PDF o Word (en resumen, el formato ofrece además HTML completo y diapositivas, y Word no combina con diapositivas). `imprimir_a4.entregar(html, carpeta, base, salida)` (o `python herramientas/imprimir_a4.py --entregar x.html "<carpeta>" "<nombre base>" --salida html|html+pdf|pdf`) deja en la carpeta de salida lo pedido con el mismo nombre base y el metadato Title del PDF igual al nombre base (PyMuPDF solo pone ese metadato); con «solo PDF» el HTML se queda en el directorio temporal.
- **Nombres de archivo**: `herramientas/nombres.py` arma el nombre de todo archivo nuevo: `[Materia] ｜ [Tipo]꞉ Unidad x`, con ｜ (U+FF5C, espacio a cada lado) y ꞉ (U+A789, espacio después) en lugar de `|` y `:`, que Windows y los servicios de nube no admiten; las dos constantes y la validación de caracteres inválidos están solo ahí. Los resúmenes llevan al final el modo y el formato (`… ｜ corto ｜ hoja A4`); el `.md` fuente lleva el modo sin el formato; cuestionarios, TP, parciales y soluciones no llevan sufijo (las soluciones terminan en `Soluciones꞉ resultados` o `Soluciones꞉ resolución`). Tema corto: `[Materia] ｜ Resumen de [tema]` (con sufijo) y `[Materia] ｜ Tabla de fórmulas` (sin sufijo: largo definido, siempre hoja A4). `python herramientas/nombres.py --probar` corre los casos; la regla 35 los exige.
- **Soluciones en dos documentos separados**, para que no compartan hoja al imprimir a doble faz: `demo/soluciones-resultados` (solo resultados, en verde con la palabra «Resultado» o en tabla) y `demo/soluciones-resolucion` (paso a paso, ambos HTML que arma `construir.py`, con supuestos en lápiz y la errata del original en rojo con la palabra «Errata»). Todos los números se calculan en Python: `demo/material/calculos.py` los recalcula y falla si alguno de los Markdown no coincide.
- **Cuestionario.** El mismo lenguaje: número de pregunta colgado en azul, opciones (a) (b) y la elegida encerrada en azul como con birome, nota sobre 10 en rojo de corrección, repaso agrupado por tipo de error (incorrectas, selección incompleta o de más, sin responder, y en «Ver el intento completo» también las correctas) con la corrección al margen. Siempre oscuro. Única animación: el avance de la barra.

## Cómo se usa

### Resumen, tres formatos y dos modos

`construir.py` (función `resumen`) es la cadena de referencia. Equivale a:

```
pandoc "<Nombre>.md" --standalone --embed-resources --math-method=mathml --syntax-highlighting=pygments \
  --lua-filter=incluir/estudio.lua -M formato=<completo|a4|diapositivas> -M modo=<extenso|corto> [-M indice=true] \
  --include-in-header=incluir/fuentes.html --css=css/tokens.css \
  [solo completo y diapositivas: --css=css/tokens-oscuro.css --include-before-body=incluir/tema.html] \
  --css=css/resumen-base.css --include-after-body=incluir/formulas-rectas.html \
  completo:     --css=css/resumen-pantalla.css --css=css/resumen-completo.css
  a4:           --css=css/resumen-a4.css --include-in-header=incluir/a4-pagina.html \
                --include-in-header=incluir/paged-init.html [-M espejo=false si no se imprime]
  diapositivas: --css=css/resumen-diapositivas.css --include-after-body=incluir/diapositivas.html
```

Correr Pandoc con la carpeta actual en la del `.md` (`Resúmenes` o `Resúmenes/HTML y MD`; las figuras, en `Resúmenes/Figuras`, se resuelven contra ella como `../Figuras/<archivo>`). En Python, `resumen(md, salida, formato, modo, indice=False, extra_meta=(), espejo=True)`; `espejo=False` solo para la Hoja A4 que no se imprime. El índice (`-M indice=true`) solo va en HTML completo y A4 extenso. Ya no se usan `--toc`, `hoja-open.html`/`hoja-close.html` ni el header temporal de color de ámbito.

### Clases de Pandoc para cada componente

| Escribir en el Markdown | Resultado |
|---|---|
| metadatos `materia`, `unidad` (`sigla` es solo un dato interno) | Encabezado con materia y unidad, juntas y separadas por una barra vertical; la cabeza de hoja no lleva sigla. |
| metadato `espejo: false` o `-M espejo=false` (alias `imprime`) | Solo Hoja A4, material y TP: documento que no se imprime, márgenes iguales en todas las hojas. |
| metadato `indice: true` o `-M indice=true` | Índice después del encabezado; con enlaces en pantalla, lista simple en A4. |
| metadato `practica: true` | Activa los componentes de práctica (apagados por defecto). |
| metadato `sintesis: false` | Oculta las síntesis (activadas por defecto). |
| `# Título {unidad=3}` | Apertura de unidad: numeral grande en azul y título. `{.unnumbered}` sin numeral. |
| `## Sección {#sec:id}` / `## Sección {-}` | Numerada «3.1», número colgado en azul / sin número (Glosario). |
| `### Subtítulo` | Segundo nivel, sin número. |
| `::: {.definicion titulo="..." #def:id}` | «Definición 3.1 (...).» en línea, sin caja. También `.ejemplo`, `.propiedad`. |
| `::: resolucion` dentro de un ejemplo | Plegable «Ver la resolución»; en A4, abierta con «Resolución.». |
| `::: {.demostracion titulo="..."}` | Demostración entera plegable; en A4, abierta. |
| `::: clave` (con `::: ecuacion` adentro) | Recuadro de fórmula clave, el único recuadro; como mucho uno por hoja. |
| `::: {.ecuacion #ec:id}` + `$$...$$` | Número «(3.1)» a la derecha. |
| `::: sintesis` | Resumen breve al pie de la sección, rótulo colgado «Síntesis». |
| `::: errores` + lista | «Errores frecuentes» con aspa roja colgada (modo extenso). Solo errores reales. |
| `::: ojo` | Modo corto: error típico en una o dos líneas, con aspa roja colgada y «Ojo.». |
| `---` o `::: corte` vacío | Solo diapositivas: corta la diapositiva ahí; en los otros formatos se ignora. Un `###` también abre una diapositiva. |
| `## Glosario {-}` + `::: glosario` + lista de definición | Glosario en dos columnas. |
| `::: margen` | Nota al margen sin número, pegada al bloque siguiente. |
| `^[texto]` | Nota al margen numerada, pegada a su párrafo. |
| `![epígrafe](x.svg){#fig:id}` | «Figura 3-1.» con el epígrafe al margen; el SVG va en línea y toma letra y colores (usar `currentColor` y la clase `acento`). |
| `::: {#tbl:id}` + tabla con `Table: ...` | «Tabla 3-1.» |
| `[](#sec:id)`, `[](#fig:id)`, `[](#tbl:id)`, `[](#ec:id)`, `[](#def:id)` | «sección 3.3», «figura 3-1», «tabla 3-1», «ecuación (3.3)», «definición 3.1». |
| `::: previas`, `::: proba`, `::: respuestas-practica` | Solo con `practica: true`: «Antes de leer», «Probá sin mirar» y sus respuestas, marcados como material de práctica; sin eso se quitan y el filtro avisa en la consola. |

### Cuestionario

Igual que hoy: copiar `cuestionario/Plantilla-Cuestionario.html`, reemplazar `{{ACCENT}}`, `{{TITULO_PAGINA}}`, `{{KICKER}}`, `{{H1}}`, `{{PREGUNTA_HERO}}`, `{{LEDE}}`, `{{QUIZ_LEN}}`, `{{LS_KEY}}` y el bloque `CUESTIONARIO_JSON`. Mismo formato de banco; un cuestionario viejo se regenera con la plantilla nueva sin tocar el banco. `{{ACCENT}}` se conserva por compatibilidad pero ya no cambia el color. Se conservan sorteo, prioridad SM-2, orden aleatorio de opciones, navegador, borrado, flechas del teclado, confirmación con Escape, mejor resultado y «Ver el intento completo». Ejemplo: `demo/construir_cuestionario.py`.

**Dos modos, elegibles en el inicio**:

- **Práctica** (por defecto). Sin límite de tiempo, corrección al final, SM-2 activo exactamente como antes (calidad 5 si acierta, 2 si no; prioridad en el sorteo).
- **Parcial.** Tiempo a elección: botones de 30, 60, 90 y 120 minutos o un campo libre (entero de 1 a 300; si no es válido, el botón de comenzar queda inhabilitado con el motivo a la vista). Interruptor «Permitir volver a preguntas anteriores» (activado por defecto): apagado, solo se avanza, sin «Anterior», con el navegador inhabilitado y la flecha izquierda sin efecto. Temporizador visible todo el intento, sin animación; con poco tiempo (el 20 % del total o 5 minutos, lo menor) agrega «! Queda poco tiempo» en rojo y negrita. Corrección al final y, al vencer el tiempo, automática: lo no respondido cuenta como incorrecto y se muestra la nota sobre 10.

Descartados: «Mostrar opciones», autoevaluación seguro / dudo / adiviné y SM-2 graduado.

**Reglas que se decidieron al implementar el Parcial:** el SM-2 no se actualiza (es una simulación); el mejor resultado se guarda aparte del de Práctica; el sorteo, el orden aleatorio y `{{QUIZ_LEN}}` son los de siempre; el reloj usa hora de inicio y hora límite (sigue corriendo con la pestaña en segundo plano); el intento en curso se guarda y, tras recargar, el inicio ofrece retomarlo (si el tiempo ya venció, lo corrige con lo respondido).

**Claves de `localStorage`** (siempre en `try/catch`): `LS_KEY` (mejor de Práctica) y `LS_KEY_sm2` sin cambios; nuevas `LS_KEY_parcial` (mejor de Parcial, porcentaje) y `LS_KEY_parcial_intento` (intento en curso; se borra al terminar).

Para ver un vencimiento sin esperar, `herramientas/capturas.py` usa un Parcial de 1 minuto con `pausa_guion` de `captura_espera.py`; también sirve guardar a mano en `LS_KEY_parcial_intento` un intento con `deadline` cercano y recargar.

### Parcial, soluciones y modelos (HTML A4)

`construir.py` (función `material`) es la cadena de referencia. Equivale a:

```
pandoc "<Nombre>.md" --standalone --embed-resources --math-method=mathml --lua-filter=incluir/material.lua \
  --include-in-header=incluir/fuentes.html --css=css/tokens.css --css=css/material-a4.css \
  --include-in-header=incluir/a4-pagina.html --include-in-header=incluir/paged-init.html \
  --include-after-body=incluir/formulas-rectas.html [-M espejo=false] -o "<Nombre>.html"
```

Metadatos: `materia` y `tema` (forman la línea superior «materia | tema»). Ya no se usan `cabeza`, `sigla` ni `pie-original`. Clases:

| Markdown | Resultado |
|---|---|
| `::: {.cabecera-original titulo="..."}` | Encabezado fiel del original sin los renglones Legajo, Apellido y nombre y Curso ni la fecha; `::: consigna` para la consigna general. |
| `::: {.ejercicio n=1 espacio=46}` | Número «1)» colgado; incisos como lista `a.`, `::: datos`, figura `![](x.svg){width=76mm}` y espacio en blanco de 46 mm. No se parte entre hojas. |
| `::: resultado`, `::: supuesto`, `::: errata` | «Resultado.» en verde, «Supuesto.» en lápiz, «Errata.» en rojo. |
| `::: subtitulo`, `::: tabla-resultados` + tabla | Bajada con filete y hoja de resultados. |
| Tablas comunes | Tablas de Pandoc, por ejemplo la de resultados. |

`\dfrac` para cocientes principales; `\frac{\text{m}}{\text{s}}` para unidades. Las reglas y el flujo por tipo de documento están en `apoyo/material-a4.md`. Para ver el PDF que imprimiría el navegador: `python herramientas/imprimir_a4.py demo/parcial.html` (va al directorio temporal); para entregarlo en la carpeta de salida, `--entregar` (ver «Formatos de archivo y salida»).

Las fórmulas son MathML nativo con `formulas-rectas.html`; no hay PNG de fórmulas. Ejemplos completos: `demo/material/`.

### Trabajo práctico en HTML A4 (y PDF)

El mismo Markdown y el mismo JSON de carátula que el `.docx` (ver abajo) salen también en HTML A4: `construir.tp(md, salida, datos=json)` en `construir.py`, que equivale a Pandoc con `--metadata-file=<json> --lua-filter=incluir/tp.lua --css=css/tokens.css --css=css/tp-a4.css` más `a4-pagina.html`, `incluir/paged-init.html` y `formulas-rectas.html` (`espejo=False` si no se imprime). La carátula (campos vacíos como renglón; los integrantes, en una tabla «Apellido y nombre» y «Legajo» con una fila por integrante, cargada desde `integrantes` del JSON, y dos filas vacías si falta la lista; los datos los pasa la persona en cada TP y no se guardan en el proyecto) es la hoja 1 y no lleva cabeza de hoja; desde la hoja 2, «Hoja n de N» del lado exterior y el trabajo del lado interior, igual que en Word. Mismos márgenes de carpeta y cuerpo de 12 pt. El texto del trabajo de la cabeza de hoja lo agrega `tp.lua` con un script que suma el `@page` al `<head>` (Paged.js no toma un `<style>` suelto del cuerpo). Demostración: `demo/tp.html`. El PDF se obtiene con `imprimir_a4.entregar`.

### Word (.docx): todos los tipos

Todo lo que sale en HTML puede salir también en Word, con el mismo Markdown y el sistema visual v4: resumen extenso y corto (no diapositivas), parcial digitalizado y modelo de práctica, soluciones (resultados y resolución) y TP. Una tabla de fórmulas o una hoja puntual no son un tipo de Word. Cuerpo de 12 pt en todos.

```
python docx/construir_docx.py Resumen.md --tipo resumen --modo extenso|corto [--indice] [--practica] [--sin-espejo] -o "Resumen.docx" --chequeo
python docx/construir_docx.py Parcial.md --tipo parcial [--sin-espejo] -o "Parcial.docx"
python docx/construir_docx.py Soluciones.md --tipo soluciones [--sin-espejo] -o "Soluciones.docx"
python docx/construir_docx.py TP.md --tipo tp --datos TP.json [--sin-espejo] -o "TP.docx" --chequeo
python herramientas/captura_docx.py "X.docx" <carpeta> --pdf <carpeta>/x.pdf     (Word sin interfaz; no deja WINWORD abierto)
python herramientas/verificar_margenes.py <carpeta>/x.pdf
```

Una sola herramienta, tres perfiles de estilos (`docx/reference.docx` del TP, `reference-resumen.docx`, `reference-material.docx`) y un filtro por tipo: `docx.lua` (TP), `docx-resumen.lua` y `docx-material.lua`, con piezas comunes en `docx-comun.lua`. Los SVG del Markdown pasan a PNG de 2400 px (unos 500 ppp) con el navegador. **Notas al margen y epígrafes de figuras**: tabla invisible de dos columnas (cuerpo 72 % | nota 28 %), una sola fila que no se parte, como el par texto-nota del HTML. **Rótulo tipo plano del material**: una sola línea en la cabecera de la sección (marcador `ROT_LINEA`), «materia | tema» del lado interior y «Hoja n de N» del exterior; sin pie. **Sección vigente** en la cabeza del resumen: campo `STYLEREF`. Plegables abiertos. Guía completa, decisiones y errores de Word ya conocidos en `apoyo/generar-docx.md`.

Pandoc con el `reference-*.docx` del perfil y el filtro del tipo, más un post-proceso: letra Alegreya Sans incrustada (familia «Estudio Sans», cifras de caja alta; partes `.odttf` ofuscadas y `w:embedTrueTypeFonts`, `fsType` 0 = incrustación permitida), fórmulas nativas de Word en letra recta con Noto Sans Math incrustada y cocientes apilados, tablas con autoajuste y filas enteras, carátula desde el JSON (con la tabla de integrantes), márgenes de carpeta espejados (iguales con `--sin-espejo`, sin `w:mirrorMargins` ni `w:evenAndOddHeaders`) y cabeza de hoja par e impar (solo «Hoja n de N» y el trabajo, sin la asignatura; en el material, «Hoja n de N» y el rótulo «materia | tema»). Probado exportando con Word: el PDF usa la letra incrustada (`___WRD_EMBED_SUB`) sin tenerla instalada en Windows. Guía completa en `apoyo/generar-docx.md`; estándar de TP en `flujos/tp.md`; demostración en `docx/demo/` y `docx/capturas/`.

## Tipografías

Todas SIL Open Font License 1.1, sin nombre reservado; descargadas de `github.com/google/fonts` (rama `main`, carpetas `ofl/`). Los `OFL.txt` y `METADATA.pb` están en `fonts/originales`.

| Archivo | Familia y uso | Versión |
|---|---|---|
| `AlegreyaSans-{Regular, Italic, Medium, MediumItalic, Bold, BoldItalic, ExtraBold}.ttf` | Estudio Sans: todo el texto | 2.004 |
| `JetBrainsMono-VF.ttf` | Estudio Mono: código | 2.211 |
| `NotoSansMath-Regular.ttf` | Estudio Mate: respaldo de MathML, con tabla MATH | 3.000 |
| `NotoSansSymbols2-Regular.ttf` | Estudio Marcas: ✓ ✗ ✱ | (Google Fonts) |

**Cobertura, comprobada con fontTools sobre el mapa de caracteres.** Alegreya Sans cubre á é í ó ú ü ñ y mayúsculas, ¿ ¡ « » º ª °, griego completo (Δ α β γ π σ ω μ θ λ ρ τ φ Ω Σ), ± × ÷ ≤ ≥ ≠ ≈ ² ³ µ − √ ∞ ∑ ∫ ∂ ∆ ′ ″, y tiene versalitas y cifras de caja alta, tabulares y proporcionales. Le faltan ∇, ✓, ✗ y ✱: los dos primeros los da Estudio Mate, los otros Estudio Marcas. JetBrains Mono no tiene ∆ ni ∇ (no hacen falta en código).

**Peso.** Subconjuntos WOFF de unos 50 KB por estilo; cada resumen pesa unos 710 KB (el A4 1,7 MB con Paged.js) y el cuestionario 525 KB.

## Reglas contra el aspecto de IA

`python herramientas/verificar_reglas.py` las comprueba sobre el CSS sin comentarios, el HTML generado y las medidas que toma el navegador (`capturas/medidas.json`); sale con error si alguna falla. Todas tienen que cumplir; la corrida de `construir.py` termina con error si alguna falla.

| # | Regla | Cómo se comprobó | Resultado |
|---|---|---|---|
| 1 | Sin borde de color de un lado | Busca `border-left/right/inline-*` en los tres CSS; exceptúa el separador de celdas de las tablas impresas (`th + th, td + td`, línea vertical entre columnas) | cumple |
| 2 | Sin mayúsculas espaciadas | `uppercase` y `letter-spacing` positivo | cumple |
| 3 | Sin píldoras | Radios de 1 em o más | cumple |
| 4 | Radio solo en controles | Selectores con `border-radius` | cumple |
| 5 | Una sola sombra | Selectores con `box-shadow` | cumple |
| 6 | Un color cromático | Tonos agrupados de 30 grados, solo tokens usados | cumple |
| 7 | Sin fondos por bloque | `background` fuera de papel, mesa y controles | cumple |
| 8 | Sin punto medio ni flechas | Texto visible de los 6 HTML | cumple |
| 9 | Sin raya en títulos y rótulos | h1 a h3, epígrafes | cumple |
| 10 | Rótulos en línea | Ningún `.rotulo` dentro del recuadro | cumple |
| 11 | Numeración citable | Referencias y elementos numerados | cumple |
| 12 | Un recuadro por hoja | Cuenta `.clave` por hoja en el navegador | cumple |
| 13 | Ritmo desigual | Valores de espacio vertical | cumple |
| 14 | Letra propia | Primera familia del texto | cumple |
| 15 | Medida y cuerpo | Medido en el navegador | cumple |
| 16 | Prueba en gris | `capturas/gris-*.png`, revisadas a ojo | cumple |
| 17 | Color nunca solo | Busca signos y palabras | cumple |
| 18 | Sin emojis ni íconos | Rango de emojis | cumple |
| 19 | Dos niveles de título | h4 o más | cumple |
| 20 | Preguntas de recuperación | Reemplazada por la síntesis al pie de cada sección | cumple |
| 22 | Nada fuera del área imprimible | `verificar_margenes.py` mide con PyMuPDF los PDF que imprime el navegador (`herramientas/imprimir_a4.py`, en el directorio temporal) de todas las hojas A4 (resúmenes, parcial, soluciones y TP) y el `.docx` exportado por Word: texto (sin espacios), imágenes y trazos de cada hoja, sin contar el fondo de página; las diapositivas no se imprimen y no se miden | cumple |
| 23 | Un solo juego de márgenes | Todo `@page` de los CSS contra `--hoja-*` de `tokens.css`, y `incluir/espejo.lua` (`INTERIOR`, `EXTERIOR`) contra `tokens.css` | cumple |
| 24 | Diapositivas sin desborde | El navegador mide cada diapositiva en 1280x720, 390x844 y 844x390: nada sobresale a los costados ni necesita desplazarse a lo ancho; en escritorio ninguna se desplaza a lo alto | cumple |
| 25 | Letra y contraste de las diapositivas | Tamaño computado mínimo (en figuras, con la escala del SVG) y contraste real texto contra fondo, en claro y en oscuro | cumple |
| 26 | (retirada) | Era el folleto de diapositivas; las diapositivas no se imprimen | no aplica |
| 28 | Material A4 | Rótulo tipo plano de una sola línea en el margen superior (`material.lua`: materia y tema, más «Hoja n de N» del CSS), sin pie, sin datos personales ni fecha; el encabezado del parcial sin Legajo, Apellido y nombre, Curso ni fecha | cumple |
| 29 | Cabecera de hoja | Ningún `@top-*` de los CSS A4 usa sigla ni unidad (resúmenes y TP); el `.docx` no lleva la asignatura; el material lleva materia y tema en su línea superior (excepción explícita) | cumple |
| 30 | Encabezado | «Materia \| Unidad N» en un mismo párrafo, del lado izquierdo (completo, A4 y diapositivas) | cumple |
| 31 | Ancho de la Hoja A4 | El navegador mide: texto corrido de 160 mm o más; cuerpo con nota de 125 mm o menos; margen de 40 mm o más | cumple |
| 32 | Hoja A4 y material siempre claros | El navegador con el sistema en oscuro: sin botón, hoja y mesa claras, texto oscuro; sin `prefers-color-scheme` ni `data-theme` en el código | cumple |
| 33 | HTML para imprimir siempre hoja blanca | Con el sistema en oscuro, el PDF tiene texto oscuro sobre hoja blanca, sin modos de color (PyMuPDF sobre lo que imprime el navegador) | cumple |
| 34 | Un solo botón de tema | HTML completo y diapositivas: un botón, sigue al sistema sin elección guardada, un clic cambia los colores reales, se recuerda al recargar | cumple |
| 35 | Formatos de archivo y nombres | `nombres.py --probar` (todos los casos); ningún documento afirma ya que falte el PDF ni que los formatos se limiten a HTML y Word; los flujos resumir, tp y cuestionario y las guías generar-html y material-a4 nombran los archivos con `nombres.py` | cumple |
| 27 | Modo corto y metatexto | El corto tiene menos hojas A4 que el extenso (sin tope fijo) y búsqueda de frases metatextuales en los `.md` y `.html` de las demostraciones | cumple |
| 36 | Word, todos los tipos | Fuentes incrustadas, cuerpo de 12 pt, sin marcadores crudos de Pandoc (`:::`, `{#`), componentes traducidos, cabecera sin sigla ni unidad y rótulo del material solo con materia, tema y hoja; se construyen el resumen corto y las soluciones de resultados al vuelo; los márgenes, en la regla 22 con los PDF que exporta Word (`docx/demo/`: resumen 20 / 10 / 15,1 / 9,3; parcial 20 / 9,9 / 15,4 / 6,1; soluciones 20 / 10 / 15,4 / 6,1; TP 20 / 10 / 15,1 / 6,4) | cumple |

## Lo dudoso o no resuelto

- **Word, límites.** Las notas al margen son una tabla de dos columnas y no una columna de margen: si una nota es más alta que su párrafo, la fila crece. El índice del resumen no lleva números de página. Los campos de la cabeza (`STYLEREF`, `NUMPAGES`) se calculan al abrir o exportar con Word; con LibreOffice pueden verse vacíos. Los ejercicios largos de las hojas de soluciones pueden partirse entre hojas; los del parcial no. 
- **Celular real.** El deslizamiento y el toque en los bordes no se probaron con el dedo; solo con `<iframe>` de 390x844 y 844x390.
- **Mermaid, solo borradores.** Se dibuja bien en HTML completo, Hoja A4 y diapositivas , pero su tema violeta no sigue v4 ni el modo oscuro. Por eso un diagrama que deba verse como el resto del sistema va en SVG a mano o Graphviz; Mermaid queda para borradores rápidos.
- **Margen inferior de 5 mm.** Muchas impresoras no llegan a menos de 4 o 5 mm del borde: por eso nada va en ese margen (la cabeza de hoja pasó arriba y el rótulo del material es una línea en el margen superior). Si otra impresora corta, se sube `--hoja-inferior` en `tokens.css` y los `@page` (la regla 23 avisa si quedan distintos).
- **Word: operadores en Cambria Math.** Word no toma como fuente matemática una fuente solo incrustada: letras y cifras de las fórmulas salen en Noto Sans Math, pero `=`, `+` y la coma los dibuja con Cambria Math.
- **Word: renglón largo.** Con 180 mm de caja y 12 pt, el TP tiene unos 100 caracteres por línea (la regla 15 pide 45 a 90 en el HTML). Se prefirió aprovechar la hoja.

- **Rótulo con barra común.** El rótulo superior usa «|» (la barra de ancho completo de los nombres de archivo no está en Alegreya Sans).
- **«Hoja n de N» en doble faz** cuenta páginas, no hojas físicas (una hoja impresa a doble faz lleva dos números), igual que el original.
- **Erratas del original**: en un parcial digitalizado se mantienen y se avisan a la persona (en la hoja de resolución, con `::: errata`); no se corrigen en silencio.
- **Decimales.** El enunciado conserva el punto decimal del original (texto fiel); las soluciones, que son texto propio, usan coma.
- **Cuestionario:** las unidades en las preguntas van como texto («m/s»): la plantilla muestra texto plano, sin MathML. Apilarlas exigiría cambiar el formato del banco.
- **Rojo en el resumen.** La regla 6 pide un solo color cromático; el aspa roja de los errores frecuentes es una excepción semántica que responde a la semántica fija (rojo = error). Si molesta, se puede pasar a tinta sin perder información (el aspa y el título ya la llevan).
- **Unidades apiladas.** Con `\frac` las unidades apiladas en una línea de texto salen chicas pero legibles; con `\dfrac` quedan desproporcionadas. Se eligió `\frac` para unidades.
- **Vista A4 en oscuro.** Funciona, pero en oscuro el borde de la hoja casi no se ve sobre la mesa; como es la vista de impresión, quizá convenga dejar el A4 siempre claro y sacar el botón de ese formato.
- **Celular.** Se probó con un `<iframe>` de 390 px dentro de navegador sin interfaz (las consultas de medios responden a ese ancho), no en un teléfono real. En celular la letra de la figura sube a 19 unidades para seguir legible.
- **Paged.js y la cabeza de hoja.** La sección de la cabeza es la primera que empieza en esa hoja (convención de diccionario); `string(seccion, start)` de Paged.js no funcionó bien.
- **Tamaño.** Cada HTML suma unos 600 KB de fuentes; el material A4 pesa unos 1,7 MB por incluir Paged.js.

## Formato base de todo lo imprimible
Estas reglas ya viven en la plantilla, no hay que repetirlas en cada documento. Valen para la Hoja A4 y el Word del resumen, el material impreso (parcial, modelos, soluciones; el parcial digitalizado mantiene el contenido fiel al original pero con este formato) y el TP:
- **Texto justificado y sin guionado** en el cuerpo: Word (`construir_docx.py`, perfiles `tp`, `resumen` y `material`: `jc=both`, `sin_guiones`, sin `autoHyphenation`) y HTML A4 (`css/tp-a4.css`, `resumen-a4.css`, `material-a4.css`: `text-align: justify; hyphens: none`; titulos, tablas y epigrafes quedan a la izquierda o centrados).
- **Tablas con linea vertical entre columnas**: Word (`tablas()`, `insideV`, estilo `Table`) y HTML A4 (`th + th, td + td` en los tres CSS A4).
- **Leyenda de los graficos debajo del area de trazado**: `graficos_v4.leyenda(ax)`; nunca encima de datos ni rotulos.
- **Sin bloques de «supuestos» en el TP**: el error de cada instrumento va en su vineta del instrumental (regla de contenido de `flujos/tp.md`); las soluciones del material impreso si llevan `::: supuesto`.
- **Capturas de simuladores en alta resolucion**: ver `flujos/tp.md`.
