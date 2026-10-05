# Ayudante Universitario

Un ayudante de estudio que se adapta a cualquier carrera universitaria y funciona con cualquier modelo de IA. Crea resúmenes de unidades o de materias enteras, ayuda con trabajos prácticos, explica temas para repasar y arma cuestionarios y parciales de práctica (con o sin parte teórica), siempre a partir del material de tu cátedra y verificándolo antes de darlo por bueno.

No contiene datos de ninguna persona, materia ni trabajo realizado: es una plantilla limpia. Lo personal (tu universidad, tu carrera, tus carpetas) se completa en un único archivo, `configuracion/proyecto.md`.

## Qué produce
- **Resúmenes** en dos modos (extenso y explicativo, o corto y rápido) y cuatro formatos: HTML para leer en pantalla o celular (con modo oscuro), hoja A4 para imprimir (con PDF), diapositivas o Word.
- **Trabajos prácticos** con carátula, desarrollo, gráficos reales y cálculo verificado, en HTML, PDF o Word.
- **Explicaciones** conversacionales para repasar, sin generar archivos.
- **Cuestionarios** interactivos que se abren en el navegador, con modo práctica y modo parcial con tiempo.
- **Parciales digitalizados, modelos de práctica y soluciones** listos para imprimir.

## Cómo está organizado
| Carpeta o archivo | Para qué |
|---|---|
| `MANUAL-DE-USO.md` | Cómo estudiar con el proyecto, pedido por pedido |
| `MANUAL-DE-IMPLEMENTACION.md` | Instalación, conexión con tu IA y adaptación a tu carrera |
| `INSTRUCCIONES.md` | El núcleo que lee la IA: reglas, flujos y estilo |
| `configuracion/` | Tu único archivo personal (`proyecto.md`) y la plantilla de estado de cada materia (`Materia.md`) |
| `flujos/` | Los cuatro flujos: resumir, TP, explicar, cuestionario |
| `roles/` | Los cuatro roles: analista de fuentes, profesor, verificador, cuestionador |
| `apoyo/` | Guías de generación, de diagramas y estándares por área de conocimiento |
| `sistema-visual/` | Las herramientas que generan los documentos (Pandoc, Python, plantillas, tipografías) y su documentación |
| `adaptadores/` | Cómo conectar el proyecto con cada herramienta de IA |
| `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursor/`, `.github/` | Archivos de entrada que cada herramienta de IA reconoce; todos mandan a leer `INSTRUCCIONES.md` |

## Inicio rápido
1. Instalá Python, Pandoc y Firefox, y después `python -m pip install -r requirements.txt` (detalle en `MANUAL-DE-IMPLEMENTACION.md`).
2. Abrí tu herramienta de IA dentro de esta carpeta (si no lee archivos, `python adaptadores/adaptar.py --prompt-unico` arma un documento para pegar).
3. Pedile: «Hacé la puesta en marcha». Te pregunta por tu carrera y tus carpetas, y lo anota.
4. Empezá a pedir: «Resumí la unidad 1 de [materia] en modo extenso, en hoja A4».

## Principios
- **La fuente manda**: nada se inventa; lo que no viene de tu material se verifica en una fuente confiable y se informa aparte.
- **Tu material no se modifica**: la IA lee tus fuentes y escribe solo en carpetas de salida.
- **Independiente del modelo**: el conocimiento está en archivos de texto, no en una plataforma.
- **Limpio y portable**: funciona en Windows, macOS y Linux; ningún dato personal queda en el proyecto.

## Licencias
Las tipografías incluidas (Alegreya Sans, JetBrains Mono, Noto Sans Math y Noto Sans Symbols 2) son de código abierto con licencia SIL Open Font License 1.1; los textos de licencia están en `sistema-visual/fonts/originales/`. Paged.js y Mermaid van incrustados en archivos de `sistema-visual/` bajo sus propias licencias de código abierto. Falta definir la licencia del resto del proyecto: elegila antes de compartirlo.
