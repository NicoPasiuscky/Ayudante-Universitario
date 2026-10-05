# Guía: Graphviz (árboles, jerarquías, flujos y dependencias)

Genera diagramas de árboles, jerarquías, dependencias, flujos de proceso y relaciones entre conceptos con Graphviz (DOT). Se usa solo cuando la fuente no trae un diagrama usable para ese concepto (ver `roles/profesor.md`, regla «Diagramas: extraer de la fuente antes que generar»). No para UML formal (`apoyo/plantuml-diagramas.md`) ni gráficos de funciones o superficies (`apoyo/graficos-matematicos.md`).

## Cuándo usarla
Solo si el `profesor` ya evaluó que la fuente no tiene un diagrama usable para ese concepto (o el que tiene es de mala calidad). Nunca como primera opción: ver la regla de prioridad en `roles/profesor.md`. Para diagramas chicos (hasta unos 6 o 7 nodos) conviene el SVG a mano.

## Herramienta
Graphviz (`dot`). Instalación en `MANUAL-DE-IMPLEMENTACION.md`; probar con `dot -V`.

## Formato de salida: SVG por defecto
Como el formato de entrega por defecto es HTML, generar **SVG** (`dot -Tsvg archivo.dot -o archivo.svg`): vectorial, nítido a cualquier zoom, mucho más liviano que un PNG para diagramas de líneas y cajas. Referenciarlo en el Markdown igual que una imagen: `![epígrafe](archivo.svg)`. Solo generar PNG (`-Tpng -Gdpi=300`) si el pedido puntual es un `.docx` (ver `apoyo/generar-docx.md`), porque Word no siempre maneja bien el SVG embebido (aunque `construir_docx.py` ya pasa los SVG a PNG por su cuenta).

**Archivos:** el `.dot` fuente es descartable: trabajarlo en el directorio temporal. A la carpeta de figuras de la materia solo va el `.svg` o `.png` final que el resumen referencia, nunca el `.dot`.

## Estilo (sistema visual v4, ver `sistema-visual/DESIGN-SYSTEM.md`, sección 3)
- Texto en Alegreya Sans (`fontname="Alegreya Sans"`), la letra del resumen; si no está instalada en el sistema, instalar o apuntar a los TTF de `sistema-visual/fonts/originales`. Nunca Arial.
- Diagrama pensado para hoja (HTML A4 o `.docx`): 180 mm de ancho como máximo, el área útil A4 con los márgenes de carpeta (180 x 277 mm).
- Tinta `#1D1F23` para trazos, bordes y texto; nodos sin relleno de color (`style=solid`, a lo sumo blanco). Un solo realce en azul birome `#1C3F94` en el nodo o la arista que haya que destacar, nunca un color por nodo ni por categoría.
- `rankdir` según lo que se lea mejor (LR para procesos secuenciales, TB o BT para jerarquías verticales; por ejemplo `rankdir=BT` para una jerarquía de abstracciones).
- Etiquetas de arista cortas: si una etiqueta es una frase larga, partirla en 2 líneas con `\n` dentro del label en vez de dejar una línea larguísima.

## Paso obligatorio después de generar
Pasar por `apoyo/verificacion-visual.md` antes de incluir el diagrama en el resumen. Nunca asumir que el diseño automático de Graphviz salió bien a la primera (superposición de nodos, flechas que se cruzan mal, texto que se corta).
