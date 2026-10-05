# Flujo: resumir

Resume una unidad, una materia entera o un tema corto para estudiar. Pregunta formato (HTML completo, Hoja A4, Diapositivas HTML o Word), salida si es Hoja A4 (solo HTML, HTML + PDF o solo PDF) y modo (extenso y explicativo o corto y rápido); resuelve la fuente y la carpeta de salida, redacta el resumen en Markdown, lo verifica y genera solo lo que se pidió.

Se activa cuando la persona pide un resumen formal para guardar. Para repasar en el chat, ver `explicar.md`; para un entregable de cursada, `tp.md`.

## Paso 0: resolver fuente y salida (solo la primera vez por materia)
Si el `Materia.md` de la materia todavía no existe o está incompleto (plantilla en `configuracion/Materia.md`): buscar en la carpeta raíz de la universidad (`configuracion/proyecto.md`) qué subcarpetas son programa, teoría y práctica de la cátedra y cuál es la carpeta de salida (`Resúmenes`; si ya existe una variante del nombre, por ejemplo sin tilde, usar esa; si no hay ninguna, preguntar). **Confirmar con el usuario** antes de seguir y anotar todo en `Materia.md`, creado en la RAÍZ de la carpeta de la materia, fuera de la carpeta de resúmenes (ver `INSTRUCCIONES.md`, «Fuentes y salidas»). Las veces siguientes, usar directo lo ya anotado.

Nunca escribir ni modificar nada dentro de las subcarpetas de fuente.

## Paso 1: preguntar formato, salida y modo (salvo que ya estén dichos)
Preguntar en este orden. Si el usuario ya lo dijo en el pedido o quedó guardado en `Materia.md` o en `configuracion/proyecto.md`, se reutiliza sin volver a preguntar.

1. **Formato**: HTML completo (pantalla, celular y escritorio, modo claro u oscuro), Hoja A4 (para imprimir), Diapositivas HTML (una idea por diapositiva, con navegación y modo claro u oscuro) o Word (`.docx`, mismo Markdown, para extenso y corto). Word no combina con diapositivas. El modo claro u oscuro con botón existe solo en HTML completo y diapositivas; la Hoja A4 y el Word salen siempre claros.
2. **Salida**, solo si el formato es Hoja A4: **solo HTML**, **HTML + PDF** o **solo PDF**. El PDF es ese mismo HTML impreso con navegador sin interfaz (`imprimir_a4.entregar`, ver `apoyo/generar-html.md`); no hay otro generador. Con «solo PDF» el HTML se arma en el directorio temporal y en la carpeta de salida quedan solo el PDF y el `.md` fuente; con «HTML + PDF», ambos con el mismo nombre base. HTML completo, diapositivas y Word no tienen esta pregunta.
3. **Modo**: **extenso y explicativo** (para empezar a estudiar: conceptos parafraseados para que se entiendan mejor, algo más corto que la fuente, sin llegar a ser un libro de cátedra) o **corto y rápido** (para repasar y terminar de fijar: mucho más corto, conceptos cortos). El largo del corto (una a dos hojas A4 o 10 a 15 diapositivas por unidad) es orientativo, no un tope; lo único obligatorio es que el corto sea claramente más corto que el extenso de las mismas unidades.
4. **Índice**, solo si el formato es HTML completo u Hoja A4 y el modo es extenso (en A4 sale sin enlaces). Cualquier combinación de modo y formato es válida.
5. **¿Se imprime o es solo digital?** Imprime = márgenes espejados a doble faz (por defecto). Solo digital = márgenes iguales en todas las hojas y «Hoja n de N» siempre a la derecha: Pandoc `-M espejo=false` (alias `-M imprime=false`), en Python `construir.resumen(..., espejo=False)`, en la entrega `imprimir_a4.py --entregar ... --sin-espejo` y en Word `construir_docx.py --sin-espejo`. No aplica a HTML completo ni a diapositivas.
6. **Carpetas**, solo si la entrega lleva HTML y PDF: «¿HTML y MD en una carpeta aparte y los PDF afuera, o todo junto?». Las figuras van siempre en `Resúmenes/Figuras`.

**Se genera SOLO lo que se pide**: un modo en un formato. Si después quiere otro formato del mismo modo, alcanza con re-exportar el mismo `.md` (`apoyo/generar-html.md`); no hay que redactar de nuevo.

**Tema corto.** Si lo que pide resumir es un tema corto (una tabla de fórmulas, un procedimiento puntual) y no una o varias unidades, es un resumen igual: este mismo flujo. Preguntar el tema si no es obvio. El nombre no lleva «Unidad x»: `[Materia] ｜ Resumen de [tema]` (conserva modo y formato) o `[Materia] ｜ Tabla de fórmulas` (sin modo ni formato: tiene un largo definido y siempre es hoja A4; solo se elige la salida y la extensión distingue el archivo). No existe «formulario» como tipo de documento.

**Nombres de archivo.** Todo archivo nuevo se nombra con `sistema-visual/herramientas/nombres.py` (`nombre(materia, tipo, unidades, modo, formato, tema=...)`), nunca a mano: `Materia ｜ Resumen꞉ Unidad 1 a 4 ｜ corto ｜ hoja A4` (el `.md` fuente lleva el modo pero no el formato; el PDF usa el mismo nombre base que su HTML). Los caracteres ｜ y ꞉ reemplazan a `|` y `:`, que Windows y los servicios de nube no admiten; las dos constantes viven solo en ese módulo. No se renombran archivos viejos.

## Flujo por unidad
1. **Analizar la fuente** (solo si hace falta): rol `analista-fuente` (`roles/analista-fuente.md`). **Derivación sin releer**: si ya existe un resumen extenso verificado de esa unidad (su `.md` extenso, marcado verificado en `Materia.md`), el modo corto se deriva de él sin releer la fuente; si no existe, se hace desde la fuente. Si un tema ya fue resumido en ese mismo modo, no reprocesar. Si la fuente es un PDF que ya cubrió otra unidad antes, el analista reutiliza el texto ya extraído en `trabajo/cache/[Materia]/[NombreFuente].txt` en vez de reabrir el PDF (ver `INSTRUCCIONES.md`, «Excepción: caché técnico»).

2. **Redactar el resumen**: rol `profesor` (`roles/profesor.md`), diciéndole el modo. Salida: el `.md` fuente, con el nombre de `nombres.py` (`… ｜ Resumen꞉ Unidad 1 a 4 ｜ corto.md`), en la carpeta de salida (`Resúmenes`, o `Resúmenes/HTML y MD` si se separó). Las imágenes que use van en `Resúmenes/Figuras` y el `.md` las cita con ruta relativa (`../Figuras/<archivo>` si el `.md` está en `HTML y MD`, o `Figuras/<archivo>` si está en `Resúmenes`). Estructura, componentes y cortes de diapositiva: `roles/profesor.md` y `sistema-visual/DESIGN-SYSTEM.md`, sección 1. Preguntas previas y «Probá sin mirar» solo si el usuario las pide (`practica: true`).
   **Regla de fuente:** en el modo extenso se puede reformular y completar con conocimiento propio cuando la fuente es escueta, pero el documento **no lleva ningún comentario metatextual** («según la fuente», «está parafraseado», «no incluye la resolución»). La trazabilidad va afuera: el profesor entrega en la conversación, y anota en `Materia.md`, la lista breve de **agregados propios**.

3. **Verificar**: rol `verificador` (`roles/verificador.md`), en un paso o agente aparte del que redactó (opcionalmente con Codex como motor, ver ese rol). Contrasta el resto del documento contra la fuente y los agregados propios contra fuentes confiables; el modo corto contra el extenso o la fuente. Calcula Cobertura y Exactitud y, si algo no cierra, lo señala en la conversación en vez de dar la unidad por cerrada en silencio. Actualiza la tabla de cobertura de `Materia.md` (modo, formato, agregados propios).

4. **Exportar**: `apoyo/generar-html.md` con el formato, la salida, el modo y el espejo (se imprime o no) elegidos (con salida PDF, `imprimir_a4.entregar`). Si el formato es Word, `apoyo/generar-docx.md`: `python sistema-visual/docx/construir_docx.py <md> --tipo resumen --modo extenso|corto [--indice] [--practica] [--sin-espejo] -o <x>.docx --chequeo` (mismo modo y mismo `.md`; el índice del Word no lleva números de página).

## Flujo para «toda la materia» (resumen final)
Repetir el flujo por unidad (pasos 1 a 3) para cada unidad con fuente disponible que todavía no esté resumida en ese modo. Antes de compilar, revisar `Materia.md`: si falta una unidad sin resumir, avisar cuáles antes de armar un documento incompleto en silencio.

Compilar (rol `profesor`): portada + índice (solo extenso, HTML completo o A4) + cada resumen de unidad en orden de programa. No vuelve a leer la fuente ni recalcula nada: solo compone lo ya escrito. Portada por defecto: un `#` simple con el nombre de la materia, sin nada visual.

En la Hoja A4 cada unidad arranca en una página nueva (lo resuelve `generar-html` con `# Título {unidad=N}` por unidad); en diapositivas cada `#` es una portada de unidad.

## Portada elaborada (opcional, paso manual del usuario)
Por defecto la portada del resumen final es un `#` simple con el nombre de la materia. Si el usuario quiere algo más elaborado, es trabajo suyo, fuera de este flujo.
1. La arma con la herramienta de diseño que prefiera, con la paleta del sistema v4 (tinta y azul birome; ver `sistema-visual/DESIGN-SYSTEM.md`, sección 3), y la exporta como PNG.
2. Cuando avisa «ya la exporté», mover ese PNG (no copiarlo) a `Resúmenes/Figuras` como `Portada - [Materia].png`.
3. En el Markdown del resumen final, la primera línea (antes del título y el índice) queda:
   ```
   <div class="portada">

   ![Portada](../Figuras/Portada - [Materia].png)

   </div>
   ```
   **Pendiente del sistema visual**: todavía no tiene reglas CSS para `.portada`. La primera vez que se pida, agregar la regla en `sistema-visual/css/resumen-base.css` (y el salto de página en `resumen-a4.css`), correr `python construir.py` en `sistema-visual` y confirmar que `verificar_reglas.py` pasa.
4. Regenerar como siempre: la portada es solo la primera imagen del documento.

## Notas de economía de contexto
Trabajar una unidad por vez, guardando cada archivo apenas está terminado. **Encadenar unidades** solo si el trabajo es pesado (dos o más unidades en modo extenso, fuentes largas o escaneadas; criterio completo en `INSTRUCCIONES.md`, «Economía de contexto»). Las unidades en modo corto derivadas de extensos ya verificados, un tema corto o una sola unidad van en una sola sesión, y se avisa antes de empezar cuál de los dos caminos se toma.

Cuando se encadena, al cerrar cada unidad (resumen verificado y `Materia.md` al día) NO seguir con la siguiente en la misma conversación: entregar en el chat, en un bloque de código listo para copiar, un **prompt autocontenido** para la unidad que sigue. La persona abre otra sesión, lo pega y esa sesión resume. El prompt lleva materia, unidad, formato, salida, modo, índice, si se imprime, carpetas, lo ya resuelto en `Materia.md` (fuente y salida, no hay que volver a preguntar) y la orden de entregar, al terminar, el prompt de la unidad siguiente. Así hasta la última; después de ella, el prompt que se entrega es el de la compilación final («toda la materia»), también para una sesión aparte. Ese paso final es la excepción: no relee fuentes, es liviano y solo junta lo ya resumido.
