# Guía: PlantUML (UML formal)

Genera diagramas UML con semántica formal (casos de uso, clases, secuencia, actividad, estados) para materias de análisis y diseño de sistemas, desarrollo de software, paradigmas de programación o cualquier materia que modele con UML. Se usa solo cuando la fuente no trae el diagrama, o el que trae es de mala calidad (ver `roles/profesor.md`). No para árboles o jerarquías genéricos (`apoyo/graphviz-diagramas.md`).

## Cuándo usarla
Misma regla que `graphviz-diagramas.md`: solo si la fuente no tiene un diagrama usable para ese concepto. Para diagramas chicos conviene el SVG a mano (ver `roles/profesor.md`).

## Herramienta
Java y `plantuml.jar` (instalación en `MANUAL-DE-IMPLEMENTACION.md`). Probar primero `plantuml -version`; si no está en el PATH de la sesión, usar la ruta completa (`java -jar <ruta>/plantuml.jar`). El `.jar` lo descarga la persona desde la página oficial de lanzamientos de PlantUML: no descargues ni ejecutes binarios sin que ella lo autorice.

## Formato de salida: SVG por defecto
```
plantuml -tsvg archivo.puml
```
Igual que `graphviz-diagramas.md`: SVG por defecto (HTML es el formato de salida por defecto), PNG (`-tpng`) solo si el pedido puntual es `.docx`.

**Archivos:** el `.puml` fuente es descartable: trabajarlo en el directorio temporal. A la carpeta de figuras de la materia solo va el `.svg` o `.png` final que el resumen referencia, nunca el `.puml`.

## Estilo
Usar `skinparam` al inicio del `.puml` para que el diagrama no quede con los colores por defecto de PlantUML (que no coinciden con el resto del documento):
```
skinparam backgroundColor white
skinparam defaultFontName "Alegreya Sans"
skinparam defaultFontColor #1D1F23
skinparam ArrowColor #1D1F23
skinparam ClassBorderColor #1D1F23
skinparam ClassBackgroundColor white
skinparam shadowing false
```
Sistema visual v4 (ver `sistema-visual/DESIGN-SYSTEM.md`, sección 3): tinta `#1D1F23`, sin rellenos de color, un solo realce en azul birome `#1C3F94` (por ejemplo en el elemento a destacar), sin color por materia. Letra Alegreya Sans (TTF en `sistema-visual/fonts/originales` si no está instalada); nunca Arial. Diagrama pensado para hoja (HTML A4 o `.docx`): 180 mm de ancho como máximo, el área útil A4 con los márgenes de carpeta (180 x 277 mm).

## Qué diagrama usar según lo que pide la fuente
- Caso de uso: actores + elipses de casos de uso.
- Clases: atributos y métodos con visibilidad exacta si la fuente la especifica (no inventar `+`, `-` o `#` si la fuente no los da).
- Secuencia: orden temporal de mensajes entre objetos o participantes.
- Actividad: flujo de un proceso con decisiones.
- Estados: la misma notación que use la cátedra para las máquinas de estado; no mezclar convenciones.

## Paso obligatorio después de generar
Pasar por `apoyo/verificacion-visual.md` antes de incluir el diagrama: PlantUML también puede generar diseños con texto cortado o cajas superpuestas en diagramas con muchos elementos.
