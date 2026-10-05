# Guía: generar .docx (Word) con el sistema visual v4

Genera un `.docx` para todos los tipos de documento (TP, resumen extenso o corto, parcial digitalizado o modelo de práctica, hojas de soluciones de resultados y de resolución) con el mismo Markdown que alimenta el HTML. Markdown → Word con `sistema-visual/docx/construir_docx.py` (`--tipo tp|resumen|parcial|soluciones`; Pandoc + `reference-*.docx` + filtros Lua + posproceso + fuentes incrustadas).

Todo lo que sale en HTML puede salir también en Word, con el mismo Markdown y el mismo lenguaje visual: resumen extenso y corto (no diapositivas), parcial digitalizado, modelo de práctica, soluciones y TP. Formularios y hojas puntuales **no** son un tipo: si se repite algo así, cuenta como un resumen. Cuerpo de 12 pt (Alegreya Sans incrustada) en todos los tipos.

## Comando (siempre este, nunca Pandoc suelto)
Desde la raíz del proyecto:
```
python sistema-visual/docx/construir_docx.py "<Nombre>.md" --tipo resumen --modo extenso|corto [--indice] [--practica] [--sin-espejo] -o "<Nombre>.docx" --chequeo
python sistema-visual/docx/construir_docx.py "<Parcial>.md" --tipo parcial [--sin-espejo] -o "<Parcial>.docx"
python sistema-visual/docx/construir_docx.py "<Soluciones>.md" --tipo soluciones [--sin-espejo] -o "<Soluciones>.docx"
python sistema-visual/docx/construir_docx.py "<TP>.md" --tipo tp --datos "<TP>.json" [--sin-espejo] -o "<TP>.docx" --chequeo
```
- **Antes de generar, preguntar «¿se imprime o es solo digital?»** (se reutiliza lo ya indicado para la materia). Imprime = márgenes espejados a doble faz, como siempre. Solo digital (por ejemplo un TP que va por el aula virtual) = `--sin-espejo`: márgenes iguales en todas las hojas (izquierdo 20 mm, derecho 10, superior 15, inferior 5, sin `w:mirrorMargins` ni `w:evenAndOddHeaders`), «Hoja n de N» siempre a la derecha y el texto de cabeza (sección, trabajo, o materia y tema) a la izquierda.
- `--tipo`: `tp` (por defecto), `resumen`, `parcial` (también modelo de práctica) o `soluciones` (hoja de resultados o de resolución).
- `--modo`: solo resumen; el corto no lleva síntesis, glosario, demostraciones ni índice. `--indice`: índice simple (sin enlaces) en el resumen extenso. `--practica`: activa `practica: true` (previas y «Probá sin mirar», marcados como material de práctica).
- `--datos` (JSON): en `tp`, la carátula y la cabeza (ver «Carátula»); en los demás, opcional: `{"cabecera": {"materia": "...", "tema": "..."}}`. Sin `--datos`, materia y tema salen del encabezado YAML del `.md` (el mismo del HTML).
- `--referencia` regenera los tres `reference-*.docx` (también lo hace `python construir.py`).
- Requisitos: Pandoc, un navegador (pasa los SVG a PNG), `pip install lxml fonttools pillow pymupdf`.
- Los archivos de trabajo (PNG de figuras, fuentes renombradas) van a una carpeta temporal que se borra. En la carpeta de la persona queda solo el `.docx` final.

## Qué traduce cada tipo (los mismos marcadores que el HTML)
**Resumen** (`docx-resumen.lua`, sangría de 1,3 cm donde cuelgan números, rótulos y aspas): encabezado «Materia | Unidad N» solo en la primera hoja; `#` apertura con numeral azul grande y filete grueso (desde la segunda unidad, hoja nueva); `##` numerado 3.1 con número azul colgado; `###` sin número; `::: definicion/ejemplo/propiedad/demostracion` con rótulo en línea «Definición 3.1 (...).»; `::: resolucion` abierta («Resolución.»); `::: clave` (único recuadro); `::: ecuacion` nativa centrada con «(3.1)» a la derecha; `::: sintesis` con filete y rótulo colgado; `::: errores` y `::: ojo` con aspa roja colgada y la palabra; `::: margen` y `^[nota]`; figuras y tablas numeradas «Figura 3-1.» y «Tabla 3-1.»; `::: glosario`; `::: hoja-aparte`; referencias `[](#id)` en azul; práctica marcada como material de práctica.
**Parcial** (`docx-material.lua`): `::: cabecera-original` fiel (título y filete; sin los renglones de legajo, apellido y nombre y curso ni la fecha), `::: consigna`, `::: ejercicio n= espacio=` con el número colgado y el espacio en blanco sin líneas (párrafo vacío de alto exacto), incisos, `::: datos`, figuras. **Soluciones**: `::: resultado` (verde, «Resultado.»), `::: supuesto`, `::: errata` (rojo, «Errata.»), `::: subtitulo`, `::: tabla-resultados`.

## Decisiones de Word que no tienen equivalente directo en HTML
- **Notas al margen y epígrafes de figuras**: Word no tiene columna de margen. Cada nota (o figura) va en una **tabla invisible de dos columnas** (cuerpo 72 % | nota 28 %, con 0,5 cm de hueco), una sola fila que no se parte entre hojas: la nota nunca queda en otra hoja que su párrafo, y el epígrafe queda al costado de la figura, alineado abajo. Es el mismo esquema del HTML (120 mm + 44 mm) y es más estable que una nota al pie, que separaría la nota del párrafo.
- **Figuras**: los SVG del Markdown se pasan a **PNG de 2400 px de ancho** (unos 500 ppp) con navegador sin interfaz, con la letra y los colores de la página; Word no dibuja bien SVG con CSS (`currentColor`, clases). El Markdown no cambia: sigue apuntando al `.svg`.
- **Plegables**: `resolucion` y `demostracion` salen abiertas, como en impresión.
- **Sección vigente en la cabeza de hoja**: campo `STYLEREF TituloSec`; el texto de cada título de unidad o sección lleva ese estilo de carácter. La primera hoja no la lleva (como la A4). Word lo calcula al abrir; otros lectores pueden mostrarlo vacío.
- **Rótulo tipo plano del material**: una sola línea en la **cabecera** de la sección, en el margen superior: «materia | tema» del lado interior y «Hoja n de N» del exterior (marcador `ROT_LINEA` que reemplaza el posproceso). Sin pie: el área de texto ocupa toda la hoja. Sin datos personales ni fecha.
- **Ejercicios**: tabla de dos columnas («1)» | contenido) con la fila sin partir cuando hay espacio para responder (equivale a `break-inside: avoid`). En las hojas de soluciones un ejercicio muy largo puede partirse entre dos hojas.
- **Índice**: lista simple, sin enlaces ni números de página.

## Identidad v4 en Word
- Letra: Alegreya Sans en todo, incrustada como familia «Estudio Sans» (copia con cifras de caja alta de `sistema-visual/fonts/graficos`, renombrada); «Estudio Marcas» (subconjunto con el aspa, el visto y el asterisco) y Noto Sans Math para las fórmulas. Cuerpo 12 pt; resumen 1,38 de interlineado, títulos 25 (apertura), 14,4 y 12 pt; notas, epígrafes y tablas 9,5 pt.
- Fórmulas nativas de Word (OMML) en letra recta, cocientes siempre apilados (`\frac`, `\dfrac`, nunca `a/b`; unidades `\frac{\text{m}}{\text{s}}`; decimales `1{,}96`). Los operadores los dibuja Word con Cambria Math (Word no toma como fuente matemática una fuente solo incrustada).
- Color: tinta `#1D1F23`; azul `#1C3F94` solo en números y referencias; rojo solo en el aspa de error y en «Errata», siempre con la palabra; verde solo en «Resultado». Sin cajas de colores (la única caja es la fórmula clave, en tinta), sin mayúsculas espaciadas, sin fondos en la cabecera de tabla.
- **Formato base de lo imprimible** (igual que los TP y la Hoja A4): texto justificado y sin guionado (`sin_guiones`), estilo de tabla `Table` con línea vertical entre columnas y leyenda de los gráficos debajo del área de trazado. Vale para resumen, parcial (contenido fiel al original, con este formato), soluciones y TP.
- Márgenes de carpeta (de `sistema-visual/css/tokens.css`): A4 doble faz espejada (`w:mirrorMargins`; con `--sin-espejo`, iguales en todas las hojas), interior 2,0 cm, exterior 1,0, superior 1,5, inferior 0,5. La cabeza de hoja empieza a 7 mm del borde (`MARGEN["cab"]` = 0,7 cm en `construir_docx.py`, `w:header`; su línea de texto queda a unos 10 mm, parecida al HTML), distinta en pares e impares: «Hoja n de N» del lado exterior; del lado interior el trabajo (tp) o la sección vigente (resumen); el material, «materia | tema» (el rótulo). **Sin sigla ni unidad** en la cabecera de resúmenes y TP (la unidad va en el encabezado de la primera hoja). Los filetes de párrafo y de tabla entran unos décimos de milímetro porque Word los dibuja medio trazo hacia afuera.

## Carátula del TP
Campos y orden por defecto: «Trabajo Práctico de laboratorio N°» (número en azul), título del práctico, «Materia:», «Año:», «Curso:» y una **tabla de integrantes** con las columnas «Apellido y nombre» y «Legajo», una fila por integrante (sin límite fijo), cargada desde `integrantes`; sin la lista, dos filas vacías para completar. Campo vacío = renglón para completar. Nunca inventar datos personales. Los integrantes los pasa la persona en cada TP por el chat: **no se guardan en ningún archivo del proyecto ni en la memoria de la IA**; las demos usan «Apellido Nombre» y legajos falsos (00000). Igual en el HTML A4 (`tp.lua`, `tp-a4.css`). Si la cátedra exige otro modelo de carátula, el nombre de la columna de identificación se cambia con `"rotulo_id"` dentro de `caratula` (por defecto «Legajo»; por ejemplo «Matrícula»), y los demás rótulos fijos («Materia:», «Año:», «Curso:») están en `construir_docx.py` (Word) y `incluir/tp.lua` (HTML A4); se adaptan ahí. JSON:
```json
{"caratula": {"encabezado": "Trabajo Práctico de laboratorio", "numero": "4",
              "titulo": "Título del trabajo", "materia": "Materia A", "anio": "2026",
              "curso": "", "institucion": [], "extra": [], "logo": "",
              "integrantes": [{"nombre": "Apellido Nombre", "legajo": "00000"}]},
 "cabecera": {"materia": "Materia A", "trabajo": "Trabajo Práctico N° 4"}}
```
`institucion` (opcional, arriba de todo) y `extra` (`[["Fecha de entrega", "..."]]`) solo si la persona los pide. `logo` es la ruta de un PNG (opcional). Estándar de TP: `flujos/tp.md`.

## Bugs de Word ya conocidos
1. **Nunca la lista de definición nativa**: el estilo `Definition` no aplica su sangría.
2. **La familia se fija en `docDefaults`, en cada estilo y en el tema** (Aptos por defecto). Nunca Arial.
3. **Formato condicional de tabla** (`tblStylePr firstRow`): la negrita cascadea, el centrado no.
4. **`w:caps` rompe el autoajuste de columnas**: el posproceso lo quita (y la v4 no usa mayúsculas).
5. **Autoajuste de tablas**: el posproceso fija el ancho de columnas (tablas de datos: según el texto; de diseño: fracciones fijas) y `tblLayout`.
6. **Filas partidas entre hojas**: `w:cantSplit` en cada fila (salvo las hojas de soluciones, cuyos ejercicios largos pueden partirse).
7. **Pandoc no copia `m:mathPr`** (sin eso Word usa Cambria Math): el posproceso lo agrega.
8. **Filetes medio trazo hacia afuera**: párrafos y tablas con filete entran 0,07 cm.
9. **Nombre de estilo = id**: Pandoc busca el estilo por nombre; si no coincide con el de `reference-*.docx` crea uno duplicado con la herencia equivocada.
10. **`Plain` dentro de un Div con estilo sale como «Compact»**: los filtros pasan todo a `Para`.
11. **Continuación de un ítem de lista dentro de un Div con estilo**: Pandoc le pone viñeta (`numId` 1000); el posproceso la quita y la sangra.
12. **Tablas anidadas se corren a la derecha** (el rótulo del material es una línea de cabecera, no una tabla). La tabla de integrantes de la carátula entra 120 twips para que su filete no invada el margen interior.
13. **Aspa en una fuente de símbolos**: sus métricas de línea agrandan el renglón; el subconjunto incrustado copia las de Alegreya.
14. **`Quit(0)` de Word por COM falla**: `captura_docx.py` usa `Quit([ref]$sc)`; si una sesión deja un WINWORD abierto, cerrarlo (solo el que se lanzó).
15. **Versiones de Pandoc**: el filtro `docx-comun.lua` arma las tablas con `pandoc.TableBody` si existe y con una tabla equivalente si no, para funcionar en versiones distintas.

## Verificación antes de entregar
- `--chequeo` (fórmulas, corridas sin letra recta, cocientes apilados, fuentes incrustadas, Arial, `w:caps`).
- Mirarlo de verdad: `python sistema-visual/herramientas/captura_docx.py "<Nombre>.docx" <carpeta> --pdf <pdf>` exporta a PDF (con Word sin interfaz en Windows si está instalado; si no, con LibreOffice sin interfaz) y saca un PNG por hoja. En el PDF exportado por Word, la lista de fuentes muestra `___WRD_EMBED_SUB` si Word usó la letra incrustada. Después `python sistema-visual/herramientas/verificar_margenes.py <pdf>` mide los márgenes. PDF y capturas al directorio temporal, no a la carpeta de la persona.
- `python sistema-visual/herramientas/verificar_reglas.py`: la regla 22 mide los PDF de `docx/demo/` y la regla 36 revisa fuentes, 12 pt, marcadores crudos de Pandoc (`:::`, `{#`), componentes traducidos y cabecera sin sigla ni unidad.
- Demostraciones en `sistema-visual/docx/demo/`: `tp-demo` y, generadas por `construir.py`, `resumen-extenso`, `parcial` y `soluciones-resolucion` (`.docx` y su PDF).
