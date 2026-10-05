# Permisos recomendados

La regla de fondo (ver `INSTRUCCIONES.md`, «Reglas de seguridad»): **lectura total** de la carpeta raíz de la universidad y **escritura solo** en las carpetas de salida de cada materia y en su `Materia.md`; nunca en las carpetas de fuente de la cátedra. Si tu herramienta de IA permite configurar permisos, aplicalos así. Si no lo permite, la regla igual vale: la IA la cumple por instrucción.

Reemplazá `RUTA_RAIZ` por la carpeta raíz de tu universidad (en `configuracion/proyecto.md`).

## Claude Code (`.claude/settings.json` del proyecto)
Las rutas absolutas de Claude Code empiezan con `//` (por ejemplo `//home/ana/universidad/**` o, en Windows, `//c/Users/ana/Universidad/**`).
```json
{
  "permissions": {
    "allow": [
      "Read(//RUTA_RAIZ/**)",
      "Edit(//RUTA_RAIZ/**/Resúmenes/**)",
      "Edit(//RUTA_RAIZ/**/Cuestionarios/**)",
      "Edit(//RUTA_RAIZ/**/TPs/**)",
      "Edit(//RUTA_RAIZ/**/Parciales digitalizados/**)",
      "Edit(//RUTA_RAIZ/**/Parciales para practicar/**)",
      "Edit(//RUTA_RAIZ/*/*/Materia.md)",
      "Write(//RUTA_RAIZ/**/Resúmenes/**)",
      "Write(//RUTA_RAIZ/**/Cuestionarios/**)",
      "Write(//RUTA_RAIZ/**/TPs/**)",
      "Write(//RUTA_RAIZ/**/Parciales digitalizados/**)",
      "Write(//RUTA_RAIZ/**/Parciales para practicar/**)",
      "Write(//RUTA_RAIZ/*/*/Materia.md)",
      "Bash(python:*)",
      "Bash(python3:*)",
      "Bash(pandoc:*)",
      "Bash(dot:*)"
    ],
    "deny": [
      "Read(**/.env*)",
      "Read(**/*.pem)",
      "Read(**/*.key)",
      "Edit(//RUTA_RAIZ/**/Teoría/**)",
      "Edit(//RUTA_RAIZ/**/Práctica/**)",
      "Edit(//RUTA_RAIZ/**/Programa/**)",
      "Edit(//RUTA_RAIZ/**/Material de cátedra/**)",
      "Write(//RUTA_RAIZ/**/Teoría/**)",
      "Write(//RUTA_RAIZ/**/Práctica/**)",
      "Write(//RUTA_RAIZ/**/Programa/**)",
      "Write(//RUTA_RAIZ/**/Material de cátedra/**)"
    ]
  }
}
```
No permitas de antemano `pip`, `winget`, `brew`, `apt` ni instaladores: el proyecto verifica las dependencias y pide tu permiso antes de instalar algo, y la herramienta de IA debería pedir confirmación en cada instalación. Los nombres de la lista `deny` son una red de seguridad: los nombres de las carpetas de fuente cambian de una materia a otra, así que agregá los de tu universidad. La regla de fondo sigue siendo la de `INSTRUCCIONES.md`.

## Otras herramientas
Casi todas permiten limitar en qué carpetas puede escribir el agente, o pedir confirmación antes de cada escritura. Configurá lo mismo: escritura permitida solo en las carpetas de salida; ejecución de comandos limitada a `python`, `pandoc`, `dot` y `plantuml`. Si la herramienta no distingue carpetas, dejá activada la confirmación manual de escrituras y revisá cada ruta antes de aceptar.
