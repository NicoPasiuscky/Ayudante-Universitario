# Flujo: explicar (repaso conversacional)

Explica un tema, una unidad o un conjunto de unidades de una materia de forma conversacional en el chat, para repasar o ponerse al día antes de un parcial o un final, sin generar archivos por defecto. Se usa cuando la persona quiere entender, repasar o que la pongan al día con contenido de cátedra; no cuando pide un resumen formal para guardar (eso es `resumir.md`) ni ayuda con un entregable de cursada (eso es `tp.md`).

El objetivo es explicar contenido de cátedra con el mismo rigor que un resumen, pero sin el costo de guardar y verificar formalmente cada vez. Está pensado para el repaso rápido, el «no entiendo tal cosa» o ponerse al día con varias unidades de una vez.

## Flujo
1. **Identificar materia y alcance.** Si es la primera vez que se toca esa materia, resolver la fuente igual que en el Paso 0 de `resumir.md` (qué subcarpetas son fuente válida de cátedra) y confirmar con la persona; no hace falta resolver ni crear la carpeta de salida si no se va a guardar nada ahora. Si ya existe el `Materia.md` de la materia, usarlo.

2. **Priorizar lo ya resumido, sin importar el modo.** Si en la carpeta de resúmenes (`HTML y MD`, o `Resúmenes` si no se separó) ya existe un `.md` de resumen de la unidad pedida (`… ｜ Resumen꞉ Unidad x ｜ extenso.md` o `… ｜ corto.md`), explicar a partir de ese resumen en vez de releer la fuente cruda. Si hay de los dos modos, usar el extenso para explicar y el corto para repasar.

3. **Si no hay resumen todavía**, pedirle al rol `analista-fuente` la estructura del alcance pedido (solo lo que hace falta para esta explicación, no toda la materia) y explicar directamente desde esa extracción, sin pasar por `profesor`, `verificador` ni exportación (son pasos del flujo persistente de `resumir.md`).

4. **Rigor de fuente.** No inventar ni dejar afirmaciones sin sustento. En el chat se puede reformular y completar con conocimiento propio cuando la fuente es escueta, pero **distinguiéndolo**: lo que no viene de la fuente se dice como tal (acá sí corresponde el comentario, porque la conversación no es un documento de estudio), y las ambigüedades o contradicciones de la fuente se señalan en vez de resolverse en silencio. Aplicar el estándar de las áreas de conocimiento de la materia (`apoyo/estandares-por-area.md`).

5. **Gráficos reales cuando el tema lo amerite.** Misma regla que en cualquier otro flujo: nunca una interpretación en texto de cómo sería un gráfico. Generarlos con la guía que corresponda (`apoyo/graficos-matematicos.md`, `apoyo/graphviz-diagramas.md`, `apoyo/plantuml-diagramas.md`), verificarlos con `apoyo/verificacion-visual.md` y mostrárselos a la persona en el chat (adjuntando el archivo desde el directorio temporal, si la herramienta lo permite). No hace falta guardarlos salvo que pida persistir la explicación como resumen formal.

6. **Si la persona pide guardarlo o exportarlo** en cualquier momento (HTML, `.docx`, «guardalo», «quiero tenerlo después»), no reconstruir todo de cero: seguir con `resumir.md`, reutilizando la extracción y el contenido ya generado (fuente resuelta, gráficos ya hechos) en vez de repetir el trabajo. Recién ahí preguntar formato y modo, resolver la carpeta de salida si todavía no está confirmada y correr `profesor` + `verificador` antes de exportar.

## Economía de contexto
Mismo criterio que `resumir.md`. Si el alcance abarca varias unidades de una sola vez está bien: es exactamente el caso de uso de `explicar` para repasar antes de un parcial. No hace falta trocearlo en una conversación por unidad, porque no hay pasos de guardado ni verificación formal que paguen ese costo por unidad.
