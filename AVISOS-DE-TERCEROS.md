# Avisos de componentes de terceros

Este proyecto incluye, sin modificar su licencia, los siguientes componentes. Cada uno se rige por su propia licencia, que debe conservarse al redistribuirlo.

## Tipografías (SIL Open Font License 1.1)
Los archivos originales y sus textos de licencia están en `sistema-visual/fonts/originales/`.

| Tipografía | Copyright | Uso |
|---|---|---|
| Alegreya Sans | 2013 The Alegreya Sans Project Authors (https://github.com/huertatipografica/Alegreya-Sans) | Todo el texto |
| JetBrains Mono | 2020 The JetBrains Mono Project Authors (https://github.com/JetBrains/JetBrainsMono) | Código |
| Noto Sans Math | 2022 The Noto Project Authors (https://github.com/notofonts/math) | Respaldo de fórmulas |
| Noto Sans Symbols 2 | 2022 The Noto Project Authors (https://github.com/notofonts/symbols) | Signos (✓ ✗ ✱) |

Las carpetas `sistema-visual/fonts/web/` y `sistema-visual/fonts/graficos/` contienen versiones derivadas (subconjuntos y variantes con cifras de caja alta) de esas fuentes, que siguen bajo la misma licencia OFL 1.1. Los archivos `sistema-visual/incluir/fuentes.html`, `sistema-visual/cuestionario/Plantilla-Cuestionario.html` y los documentos que el sistema genera llevan esas tipografías incrustadas en base64, también bajo OFL. Según la OFL, las fuentes no pueden venderse por sí solas; sí pueden acompañar a un documento o programa. Las copias derivadas se identifican con los nombres «Estudio Sans», «Estudio Mono», «Estudio Mate» y «Estudio Marcas», distintos de los originales.

## Paged.js (MIT)
`sistema-visual/incluir/paged-init.html` incluye Paged.js v0.4.3, © los autores de Paged.js (https://gitlab.coko.foundation/pagedjs/pagedjs), licencia MIT. El aviso de licencia está en el encabezado del propio archivo.

## Mermaid y sus dependencias (MIT y otras)
`sistema-visual/mermaid-init.html` incluye la biblioteca Mermaid (licencia MIT, https://github.com/mermaid-js/mermaid) empaquetada junto con sus dependencias, entre ellas DOMPurify (Apache 2.0 o MPL 2.0, © Cure53 y colaboradores), lodash y underscore (MIT). Los avisos de cada una están conservados dentro del archivo. Este archivo solo se agrega a un documento cuando este contiene diagramas Mermaid.

## Programas externos (no se distribuyen con el proyecto)
Se instalan aparte y se ejecutan como programas independientes; su licencia no se extiende al proyecto.
- Pandoc (GPL v2 o posterior), Python, Graphviz, PlantUML, Firefox, LibreOffice.
- Bibliotecas de Python opcionales o requeridas: PyMuPDF (AGPL v3 o licencia comercial de Artifex), NumPy, SymPy, Matplotlib, Pillow, fontTools, lxml, Docling.

Quien use el proyecto personalmente no tiene obligaciones adicionales por ellos. Quien lo integre en un servicio o producto distribuido debe revisar las condiciones de cada una, en especial la AGPL de PyMuPDF.
