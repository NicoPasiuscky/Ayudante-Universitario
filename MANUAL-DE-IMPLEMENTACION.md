# Manual de implementación

Cómo instalar el Ayudante Universitario, conectarlo con la IA que elijas y adaptarlo a tu carrera. Si ya está instalado y solo querés usarlo, andá a `MANUAL-DE-USO.md`.

El manual está ordenado como se hace: primero qué necesitás, después la instalación, la conexión con la IA, la adaptación a tu carrera, la verificación y, al final, qué hacer si algo falla.

## 1. Qué necesitás

### Una IA con ciertas capacidades
El proyecto funciona con cualquier modelo de cualquier empresa, siempre que cumpla esto. No hay un modelo obligatorio ni uno «recomendado por marca»: lo que importa son las capacidades.

| Capacidad | Para qué | Si falta |
|---|---|---|
| Contexto largo (al menos unos 32.000 tokens; mejor 100.000 o más) | Leer las instrucciones y una unidad de fuente a la vez | Usar el modo reducido (sección 7) |
| Seguir instrucciones largas y precisas | Cumplir las reglas del proyecto sin que se las recuerdes | Resultados irregulares: probá un modelo más capaz |
| Leer y escribir archivos, y ejecutar comandos (herramienta de tipo «agente») | Leer tu carpeta de la universidad y generar los documentos | Modo reducido: vos copiás y convertís |
| Ver imágenes | Verificar gráficos y documentos | Podés verificar vos mirando los archivos |
| Buscar en la web (opcional) | Verificar los agregados propios contra fuentes confiables | La IA verifica con conocimiento propio y te lo avisa |
| Subagentes (opcional) | Que el verificador sea otro agente | La IA cumple los roles en pasos separados |

Una pauta orientativa (es una estimación, no una medición): para la conversación y la mayoría de los roles alcanza un modelo de gama media; para verificar y para resolver TP de cálculo conviene el más capaz que tengas a mano. Probá con tu material real y fijate si las unidades salen bien verificadas.

### Programas en tu computadora
| Programa | Versión | Para qué | Sin él |
|---|---|---|---|
| Python | 3.10 o superior | Todas las herramientas | No funciona nada de la generación |
| Pandoc | 3.8 o superior | Markdown a HTML y Word | No hay documentos |
| Un navegador: Firefox, Chrome, Edge, Brave, Chromium u otro basado en Chromium | reciente | PDF de la Hoja A4, capturas, medidas, figuras del Word | Solo HTML y diapositivas; sin PDF ni Word con figuras |
| Bibliotecas de Python | ver `requirements.txt` | PDF, cálculo, gráficos, Word | Funciones parciales |
| Graphviz | cualquiera | Diagramas grandes | Se usan SVG a mano |
| Java + `plantuml.jar` | Java 11 o superior | Diagramas UML formales | Se usan SVG a mano |
| Word o LibreOffice | cualquiera | Revisar los `.docx` de verdad | Revisás el `.docx` abriéndolo vos |

Funciona en Windows, macOS y Linux. Los comandos de este manual usan `python`; en macOS y Linux suele ser `python3`.

## 2. Instalación paso a paso

### 2.1 Obtener el proyecto
Descargá o cloná el repositorio en una carpeta tuya (no hace falta que sea la de tu universidad; son cosas distintas: el proyecto son las herramientas y tu carpeta de la universidad es el material). Ejemplo: `~/Ayudante-Universitario`.

### 2.2 Instalar los programas
**Windows** (en PowerShell, con permisos normales):
```
winget install --id Python.Python.3.12 -e
winget install --id JohnMacFarlane.Pandoc -e
winget install --id Graphviz.Graphviz -e
winget install --id Microsoft.OpenJDK.21 -e
```
**macOS** (con Homebrew):
```
brew install python pandoc graphviz openjdk
```
**Linux (Debian y Ubuntu)**:
```
sudo apt install python3 python3-pip graphviz default-jre
```
**Navegador**: no hace falta instalar ninguno si ya usás Firefox, Chrome, Edge (viene con Windows), Brave u otro basado en Chromium; el proyecto detecta el que haya (sección 2.5). Si no tenés ninguno, instalá el que prefieras. Los navegadores instalados como paquete `snap` o `flatpak` a veces no permiten el modo de control remoto: si falla, instalá otra copia o definí `ESTUDIO_NAVEGADOR`. **Pandoc**: los repositorios de las distribuciones suelen traer una versión vieja (la 3.8 es el mínimo). Descargá la última desde `pandoc.org/installing.html`, o instalá la biblioteca que la trae incluida: `pip install pypandoc_binary` y después `python -c "import pypandoc; print(pypandoc.get_pandoc_path())"` te da la ruta, que guardás en `ESTUDIO_PANDOC`.

**PlantUML** (opcional): bajá `plantuml.jar` vos mismo desde la página oficial de lanzamientos de PlantUML y guardalo en una carpeta tuya; creá un acceso (`plantuml.cmd` en Windows o un script `plantuml` en macOS y Linux) que ejecute `java -jar <ruta>/plantuml.jar %*`. Es una descarga que conviene hacer a mano: no pidas que la IA baje ejecutables.

### 2.3 Instalar las bibliotecas de Python
Desde la carpeta del proyecto, cualquiera de las dos formas (ambas instalan desde PyPI, el repositorio oficial):
```
python -m pip install -r requirements.txt
python sistema-visual/estudio.py entorno --instalar-pip
```
La segunda instala solo las que falten y te pide confirmación antes.
(Opcional, para PDF escaneados: `python -m pip install docling`.)

### 2.4 Comprobar qué falta y dónde están los programas
Casi siempre se encuentran solos. Para comprobarlo:
```
python sistema-visual/estudio.py entorno
```
Muestra qué está instalado y qué falta (Python y su versión, Pandoc y su versión, navegador, bibliotecas de Python, y los opcionales). Para cada cosa que falta indica **para qué sirve, de qué fuente oficial se obtiene y con qué comando**. También se puede mirar solo lo necesario para una función: `--para html`, `--para pdf`, `--para word`, `--para graficos`, `--para diagramas` o `--para verificacion`.

**El proyecto no instala nada por su cuenta.** Si falta algo, te lo dice y vos decidís. Las únicas instalaciones que puede hacer, y solo si lo autorizás, son las bibliotecas de Python desde PyPI (el repositorio oficial): `python sistema-visual/estudio.py entorno --instalar-pip` te pide confirmación antes de instalar. Los programas del sistema (Pandoc, navegador, Graphviz, Java, LibreOffice) se instalan con los comandos o las páginas oficiales que el informe muestra, ya sea por vos o por tu asistente de IA con tu permiso explícito. Los comandos de generación (`estudio.py resumen`, `docx`, etc.) y `construir.py` hacen esta comprobación al empezar y se detienen con un mensaje claro si falta algo obligatorio.

Si algo aparece como faltante pero sí está instalado en un lugar poco común, definí la variable de entorno que corresponde, con la ruta completa del programa:
- `ESTUDIO_PANDOC` para Pandoc
- `ESTUDIO_NAVEGADOR` para el navegador (ruta completa, o el nombre si está en el PATH)
- `ESTUDIO_SOFFICE` para LibreOffice

En Windows: `setx ESTUDIO_PANDOC "C:\ruta\pandoc.exe"` y abrir una terminal nueva. En macOS y Linux: agregar `export ESTUDIO_PANDOC=/ruta/pandoc` al perfil de tu terminal.

### 2.5 Qué navegadores sirven
El proyecto usa un navegador sin interfaz para cuatro tareas: sacar el PDF de la Hoja A4, tomar capturas, medir las páginas (las reglas de verificación) y dibujar los gráficos de los `.docx`. Funciona con:

| Navegador | Cómo se controla | Estado |
|---|---|---|
| Firefox | Protocolo Marionette | Probado |
| Chrome, Chromium, Edge, Brave, Opera, Vivaldi y otros basados en Chromium | Protocolo de depuración remota (CDP), con un cliente propio: no hay que instalar nada más | Probado con Chromium |
| Safari, GNOME Web, Orion y otros sin modo sin interfaz | No se pueden automatizar | No compatibles para PDF y capturas |

La elección es automática: si hay Firefox, lo usa; si no, el primer navegador basado en Chromium que encuentre (Chrome, Chromium, Edge, Brave, Opera, Vivaldi). Para forzar uno, definí `ESTUDIO_NAVEGADOR` con su ruta o su nombre. Comprobación rápida: `python sistema-visual/herramientas/navegador.py` abre el navegador elegido, carga una página y muestra si pudo medirla, capturarla e imprimirla. Con Safari o sin ningún navegador automatizable seguís pudiendo generar y leer los HTML (se ven en cualquier navegador moderno), y el PDF se saca a mano con Imprimir; solo las reglas de medidas de `verificar_reglas.py` quedan «sin medir».

Una diferencia a tener en cuenta: cada motor dibuja con pequeñas diferencias (décimas de milímetro). Las reglas de márgenes y de ancho de texto se calibraron con Firefox; con otro motor un valor puede quedar justo en el límite.

## 3. Conectar el proyecto con tu IA
Detalle completo en `adaptadores/LEEME.md`. En resumen:
1. Abrí tu herramienta de IA **dentro de la carpeta del proyecto** (para que vea los archivos). Los archivos de entrada ya vienen creados: `AGENTS.md` (lo leen Codex, Cursor, Copilot, Windsurf y muchas más), `CLAUDE.md` y `GEMINI.md` (que solo importan `AGENTS.md`). Para una herramienta que necesite un archivo propio: `python adaptadores/adaptar.py --lista`.
2. Si tu IA no lee archivos del disco, generá el documento único: `python adaptadores/adaptar.py --prompt-unico` y pegá `trabajo/prompt-completo.md` en las instrucciones del proyecto o del sistema.
3. Configurá los permisos según `adaptadores/permisos-ejemplo.md` (lectura de tu carpeta de la universidad; escritura solo en las carpetas de salida).
4. Probá con un pedido corto: «Leé `INSTRUCCIONES.md` y decime qué flujos tenés». Tiene que nombrar resumir, TP, explicar y cuestionario.

## 4. Puesta en marcha con tu carrera
Completá `configuracion/proyecto.md` (o pedile a la IA «hacé la puesta en marcha» y respondé sus preguntas). Lo que define:
- **Tu universidad y tu carrera**, el plan y el año que cursás.
- **El idioma y la variante** de los documentos (por defecto, español rioplatense; cambialo si querés otra variante). Para otro idioma completo, pedile a la IA que traduzca los textos fijos que se ven en los documentos: rótulos del filtro `estudio.lua` («Definición», «Síntesis», «Hoja»), de `material.lua` y de `tp.lua`, y las frases de la interfaz de `cuestionario/plantilla-fuente.html`; después corré `python sistema-visual/construir.py`.
- **Dónde está tu material**: la carpeta raíz y cómo está organizada.
- **Tus áreas de conocimiento**: marcá las que usa tu carrera. Si falta alguna, ver 4.2.
- **Tus preferencias**: formato, modo, índice y si imprimís.

La primera vez que trabajes con una materia, la IA te va a pedir que confirmes cuáles son sus carpetas de fuente y de salida, y va a crear el `Materia.md` de esa materia en su carpeta.

### 4.1 Cómo se adapta a cualquier carrera
El sistema separa tres cosas:
1. **Reglas de proceso** (`INSTRUCCIONES.md`, `flujos/`, `roles/`): valen para cualquier carrera, porque tratan de cómo se trabaja con una fuente (leerla, resumirla fiel, verificarla), no de qué dice.
2. **Estándares de área** (`apoyo/estandares-por-area.md`): cómo se plantea y se presenta el contenido en cada disciplina (cálculo, programación, derecho, salud, humanidades, etc.).
3. **Tu contexto** (`configuracion/proyecto.md` y cada `Materia.md`): lo único personal.

Para una carrera de ciencias duras vas a usar a fondo los gráficos, las fórmulas y los TP con cálculo. Para una carrera de humanidades o derecho, los flujos de resumir, explicar y cuestionario funcionan igual, con tablas comparativas, líneas de tiempo y citas en lugar de fórmulas; los TP salen como informes de texto con la carátula. No hace falta tocar código en ningún caso.

### 4.2 Sumar un área de conocimiento
Pedile a la IA: «Agregá a `apoyo/estandares-por-area.md` el área de [tu área], siguiendo el formato de las demás». Después marcala en `configuracion/proyecto.md`. Los estándares son criterios de rigor y presentación, no datos de la disciplina: revisá que describan cómo se trabaja en tu cátedra.

### 4.3 Otras adaptaciones habituales
| Quiero... | Dónde |
|---|---|
| Otros márgenes de impresión | `sistema-visual/css/tokens.css` (`--hoja-*`) y la copia de `incluir/espejo.lua`; después `python sistema-visual/construir.py` |
| Otra carátula de TP (otros campos, «Matrícula» en vez de «Legajo») | JSON del TP: `rotulo_id`, `extra`, `institucion`, `logo`; rótulos fijos en `docx/construir_docx.py` y `incluir/tp.lua` |
| Logo de mi facultad en los TP | `caratula.logo` del JSON (ruta de un PNG) |
| Otros colores o tipografía | `sistema-visual/css/tokens.css` y `tokens-oscuro.css`; la tipografía se regenera con `python sistema-visual/construir.py --fuentes` |
| Otro separador en los nombres de archivo (en macOS y Linux sirven `|` y `:`) | Dos constantes al inicio de `herramientas/nombres.py` |
| Otros nombres de carpetas de salida | `configuracion/proyecto.md` |
| Cambiar cómo se redacta (más corto, otro tono) | `INSTRUCCIONES.md`, sección «Estilo y tono», y `roles/profesor.md` |

Regla de oro para cualquier cambio de reglas: se escribe en estos archivos, no solo en la memoria de la herramienta de IA, así vale con cualquier modelo y viaja con el proyecto.

### 4.4 IAs complementarias (opcional)
Si querés repartir el trabajo entre varias IAs (Codex para verificar, Gemini para leer fuentes y derivar resúmenes cortos), la IA te lo explica una vez al final de la puesta en marcha y no activa nada sin tu decisión. Qué es, qué implica (el contenido viaja a servidores de terceros, cuentas y cupos propios), cómo se prepara y cómo se decide: `apoyo/ias-complementarias.md`. Comprobar qué hay instalado: `python sistema-visual/estudio.py entorno --para ias` (no instala nada). Si no la querés, no tenés que hacer nada: el proyecto funciona completo sin ella.

## 5. Verificar la instalación
1. `python sistema-visual/estudio.py entorno`: Python y Pandoc tienen que aparecer; también un navegador, si querés PDF y Word.
2. Generar un documento de prueba, con el contenido de demostración incluido:
   ```
   python sistema-visual/estudio.py resumen sistema-visual/demo/resumen-corto.md --formato completo --modo corto --carpeta trabajo/prueba
   ```
   Abrí el `.html` que crea en `trabajo/prueba/`: tiene que verse un resumen con fórmulas, tablas y botón «Modo oscuro».
3. Prueba completa del sistema (necesita un navegador, tarda unos minutos):
   ```
   python sistema-visual/construir.py
   ```
   Regenera todas las demostraciones y corre las reglas de verificación. Si termina sin errores, el sistema está listo. Genera `sistema-visual/indice.html`, una muestra de todo lo que sabe hacer.
4. Generar un PDF de prueba: `python sistema-visual/estudio.py resumen sistema-visual/demo/resumen-extenso.md --formato a4 --modo extenso --salida pdf --carpeta trabajo/prueba`.

Los archivos de `trabajo/` y las demostraciones generadas no se suben al repositorio (están en `.gitignore`).

## 6. Mantenimiento
- **Actualizar el proyecto**: reemplazá los archivos por los de la versión nueva, salvo `configuracion/proyecto.md`, que es tuyo. Si compartís el proyecto, no incluyas tu `proyecto.md` completado.
- **Tus datos viven fuera del proyecto**: tus resúmenes, TP y cuestionarios se guardan en tu carpeta de la universidad, no acá. Los `Materia.md` también.
- **Privacidad**: el proyecto no guarda nombre ni legajo de nadie. Si lo compartís o lo subís a un repositorio, revisá `configuracion/proyecto.md` (es el único archivo con datos tuyos) y que `trabajo/` no se suba.
- **Cambiar de IA**: nada que hacer más que conectar la nueva (sección 3). El estado está en los archivos, no en la herramienta.

## 7. Modo reducido (IA sin archivos, sin comandos o con poco contexto)
Si la IA solo conversa:
1. Pegá el contenido de `INSTRUCCIONES.md` (o `trabajo/prompt-corto.md`) como instrucciones y la parte de `flujos/` que corresponde al pedido.
2. Pegá o adjuntá el texto de la fuente (una unidad por vez).
3. La IA te devuelve el Markdown del resumen siguiendo `roles/profesor.md`. Guardalo como `unidad.md` en una carpeta.
4. Convertilo vos con una línea:
   `python sistema-visual/estudio.py resumen unidad.md --formato a4 --modo extenso --salida html+pdf --carpeta salida`
5. La verificación la hacés pidiéndole a la IA, en una conversación nueva, que actúe como el rol de `roles/verificador.md` contra el mismo texto de la fuente.
Es más manual, pero produce los mismos documentos.

## 8. Si algo falla
| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `No se encontro ningun navegador compatible` | Ninguno instalado o en un lugar raro | Instalar uno o definir `ESTUDIO_NAVEGADOR` |
| `El navegador no respondio (protocolo de depuracion)` | Navegador empaquetado como snap o flatpak, o una opción de empresa que bloquea el control remoto | Probar con otro navegador (`ESTUDIO_NAVEGADOR`) |
| Algún valor de las reglas de medidas queda justo en el límite | Cada motor dibuja con diferencias de décimas | Repetir con el otro motor; la medida de referencia fue Firefox |
| `Unknown option --math-method` | Pandoc viejo | El sistema ya elige `--mathml`; si falla otra opción, actualizar Pandoc a 3.8 o más |
| `Unknown option --syntax-highlighting` | Pandoc anterior a 3.8 | Actualizar Pandoc |
| `attempt to call a nil value (field 'TableBody')` | Pandoc muy viejo en el filtro de Word | Actualizar Pandoc |
| Las fórmulas salen vacías | Se usó MathJax o falta MathML | Usar siempre las opciones del proyecto |
| El PDF sale con una sola hoja o sin hojas | Paged.js no terminó de paginar | Repetir; si pasa siempre, mirar el HTML en el navegador y la consola |
| `UnicodeEncodeError` en Windows | Consola con codificación vieja | Los scripts del proyecto ya escriben en UTF-8; si lo ves en un script tuyo, escribir a archivo, no a la consola |
| La IA escribe en la carpeta de fuente | Permisos mal puestos | Revisar `adaptadores/permisos-ejemplo.md` y `INSTRUCCIONES.md`; pedirle que lea esa regla |
| La IA inventa datos | Fuente no leída o contexto lleno | Pedirle que cite el pasaje de la fuente; trabajar de a una unidad |
| El proyecto «no se entera» de las reglas | La IA no cargó el archivo de instrucciones | Pedirle «leé `INSTRUCCIONES.md`»; ver `adaptadores/LEEME.md` |
| `soffice` no encontrado al revisar un `.docx` | Sin Word ni LibreOffice | Abrir el `.docx` a mano o instalar LibreOffice |
| Error al leer o escribir un archivo | Ruta con espacios sin comillas | Poner las rutas entre comillas |
