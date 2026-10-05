# Adaptadores: usar el proyecto con cualquier IA

El proyecto no depende de ningún modelo ni empresa: todo el conocimiento está en archivos Markdown (`INSTRUCCIONES.md`, `flujos/`, `roles/`, `apoyo/`) y las herramientas de generación son programas comunes (Python, Pandoc y el navegador que ya uses: Firefox, Chrome, Edge, Brave...). Lo único que cambia de una IA a otra es **cómo se entera de que esas instrucciones existen**. Esa es la tarea de esta carpeta.

## Qué hay en la raíz del proyecto
El texto de entrada vive **una sola vez**, en `AGENTS.md`: un mensaje corto que manda a leer `INSTRUCCIONES.md`. Los demás archivos no lo repiten:

| Archivo | Lo lee | Contenido |
|---|---|---|
| `AGENTS.md` | Codex CLI (OpenAI), Cursor, GitHub Copilot (agente), Jules, Aider, Windsurf y otras herramientas que adoptaron esa convención | El texto de entrada |
| `CLAUDE.md` | Claude Code (Anthropic) | Una línea, `@AGENTS.md`, que importa el archivo anterior |
| `GEMINI.md` | Gemini CLI (Google) | Una línea, `@AGENTS.md`, que importa el archivo anterior |
| `.claude/commands/` | Claude Code | Los comandos `/resumir`, `/tp`, `/explicar` y `/cuestionario` (cada uno apunta a su flujo, sin copiar texto) |

Para otras herramientas que necesiten su propio archivo (por ejemplo, GitHub Copilot en el chat de algunas versiones usa `.github/copilot-instructions.md`; Cursor tiene reglas en `.cursor/rules/`; Windsurf y Cline tienen las suyas), generalo con `python adaptadores/adaptar.py --herramienta copilot` (o `cursor`, `windsurf`, `cline`). `python adaptadores/adaptar.py --lista` muestra todas. Las convenciones de nombres las definen las empresas y cambian; si la tuya pide otro archivo, copiale el texto de `AGENTS.md`.

Podés borrar `CLAUDE.md` o `GEMINI.md` si no usás esas herramientas: no afecta a nada.

## Si tu IA no lee archivos del disco
Hay tres situaciones, de mejor a peor:

1. **Chat con proyectos o con instrucciones personalizadas** (por ejemplo, los «proyectos» de un asistente web, los GPT personalizados, los Gems o las «Spaces»). Corré `python adaptadores/adaptar.py --prompt-unico`: crea `trabajo/prompt-completo.md` (todo el proyecto en un solo documento, unos 40.000 tokens) y `--prompt-unico --sin-apoyo` crea `trabajo/prompt-corto.md` (unos 25.000 tokens). Pegá uno de los dos en las instrucciones del proyecto, o subilo como archivo de conocimiento. Si el modelo tiene una ventana de contexto chica, usá la versión corta y pegá la guía de apoyo que haga falta en el momento.
2. **Modelo local** (Ollama, LM Studio, llama.cpp, Open WebUI, etc.). Mismo procedimiento que el punto 1, pegado en el «prompt del sistema». Los modelos chicos (menos de unos 30.000 tokens de contexto) no van a poder con el proyecto completo: usá el modo reducido de `MANUAL-DE-IMPLEMENTACION.md`.
3. **Solo API, sin interfaz**. Cargá `trabajo/prompt-completo.md` como mensaje de sistema. Para que el modelo lea y escriba archivos y ejecute comandos, necesitás un agente que le dé esas herramientas (cualquiera de las de la tabla de arriba, o el tuyo propio); sin eso, funciona en modo reducido.

## Lo que la IA necesita poder hacer
Para el uso completo, la herramienta tiene que poder: leer archivos de tu carpeta de la universidad, escribir archivos en las carpetas de salida, ejecutar comandos de terminal (Python, Pandoc) y, para verificar, mirar imágenes. Buscar en la web es opcional (sirve para verificar los agregados propios). Sin ejecución de comandos, ver «Modo reducido» en `MANUAL-DE-IMPLEMENTACION.md`. Los permisos recomendados están en `permisos-ejemplo.md`.

## Roles y subagentes
Si la herramienta soporta subagentes, cada archivo de `roles/` puede ser uno (en Claude Code, por ejemplo, copiándolo a `.claude/agents/` con un encabezado `name` y `description`). Si no, la IA cumple los roles en pasos separados dentro de una misma conversación. El diseño funciona de las dos maneras.
