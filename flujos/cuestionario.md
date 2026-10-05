# Flujo: cuestionario (autoevaluación interactiva)

Genera o extiende un cuestionario interactivo (HTML autocontenido; opción múltiple, selección múltiple, verdadero o falso, respuesta numérica, V o F por ítems, completar con menús y enunciados con partes, con fórmulas, tablas y figuras) para autoevaluarse, a partir de las unidades teóricas y prácticas ya trabajadas de una materia, o de sus parciales viejos para un nivel más exigente. Se usa cuando la persona pide un cuestionario, un banco de preguntas, autoevaluación o práctica; no para un resumen (`resumir.md`) ni un TP (`tp.md`).

Dos niveles independientes por materia, nunca mezclados en el mismo banco:
- **Nivel unidad**: preguntas de repaso conceptual, basadas en las unidades teóricas y prácticas ya resueltas con `resumir.md`.
- **Nivel parcial**: preguntas más exigentes, basadas en los parciales viejos de esa materia (carpeta de parciales: fuente de solo lectura, igual que teoría y práctica).

## Paso 0: fuente y salida ya resueltas
Usa el mismo `Materia.md` que `resumir.md` (en la raíz de la carpeta de la materia). Si todavía no existe para esta materia, correr primero el Paso 0 de `resumir.md`. La salida del cuestionario va a la subcarpeta `Cuestionarios` de la materia, junto a la de resúmenes (ver `INSTRUCCIONES.md`, «Fuentes y salidas»). Si esa carpeta ya existe con material propio de la persona, se agregan archivos sin pisar los suyos; si no existe, crearla.

## Archivos por materia y nivel
En `Cuestionarios`, dos pares de archivos independientes, nombrados con `sistema-visual/herramientas/nombres.py` (nunca a mano; ｜ y ꞉ reemplazan a `|` y `:`, que Windows y los servicios de nube no admiten):
- `[Materia] ｜ Cuestionario teórico꞉ Unidad 1 a 3` (o `Cuestionario práctico`), con `.json` y `.html` (nivel unidad).
- El mismo nombre con `detalle="parciales"` al final, `… ｜ Cuestionario teórico꞉ Unidad 1 a 3 ｜ parciales`, con `.json` y `.html` (nivel parcial).
- Un banco que mezcla teoría y cálculo en un solo archivo usa el tipo `Cuestionario` sin apellido: `[Materia] ｜ Cuestionario꞉ Unidad 1 a 5`, sin sufijo `parciales`.

El cuestionario es solo HTML (y su banco `.json`): no tiene salida PDF ni Word, no tiene sentido imprimirlo. No se renombran los viejos.

El `.json` es la fuente única (el banco de preguntas real, un array de las entradas que describe `roles/cuestionador.md`); el `.html` es siempre una exportación regenerada de él, igual que el `.md` y el `.html` de un resumen. Nunca editar el `.html` a mano.

## Flujo para agregar una tanda de preguntas
1. **Fuente de esta tanda**:
   - Nivel unidad: si la unidad ya tiene mapeo del `analista-fuente` (existe `outline - Unidad [N].md`), reutilizarlo. Si no, pedirle al analista esa unidad primero (mismo paso que en `resumir.md`, con el mismo caché de `trabajo/cache/` si la fuente es un PDF ya extraído).
   - Nivel parcial: hacen falta DOS mapeos, no uno (ver «Dos modos» en `roles/cuestionador.md`; las preguntas son inventadas y ancladas en la unidad, calibradas en dificultad contra el parcial, nunca reformulaciones del parcial real):
     1. El mapeo de la unidad teórica y práctica correspondiente: mismo criterio que nivel unidad (reutilizar si ya existe).
     2. El mapeo de uno o más parciales viejos de esa materia. Si esos PDF son hojas escaneadas sin capa de texto (caso frecuente), el analista va a necesitar OCR: ver «Páginas escaneadas» en `roles/analista-fuente.md`.
2. **Redactar preguntas**: rol `cuestionador`, pasándole el o los mapeos del paso 1 y el banco JSON ya existente de ese nivel para esa materia, para que no duplique y continúe la numeración de `id`.
3. **Verificar**: rol `verificador`, en un paso o agente aparte, que revisa solo las preguntas nuevas de esta tanda contra la fuente (ver «Verificación de bancos de preguntas» en `roles/verificador.md`). Si algo no pasa, volver al paso 2 antes de seguir: nunca agregar una pregunta sin verificar al banco.
4. **Guardar y regenerar el HTML**:
   - Agregar las preguntas ya verificadas al array del `.json` correspondiente (crearlo si es la primera tanda).
   - Regenerar el `.html` a partir de `sistema-visual/cuestionario/Plantilla-Cuestionario.html` (ejemplo completo en `sistema-visual/demo/construir_cuestionario.py`): copiar la plantilla, reemplazar los marcadores (`{{ACCENT}}` con `#1C3F94`: se conserva por compatibilidad pero ya no cambia el color, no hay color por materia; `{{TITULO_PAGINA}}`, `{{H1}}`, `{{PREGUNTA_HERO}}` y `{{LEDE}}` con texto acorde a la materia y al nivel; `{{KICKER}}` es una línea común, no un rótulo en mayúsculas, y admite `<b>Materia</b>`; `{{QUIZ_LEN}}` con `Math.min(20, total)` por defecto, o lo que pida la persona; `{{LS_KEY}}` con un identificador único del estilo `[materia]_[nivel]_best_score`) y reemplazar el bloque entre `/* CUESTIONARIO_JSON_START */` y `/* CUESTIONARIO_JSON_END */` por `window.QUESTIONS = [...banco completo actualizado...];`, precedido de `window.MULTI_PARCIAL = true;` si el banco usa nota parcial en las selecciones múltiples (se pregunta al armar un banco nuevo y se anota en `Materia.md`). La plantilla es **siempre oscura**, sin variante clara ni detección de `prefers-color-scheme`.
   - Si hay que cambiar la plantilla: editar `sistema-visual/cuestionario/plantilla-fuente.html` o `css/cuestionario.css` (nunca la plantilla final a mano) y correr `python construir.py` en `sistema-visual` (arma la plantilla con `cuestionario/construir_plantilla.py` y corre `verificar_reglas.py`).
   - Guardar el `.html` resultante junto al `.json`, en `Cuestionarios`. No hace falta Pandoc ni ningún paso de `generar-html`: este HTML no viene de Markdown, es la plantilla ya completa.
5. **Verificación visual liviana**: capturar el `.html` con `sistema-visual/herramientas/captura_espera.py` (Firefox sin interfaz; puede hacer clic antes de capturar, por ejemplo empezar y ver el resultado; ver `apoyo/verificacion-visual.md`) para confirmar que la pantalla de inicio carga bien y el JSON no rompió la sintaxis del `<script>`. No hace falta jugar el cuestionario entero. La captura va al directorio temporal, nunca a la carpeta de la persona.

## Tipos de pregunta y contenido del enunciado
Disponibles en todo cuestionario de cualquier materia y nivel: al pedirle al `cuestionador` hay que pasarle esta lista y decirle que elija el tipo que pide el contenido (guía en `roles/cuestionador.md`, «Cuándo usar cada tipo»). Además de `mc-single`, `mc-multi` y `tf`, la plantilla admite `numeric` (respuesta escrita con tolerancia), `tf-items` (V o F por ítems), `cloze` (menús dentro de la frase) y `group` (enunciado común con partes); todo puntúa de 0 a 1 y los ítems o huecos suman por parte. El enunciado, las opciones y las explicaciones llevan fórmulas entre `$...$` (TeX básico, MathML de letra recta), y cualquier pregunta, parte u opción puede traer `table` y `figure` (SVG en línea con `currentColor` y `var(--azul)`). Una selección múltiple con nota parcial (suma 1/k por correcta, resta 1/(n-k) por incorrecta, sin bajar de 0) se activa con `"partial": true` o con `window.MULTI_PARCIAL = true` antes del banco. Formato completo en el comentario de `sistema-visual/cuestionario/plantilla-fuente.html` y en `roles/cuestionador.md`. Los errores del banco (índices fuera de rango, `[[n]]` que no coinciden, ids repetidos) salen en la consola del navegador. Verdadero / Falso no se mezcla de orden.

## Modos del cuestionario
La pantalla de inicio deja elegir entre dos modos antes de comenzar. No hay «Mostrar opciones», ni autoevaluación seguro / dudo / adivino, ni SM-2 graduado.
- **Práctica** (por defecto): sin límite de tiempo, corrección al final, orden libre entre preguntas. Prioridad de repetición espaciada SM-2 en el sorteo (calidad 5 si acierta, 2 si no) y mejor resultado guardado como porcentaje y mostrado como nota sobre 10.
- **Parcial**: se elige el tiempo con botones de 30, 60, 90 o 120 minutos, o se escribe el que se quiera (entero de 1 a 300; si no es válido, el botón de comenzar queda inhabilitado y se explica por qué). Interruptor «Permitir volver a preguntas anteriores»: activado permite saltar y cambiar respuestas; desactivado solo se avanza. Temporizador visible durante todo el intento, sin animación; al quedar poco (el 20 % del total o 5 minutos, lo menor) muestra «! Queda poco tiempo». Corrección al final; al vencer el tiempo se corrige solo con lo respondido (lo no respondido cuenta como incorrecto) y se muestra la nota sobre 10.

Reglas propias del modo Parcial:
- El SM-2 **no se actualiza** en Parcial (es una simulación, no repaso espaciado); el sorteo, el orden aleatorio de preguntas y opciones y la cantidad (`{{QUIZ_LEN}}`) son los mismos.
- El mejor resultado del Parcial se guarda aparte del de Práctica.
- El reloj se calcula con hora de inicio y hora límite, no con un contador: sigue corriendo aunque se cambie de pestaña. El intento en curso se guarda y, si se recarga la página, el inicio ofrece «Retomar el parcial» o descartarlo; si el tiempo ya se agotó, lo corrige con lo respondido.
- Claves de `localStorage` (todas dentro de `try/catch`): `{{LS_KEY}}` (mejor de Práctica), `{{LS_KEY}}_sm2`, `{{LS_KEY}}_parcial` (mejor de Parcial) y `{{LS_KEY}}_parcial_intento` (intento en curso, se borra al terminar). Un cuestionario viejo se regenera con la plantilla nueva sin tocar el banco.
- En los resultados hay «Nuevo intento» (mismo modo y configuración) y «Cambiar de modo» (vuelve al inicio).

## Economía de contexto
Igual que `resumir.md`: una tanda de preguntas por conversación alcanza, reutilizando el mapeo del analista si ya existe. No releer la fuente si la unidad o el parcial ya se procesó para el resumen o para una tanda anterior del cuestionario.
