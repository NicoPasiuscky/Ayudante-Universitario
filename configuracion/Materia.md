# [Nombre completo de la materia]

Este archivo va en la RAÍZ de la carpeta de la materia (`.../[Año]/[Materia]/Materia.md`), fuera de la carpeta de resúmenes. Es el único archivo de estado de la materia: lo crea la IA la primera vez que se trabaja con ella y lo actualiza al cerrar cada unidad. Para empezar, copiá este archivo ahí.

## Información de cátedra
- Año o nivel: [completar]
- Docente titular o equipo: [completar]
- Sigla (dato interno para los metadatos; ya no se muestra en el documento): [completar]
- Áreas de conocimiento que aplican (ver `apoyo/estandares-por-area.md`): [completar]
- Regla de redondeo y notación de la cátedra (cifras significativas, signos, convenciones): [completar]
- Formato preferido para esta materia: [HTML completo / Hoja A4 / Diapositivas HTML / Word / preguntar cada vez]
- Modo preferido para esta materia: [extenso y explicativo / corto y rápido / preguntar cada vez]
- Índice preferido (solo HTML completo u Hoja A4, modo extenso): [sí / no / preguntar cada vez]
- ¿Se imprime o es solo digital? (imprime = márgenes espejados; digital = `-M espejo=false` o `--sin-espejo`): [se imprime / solo digital / preguntar cada vez]
- ¿HTML y MD en una carpeta aparte y los PDF afuera, o todo junto?: [aparte / todo junto / preguntar cada vez]
- Selección múltiple con nota parcial en los cuestionarios: [sí / no]

## Fuente (resuelta y confirmada con el usuario el [fecha])
Carpeta base: `[carpeta raíz de la universidad]/[Año]/[Materia]/`
- Programa: [subcarpeta o archivo]
- Teoría: [subcarpeta]
- Práctica: [subcarpeta]
- Parciales viejos (fuente para el cuestionario de nivel parcial): [subcarpeta]
- Fuera de alcance (no es fuente válida): [subcarpetas propias o viejas del usuario]

## Carpetas de salida
Base: `[carpeta raíz de la universidad]/[Año]/[Materia]/` (nombres en `configuracion/proyecto.md`, orden en `INSTRUCCIONES.md`, «Fuentes y salidas»):
- `Resúmenes/`: los `.pdf` de cada resumen (y todo, si se eligió «todo junto»).
- `Resúmenes/HTML y MD/`: los `.html` y los `.md` (si se eligió carpeta aparte).
- `Resúmenes/Figuras/`: figuras y diagramas finales; el `.md` las cita con ruta relativa.
- `Cuestionarios/`: `.json` y `.html` de los cuestionarios.
- `Parciales digitalizados/`, `Parciales para practicar/` y `TPs/`: se crean la primera vez que se usan.

Nombres con `sistema-visual/herramientas/nombres.py`, por ejemplo `Materia ｜ Resumen꞉ Unidad 1 a 4 ｜ corto.md` y `… ｜ corto ｜ hoja A4.html` o `.pdf`.

## Cobertura por unidad
| Unidad | Tema | Fuente disponible | Modo | Formato | Resumen (archivo) | Verificado | Agregados propios |
|--------|------|-------------------|------|---------|-------------------|------------|-------------------|

Agregados propios: lista breve de lo que el resumen extenso dice y no viene de la fuente (sección y una línea de qué es), con el estado de su verificación contra fuentes confiables. Vacía si no hay.

## Ambigüedades o contradicciones de la fuente
- (unidad, lugar, qué dice la fuente; nunca se resuelven en silencio)

## Debilidades y notas
-

## Jerarquía de fuentes (hereda de INSTRUCCIONES.md)
Nunca se escribe ni se modifica nada en las subcarpetas de fuente. En el modo extenso se puede reformular y completar con conocimiento propio cuando la fuente es escueta, sin inventar ni dejar afirmaciones sin sustento; el documento no lleva comentarios metatextuales y lo que no viene de la fuente se lista arriba, en «Agregados propios», para verificarlo contra fuentes confiables.
