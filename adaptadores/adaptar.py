#!/usr/bin/env python3
"""adaptar.py - conecta el Ayudante Universitario con la herramienta de IA que uses.

El proyecto es independiente de cualquier modelo: el contenido real vive en INSTRUCCIONES.md,
flujos/, roles/ y apoyo/. Cada herramienta de IA busca sus instrucciones en un archivo con un
nombre distinto; este script crea esos archivos, todos con el mismo contenido corto que manda a
leer INSTRUCCIONES.md. Si tu herramienta no lee archivos del disco, `--prompt-unico` arma un solo
documento con todo, para pegarlo como instrucciones del sistema o del proyecto.

Uso (desde cualquier carpeta):
    python adaptadores/adaptar.py --lista                      muestra las herramientas conocidas
    python adaptadores/adaptar.py --herramienta claude         crea CLAUDE.md y los comandos /resumir, /tp...
    python adaptadores/adaptar.py --herramienta agents,gemini  varias a la vez
    python adaptadores/adaptar.py --herramienta todas          todas las conocidas
    python adaptadores/adaptar.py --prompt-unico               crea trabajo/prompt-completo.md
    python adaptadores/adaptar.py --prompt-unico --sin-apoyo   version corta (solo instrucciones, flujos y roles)

Nunca pisa un archivo que ya existe: si existe, lo deja y avisa (usa --forzar para reemplazarlo).
Las convenciones de nombres son las vigentes al escribir este script; si tu herramienta cambió la
suya, copia el contenido de `PUNTERO` al archivo que ella pida.
"""
import argparse
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True

PUNTERO = """# Ayudante Universitario

Sos el ayudante de estudio de una persona que cursa una carrera universitaria. Todas tus instrucciones
están en este proyecto, en archivos Markdown.

1. Leé `INSTRUCCIONES.md` completo antes de responder cualquier pedido: es el núcleo (reglas, flujos, estilo).
2. Leé `configuracion/proyecto.md`: ahí están la universidad, la carrera, las carpetas y las preferencias de la
   persona. Si tiene campos con `[completar]`, hacé la puesta en marcha que describe `INSTRUCCIONES.md`.
3. Según el pedido, seguí el flujo correspondiente: `flujos/resumir.md`, `flujos/tp.md`, `flujos/explicar.md` o
   `flujos/cuestionario.md`. Los roles están en `roles/` y las guías de apoyo en `apoyo/`.
4. Las herramientas de generación de documentos (Pandoc, Python, un navegador) están en `sistema-visual/`; el manual de
   instalación es `MANUAL-DE-IMPLEMENTACION.md` y el de uso, `MANUAL-DE-USO.md`.

Regla de oro: la fuente de la cátedra manda; nunca inventes, y nunca escribas dentro de las carpetas de fuente.
"""

COMANDOS = {
    "resumir": ("Resume una unidad, una materia o un tema corto en el formato y el modo pedidos.", "flujos/resumir.md"),
    "tp": ("Ayuda con un trabajo práctico y lo entrega en HTML A4, PDF o Word.", "flujos/tp.md"),
    "explicar": ("Explica un tema o unidades de una materia en el chat, sin generar archivos por defecto.", "flujos/explicar.md"),
    "cuestionario": ("Genera o extiende un cuestionario interactivo de una materia.", "flujos/cuestionario.md"),
}


def _comando_markdown(nombre, descripcion, flujo):
    return (f"---\ndescription: {descripcion}\n---\n\n"
            f"Seguí el flujo de `{flujo}` (leelo completo antes de empezar) para este pedido: $ARGUMENTS\n")


def _cursor():
    return ("---\ndescription: Ayudante Universitario, reglas del proyecto\nalwaysApply: true\n---\n\n" + PUNTERO)


# herramienta -> (descripcion, [(ruta relativa, contenido)])
def herramientas():
    h = {
        "agents": ("AGENTS.md: lo leen Codex CLI de OpenAI, Cursor, GitHub Copilot (agente), Jules, Aider y muchas más",
                   [("AGENTS.md", PUNTERO)]),
        "claude": ("Claude Code (Anthropic): CLAUDE.md y comandos /resumir /tp /explicar /cuestionario",
                   [("CLAUDE.md", PUNTERO)] +
                   [(f".claude/commands/{n}.md", _comando_markdown(n, d, f)) for n, (d, f) in COMANDOS.items()]),
        "gemini": ("Gemini CLI (Google): GEMINI.md", [("GEMINI.md", PUNTERO)]),
        "cursor": ("Cursor: regla siempre activa en .cursor/rules", [(".cursor/rules/ayudante-universitario.mdc", _cursor())]),
        "copilot": ("GitHub Copilot: .github/copilot-instructions.md", [(".github/copilot-instructions.md", PUNTERO)]),
        "windsurf": ("Windsurf: .windsurfrules", [(".windsurfrules", PUNTERO)]),
        "cline": ("Cline y Roo Code: .clinerules", [(".clinerules", PUNTERO)]),
    }
    return h


def escribir(ruta_rel, contenido, forzar):
    ruta = os.path.join(RAIZ, ruta_rel)
    if os.path.exists(ruta) and not forzar:
        print(f"  ya existe, no se toca: {ruta_rel}")
        return
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write(contenido)
    print(f"  creado: {ruta_rel}")


def leer(rel):
    with open(os.path.join(RAIZ, rel), encoding="utf-8") as f:
        return f.read().strip()


def prompt_unico(con_apoyo, forzar):
    """Un solo documento con instrucciones, configuracion, flujos, roles y (opcional) guias de apoyo."""
    partes = [("INSTRUCCIONES.md", leer("INSTRUCCIONES.md")), ("configuracion/proyecto.md", leer("configuracion/proyecto.md"))]
    for carpeta in ("flujos", "roles") + (("apoyo",) if con_apoyo else ()):
        for n in sorted(os.listdir(os.path.join(RAIZ, carpeta))):
            if n.endswith(".md"):
                partes.append((f"{carpeta}/{n}", leer(f"{carpeta}/{n}")))
    texto = ("# Ayudante Universitario: instrucciones completas\n\n"
             "Este documento reúne todos los archivos de instrucciones del proyecto, uno detrás de otro, cada uno "
             "con su ruta como título. Donde un archivo diga «ver `ruta`», buscá esa sección acá.\n\n")
    for ruta, cuerpo in partes:
        texto += f"\n\n=====\n## Archivo: {ruta}\n=====\n\n{cuerpo}\n"
    destino = "trabajo/prompt-completo.md" if con_apoyo else "trabajo/prompt-corto.md"
    escribir(destino, texto, forzar)
    print(f"  tamaño: {len(texto):,} caracteres (unos {len(texto) // 4:,} tokens)".replace(",", "."))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--herramienta", help="una o varias separadas por coma, o 'todas'")
    ap.add_argument("--lista", action="store_true")
    ap.add_argument("--prompt-unico", action="store_true")
    ap.add_argument("--sin-apoyo", action="store_true", help="con --prompt-unico: omite apoyo/")
    ap.add_argument("--forzar", action="store_true", help="reemplaza archivos que ya existen")
    a = ap.parse_args()
    h = herramientas()
    if a.lista or not (a.herramienta or a.prompt_unico):
        print("Herramientas conocidas:")
        for k, (d, _) in h.items():
            print(f"  {k:9} {d}")
        print("\nSi la tuya no está: usa --prompt-unico y pega el resultado como instrucciones, o copia el texto de "
              "AGENTS.md al archivo que tu herramienta lea.")
        return
    if a.herramienta:
        nombres = list(h) if a.herramienta == "todas" else [x.strip() for x in a.herramienta.split(",")]
        for n in nombres:
            if n not in h:
                sys.exit(f"Herramienta desconocida: {n}. Usa --lista.")
            print(f"{n}: {h[n][0]}")
            for ruta, contenido in h[n][1]:
                escribir(ruta, contenido, a.forzar)
    if a.prompt_unico:
        print("prompt único:")
        prompt_unico(not a.sin_apoyo, a.forzar)


if __name__ == "__main__":
    main()
