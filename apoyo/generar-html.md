# Guía: generar HTML (y PDF) con el sistema visual v4

Formato de salida por defecto. Convierte el Markdown fuente de un resumen a HTML con Pandoc y el sistema visual v4 (`sistema-visual/`), en uno de 3 formatos (HTML completo, Hoja A4 o Diapositivas HTML) y uno de 2 modos (extenso o corto), con o sin índice, y entrega la salida pedida (solo HTML, HTML + PDF o solo PDF en Hoja A4).

## Principio
El `.html` se genera SIEMPRE a partir del Markdown ya escrito (el `.md` fuente `… ｜ Resumen꞉ Unidad x ｜ <modo>.md`, en la carpeta de resúmenes de esa materia, o en `HTML y MD` si se separó). Ver `sistema-visual/DESIGN-SYSTEM.md`, sección 1. Nunca a mano, nunca convertido desde un `.docx`. Se genera **solo el formato y el modo pedidos**.

Todo lo visual vive en `sistema-visual/` (CSS, filtro Lua, fuentes incrustadas, tema claro u oscuro). La cadena de referencia es la función `resumen()` de `sistema-visual/construir.py`; el detalle de cada pieza está en `sistema-visual/LEEME.md`.

## Atajo: `estudio.py`
Para no armar el comando de Pandoc a mano, desde la raíz del proyecto:
```
python sistema-visual/estudio.py resumen "<base del .md>.md" --formato completo|a4|diapositivas --modo extenso|corto \
    [--indice] [--sin-espejo] [--practica] --salida html|html+pdf|pdf --carpeta "<carpeta de salida>" --nombre "<nombre base>"
```
Hace exactamente lo que describen los pasos de abajo (con el nombre base que dé `nombres.py`). Los pasos siguen documentados porque son el contrato: cualquier herramienta que no pueda correr `estudio.py` arma el comando a mano.

## Pasos
1. Si no se preguntó ya (o no está en `Materia.md`), preguntar (ver `flujos/resumir.md`): **formato** (HTML completo, Hoja A4, Diapositivas HTML), **salida** si es Hoja A4 (solo HTML, HTML + PDF, solo PDF), **modo** (extenso y explicativo, corto y rápido), **índice** (solo HTML completo u Hoja A4, modo extenso; en A4 sin enlaces), **¿se imprime o es solo digital?** (solo Hoja A4; imprime = márgenes espejados, por defecto; solo digital = `-M espejo=false`, alias `-M imprime=false`, ver `incluir/espejo.lua`) y, si la entrega lleva HTML y PDF, **carpetas** (¿HTML y MD en `HTML y MD` y el PDF afuera, o todo junto?). Se reutiliza lo anotado en `Materia.md`.
   **Nombres**: todo archivo nuevo se nombra con `sistema-visual/herramientas/nombres.py` (por ejemplo `nombre("Materia B", "Resumen", [1, 2, 3, 4], "corto", "hoja A4")` da `Materia B ｜ Resumen꞉ Unidad 1 a 4 ｜ corto ｜ hoja A4`), nunca a mano; ｜ y ꞉ reemplazan a `|` y `:`, que Windows y los servicios de nube no admiten.
2. Revisar que el Markdown tenga los metadatos: `materia`, `sigla` (dato interno: la cabeza de hoja ya no la lleva) y `unidad`, más `pagetitle` y `lang: es`. El encabezado sale «Materia | Unidad N». No hay color por materia: no se prepara ningún header ni archivo temporal.
3. Convertir, con el directorio de trabajo en la carpeta del `.md` (Pandoc resuelve las imágenes contra la carpeta actual; las figuras se citan `../Figuras/<archivo>` desde `HTML y MD` o `Figuras/<archivo>` desde la carpeta de resúmenes; desde otra carpeta tira `[WARNING] Could not fetch resource` y la imagen queda rota). Con `V4` = ruta de `sistema-visual` (en las rutas de ejemplo, separadores `/`; en Windows sirven igual):
   ```
   pandoc "<base del .md>.md" --standalone --embed-resources --math-method=mathml \
     --syntax-highlighting=pygments \
     --lua-filter=V4/incluir/estudio.lua -M formato=<completo|a4|diapositivas> -M modo=<extenso|corto> \
     [-M indice=true] \
     --include-in-header=V4/incluir/fuentes.html \
     --css=V4/css/tokens.css [completo y diapositivas: --css=V4/css/tokens-oscuro.css \
      --include-before-body=V4/incluir/tema.html] --css=V4/css/resumen-base.css \
     --include-after-body=V4/incluir/formulas-rectas.html \
     [--include-in-header=sistema-visual/mermaid-init.html] \
     <según el formato, abajo> \
     -o "<salida>.html"
   ```
   En versiones de Pandoc anteriores a las que aceptan `--math-method=mathml`, la opción equivalente es `--mathml` (`herramientas/entorno.py` elige la correcta). Se necesita Pandoc 3.8 o superior por `--syntax-highlighting`.
   - **completo** (HTML completo): `--css=V4/css/resumen-pantalla.css --css=V4/css/resumen-completo.css`
   - **a4** (Hoja A4, Paged.js; SIEMPRE clara: sin `tokens-oscuro.css` ni `tema.html`, sin botón): `--css=V4/css/resumen-a4.css --include-in-header=V4/incluir/a4-pagina.html --include-in-header=V4/incluir/paged-init.html` y, si NO se imprime, `-M espejo=false` (márgenes iguales en todas las hojas, «Hoja n de N» a la derecha; en Python `construir.resumen(..., espejo=False)`).
   - **diapositivas** (Diapositivas HTML), después de `formulas-rectas.html`: `--css=V4/css/resumen-diapositivas.css --include-after-body=V4/incluir/diapositivas.html`

   **Índice**: solo si la persona lo pidió y el modo es extenso en HTML completo o A4, `-M indice=true` (lo arma el filtro `estudio.lua`: con enlaces en HTML completo y como lista simple sin enlaces en el A4). Nunca `--toc`. En diapositivas y en el modo corto el filtro lo omite y avisa por la consola.

   Los 6 combos (3 formatos x 2 modos) y la variante con `practica`, con un solo comando: `python construir.py` en `sistema-visual`.

   **Usar siempre MathML, nunca `mathjax`**: MathJax depende de bajar una librería JS desde un CDN; sin conexión las fórmulas quedan en blanco sin error visible. MathML es nativo del navegador. `formulas-rectas.html` pone la letra recta.

   **Usar siempre `--embed-resources` junto con `--standalone`**: sin este flag Pandoc escribe el CSS como `<link>` a la ruta local de `sistema-visual/`, y el `.html` se ve sin estilo apenas se mueve a otra carpeta, otra máquina o el celular. Con el flag queda un único `.html` autocontenido (CSS, fuentes e imágenes incrustadas, sin CDN).

   **Resaltado de sintaxis**: siempre `--syntax-highlighting=pygments` (CSS generado por Pandoc, sin JS ni CDN). El bloque de código necesita el lenguaje después de los backticks (` ```python `).

   **Si el Markdown tiene un bloque ` ```mermaid `** (ver `apoyo/mermaid-diagramas.md`; vale en los tres formatos): agregar el include de `sistema-visual/mermaid-init.html` (librería embebida sin conexión, unos 3,4 MB, solo si hay un bloque mermaid). No hay posproceso: el script dibuja desde `textContent` y la Hoja A4 espera a que termine.

   Si `pandoc` no está en el PATH de la sesión, usar la ruta completa o definir la variable de entorno `ESTUDIO_PANDOC`.
4. Entregar en la carpeta de resúmenes de esa materia: solo lo pedido más el `.md` y las figuras que el Markdown referencia (en `Resúmenes/Figuras`), nunca archivos de trabajo. Si la persona eligió separar (HTML y PDF en la misma entrega), el `.html` y el `.md` van en `HTML y MD` y el PDF queda suelto en `Resúmenes`; si eligió todo junto, todo en `Resúmenes`.
   - **HTML completo y diapositivas**: `-o` directo a la carpeta de salida (o a `HTML y MD` si se separó) con el nombre de `nombres.py` (`… ｜ corto ｜ pantalla.html`, `… ｜ corto ｜ diapositivas.html`).
   - **Hoja A4**: `-o` al directorio temporal de la sesión y entregar con la salida elegida (`construir.resumen` arma el mismo comando):
     ```
     python sistema-visual/herramientas/imprimir_a4.py --entregar "<temporal>/x.html" "<Resúmenes>" "<nombre base>" --salida html|html+pdf|pdf [--sin-espejo]
     ```
     `<nombre base>` es el de `nombres.py` con formato `hoja A4`. Con `pdf`, en la carpeta queda solo el PDF (más el `.md`); con `html+pdf`, ambos con el mismo nombre base y `/Title` del PDF igual al nombre base. `--sin-espejo` solo si el HTML se armó con `-M espejo=false` (la herramienta lo comprueba con `imprimir_a4.espejo_de(html)` y falla si no coincide). En Python: `imprimir_a4.entregar(html, carpeta, base, salida, espejo=None)`. Si se separó, después de entregar a `Resúmenes` mover el `.html` (y el `.md`) a `HTML y MD`.

## Los tres formatos
- **HTML completo**: una columna de lectura en pantalla, sin aspecto de papel; en escritorio, sangría a la izquierda, texto y notas al margen; en celular (probado a 390 px) una sola columna con las notas debajo de su párrafo. Botón «Modo oscuro» / «Modo claro» (sigue al sistema, recuerda la elección con `localStorage` en `try/catch`). Plegables para las resoluciones; al imprimir salen abiertos.
- **Hoja A4**: páginas A4 reales en pantalla con Paged.js (embebido, sin conexión), con los márgenes de carpeta (valores en `css/tokens.css`): espejados a doble faz si se imprime, iguales con `-M espejo=false` si es solo digital. Cabeza de hoja solo con «Hoja n de N» y la sección (sin sigla ni unidad). Cuerpo de 12 pt (`--hoja-cuerpo`). El texto corrido ocupa los 169 mm útiles (unos 103 caracteres por línea), justificado y sin guionado; las tablas llevan línea vertical entre columnas y la leyenda de los gráficos va debajo del área de trazado (`graficos_v4.leyenda`), como en los TP; figuras y notas al margen conservan su columna de 44 mm. Impreso sale siempre claro. Es el formato para imprimir, y su PDF sale de imprimir este HTML (paso 4).
- **Diapositivas HTML**: un solo archivo autocontenido. `estudio.lua` arma una diapositiva por idea: la portada (`# título`), cada `##`, cada `###` y cada corte manual (`---` o `::: corte` vacío; en los otros formatos los cortes se ignoran). Letra fluida según la ventana; una diapositiva larga se desplaza dentro de sí misma. Navegación: flechas izquierda y derecha, AvPág y RePág, barra espaciadora (Mayús + espacio retrocede), Inicio y Fin, flechas arriba y abajo para desplazarse dentro de la diapositiva, F pantalla completa, G vista general (lista de títulos; Escape la cierra), toque en los bordes y deslizamiento en el celular, botones Anterior y Siguiente, contador «n de N», barra de progreso, `#3` en la dirección abre la diapositiva 3. Botón de modo claro u oscuro en la barra. Las resoluciones se revelan con un botón. Región `aria-live` que anuncia cada diapositiva; sin JavaScript queda una página común. **Solo pantalla** (compu y celular): las diapositivas no se imprimen, así que no tienen folleto, márgenes de carpeta ni CSS de impresión.

## Los dos modos (los aplica `estudio.lua` con `-M modo=`)
- **extenso**: estructura v4 completa (síntesis al pie de cada sección, definiciones, ejemplos con resolución plegable, fórmula clave, errores frecuentes, glosario, notas al margen).
- **corto**: sin síntesis por sección, sin glosario ni demostraciones (el filtro los quita y avisa); componentes propios: definición en una línea, fórmula clave, `::: ojo` (error típico, aspa roja y la palabra «Ojo.») y un mini ejemplo numérico sin `resolucion`. Es claramente más corto que el extenso de las mismas unidades; «una a dos hojas A4 o 10 a 15 diapositivas por unidad» es solo orientativo, no un tope.

## Word y PDF
Si el formato pedido es Word (resumen extenso o corto, no diapositivas), ver `apoyo/generar-docx.md`: `python sistema-visual/docx/construir_docx.py <md> --tipo resumen --modo extenso|corto [--indice] [--practica] [--sin-espejo] -o <x>.docx --chequeo`, desde el mismo `.md`. PDF: es el mismo HTML de la Hoja A4 impreso con navegador sin interfaz (`imprimir_a4.py`, paso 4); no hay otro generador. HTML completo y diapositivas son solo HTML.

## Componentes del Markdown
La tabla completa de clases de Pandoc (definición, ejemplo con resolución plegable, clave, ecuación numerada, síntesis, errores, ojo, glosario, margen, figuras y tablas numeradas, referencias cruzadas, práctica) está en `sistema-visual/DESIGN-SYSTEM.md`, sección 1, y en `sistema-visual/LEEME.md`, «Clases de Pandoc para cada componente». El filtro avisa en la consola si falta una síntesis (modo extenso), si hay componentes de práctica sin `practica: true` o si se omite algo por el modo: leer esos avisos antes de dar el HTML por bueno. Si hay que ajustar el estilo, editar el CSS de `sistema-visual/css/` que corresponda y correr `python construir.py` en `sistema-visual` (`verificar_reglas.py` tiene que seguir pasando).

## Chequeo rápido (sin renderizar página por página)
- Confirmar que `pandoc` terminó sin error ni `[WARNING] Could not fetch resource`, y revisar los avisos de `[estudio.lua]`.
- Confirmar que el `.html` no tiene ningún `<link rel="stylesheet"` apuntando a una ruta externa: tiene que quedar el CSS como `<style>` en línea.
- Si hay fórmulas: buscar un `<math` vacío o seguido de `</math>` y contar que la cantidad de `<math` coincida con los bloques `$...$` y `$$...$$` del Markdown. Solo si algo no cierra, o la fórmula ya venía marcada como densa desde el analista, capturar con `sistema-visual/herramientas/captura_espera.py` (ver `apoyo/verificacion-visual.md`).
- Diapositivas: contar las `<section class="diapositiva"` (modo corto: unas 10 a 15 como guía, no tope) y, si un bloque es muy largo, agregar un corte `---`. Para una captura exacta a 1280x720, 390x844 u 844x390 usar `captura_espera.py`.
- Para lo demás no hace falta re-verificar cada documento: la plantilla v4 ya se verificó con `verificar_reglas.py` y capturas.
- Si el Markdown tenía un bloque `mermaid`, ese sí necesita la captura siempre (Mermaid dibuja recién con JavaScript).
