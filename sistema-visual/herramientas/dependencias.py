#!/usr/bin/env python3
"""dependencias.py - verifica que este instalado todo lo que el sistema necesita y, si falta algo, lo dice.

Regla del proyecto: este programa NUNCA instala nada por su cuenta. Si falta una dependencia, informa cual es, para
que sirve, de que fuente oficial se obtiene y con que comando; la persona decide y habilita la instalacion. Solo con
`--instalar-pip` (y despues de que la persona lo haya autorizado) instala las bibliotecas de Python desde PyPI, el
repositorio oficial; los programas del sistema (Pandoc, navegador, Graphviz...) los instala la persona, o un asistente
con su permiso explicito, con los comandos o las paginas oficiales que se muestran.

Uso:
    python sistema-visual/herramientas/dependencias.py                 informe completo
    python sistema-visual/herramientas/dependencias.py --para pdf      solo lo necesario para esa funcion
    python sistema-visual/herramientas/dependencias.py --instalar-pip  instala las bibliotecas de Python que falten
                                                                       (pide confirmacion; --si la omite, para uso
                                                                       despues de que la persona lo autorizo)
    python sistema-visual/herramientas/dependencias.py --json          resultado en JSON (para otros programas)

Funciones (--para): html, pdf, word, graficos, diagramas, verificacion, todo.
Codigo de salida: 0 si no falta nada obligatorio para lo pedido, 3 si falta algo obligatorio.

Como modulo:
    import dependencias
    dependencias.exigir("pdf")     # termina con un mensaje claro si falta algo obligatorio para generar PDF
"""
import importlib
import json
import os
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import entorno  # noqa: E402

SO = "windows" if sys.platform.startswith("win") else "macos" if sys.platform == "darwin" else "linux"
PANDOC_MIN = (3, 8)
PYTHON_MIN = (3, 10)

# Bibliotecas de Python: (nombre para importar, nombre en PyPI, para que sirve)
BIBLIOTECAS = [
    ("pymupdf", "pymupdf", "leer PDF, extraer figuras, poner el titulo del PDF y medir margenes"),
    ("numpy", "numpy", "calculos y ajustes de los TP"),
    ("sympy", "sympy", "verificacion simbolica de resultados"),
    ("matplotlib", "matplotlib", "graficos"),
    ("PIL", "pillow", "imagenes (figuras y capturas)"),
    ("fontTools", "fonttools", "fuentes del sistema visual y de los .docx"),
    ("lxml", "lxml", "generacion de .docx"),
]

# Programas del sistema: clave -> (descripcion, pagina oficial, {so: comando de instalacion oficial})
PROGRAMAS = {
    "python": ("Python %d.%d o superior" % PYTHON_MIN, "https://www.python.org/downloads/",
               {"windows": "winget install --id Python.Python.3.12 -e", "macos": "brew install python",
                "linux": "sudo apt install python3 python3-pip   (o el gestor de tu distribucion)"}),
    "pandoc": ("Pandoc %d.%d o superior" % PANDOC_MIN, "https://pandoc.org/installing.html",
               {"windows": "winget install --id JohnMacFarlane.Pandoc -e", "macos": "brew install pandoc",
                "linux": "descargar el paquete de https://pandoc.org/installing.html (los repositorios de las "
                         "distribuciones suelen traer una version vieja)"}),
    "navegador": ("un navegador: Firefox, Chrome, Edge, Brave o Chromium", "https://www.mozilla.org/firefox/new/",
                  {"windows": "winget install --id Mozilla.Firefox -e   (o Chrome: winget install --id Google.Chrome -e)",
                   "macos": "brew install --cask firefox   (o: brew install --cask google-chrome)",
                   "linux": "instalar Firefox o Chromium con el gestor de tu distribucion (preferible a snap o flatpak)"}),
    "graphviz": ("Graphviz (comando dot)", "https://graphviz.org/download/",
                 {"windows": "winget install --id Graphviz.Graphviz -e", "macos": "brew install graphviz",
                  "linux": "sudo apt install graphviz"}),
    "java": ("Java 11 o superior", "https://adoptium.net/",
             {"windows": "winget install --id Microsoft.OpenJDK.21 -e", "macos": "brew install openjdk",
              "linux": "sudo apt install default-jre"}),
    "plantuml": ("PlantUML (plantuml.jar)", "https://plantuml.com/download",
                 {"windows": "descargar plantuml.jar de la pagina oficial", "macos": "descargar plantuml.jar de la pagina oficial",
                  "linux": "descargar plantuml.jar de la pagina oficial"}),
    "libreoffice": ("LibreOffice (revisar los .docx sin Word)", "https://www.libreoffice.org/download/",
                    {"windows": "winget install --id TheDocumentFoundation.LibreOffice -e",
                     "macos": "brew install --cask libreoffice", "linux": "sudo apt install libreoffice-writer"}),
}

# Que necesita cada funcion: (obligatorios, recomendados)
FUNCIONES = {
    "html": (["python", "pandoc"], []),
    "pdf": (["python", "pandoc", "navegador", "lib:pymupdf"], []),
    "word": (["python", "pandoc", "lib:lxml", "lib:fonttools", "lib:pillow"], ["navegador", "libreoffice"]),
    "graficos": (["python", "lib:numpy", "lib:matplotlib", "lib:sympy", "lib:pillow", "lib:fonttools"], []),
    "diagramas": ([], ["graphviz", "java", "plantuml"]),
    "verificacion": (["python", "pandoc", "navegador", "lib:pymupdf", "lib:lxml", "lib:fonttools", "lib:pillow",
                      "lib:numpy", "lib:sympy", "lib:matplotlib"], ["libreoffice"]),
}
FUNCIONES["todo"] = (sorted({x for o, _ in FUNCIONES.values() for x in o}),
                     sorted({x for o, r in FUNCIONES.values() for x in r}))


def _version_pandoc():
    ruta = entorno.pandoc()
    try:
        out = subprocess.run([ruta, "--version"], capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return None, None
    m = re.search(r"pandoc(?:\.exe)?\s+(\d+)\.(\d+)(?:\.(\d+))?", out)
    return (ruta, tuple(int(x) for x in m.groups() if x)) if m else (None, None)


def estado(clave):
    """Devuelve (ok, detalle) de una dependencia ('python', 'pandoc', 'lib:numpy', ...)."""
    if clave.startswith("lib:"):
        nombre = clave[4:]
        imp = next((i for i, p, _ in BIBLIOTECAS if p == nombre), nombre)
        try:
            importlib.import_module(imp)
            return True, "instalada"
        except Exception:
            return False, "no esta instalada (o no se puede importar)"
    if clave == "python":
        v = sys.version_info[:3]
        return v >= PYTHON_MIN, f"version {v[0]}.{v[1]}.{v[2]}" + ("" if v >= PYTHON_MIN else f" (hace falta {PYTHON_MIN[0]}.{PYTHON_MIN[1]} o superior)")
    if clave == "pandoc":
        ruta, v = _version_pandoc()
        if not ruta:
            return False, "no se encontro"
        ok = v >= PANDOC_MIN
        return ok, f"version {'.'.join(map(str, v))} en {ruta}" + ("" if ok else f" (hace falta {PANDOC_MIN[0]}.{PANDOC_MIN[1]} o superior)")
    if clave == "navegador":
        try:
            ruta, fam = entorno.navegador()
        except SystemExit:
            return False, "no se encontro ningun navegador compatible"
        return True, f"{ruta} ({'Firefox' if fam == 'gecko' else 'basado en Chromium'})"
    if clave == "graphviz":
        r = shutil.which("dot")
        return bool(r), r or "no se encontro"
    if clave == "java":
        r = shutil.which("java")
        return bool(r), r or "no se encontro"
    if clave == "plantuml":
        r = shutil.which("plantuml")
        return bool(r), r or "no se encontro el comando plantuml (ni un acceso directo a plantuml.jar)"
    if clave == "libreoffice":
        r = entorno.soffice()
        return bool(r), r or "no se encontro"
    raise KeyError(clave)


def _descripcion(clave):
    if clave.startswith("lib:"):
        nombre = clave[4:]
        for _, p, para in BIBLIOTECAS:
            if p == nombre:
                return f"biblioteca de Python «{p}»", para
    d = PROGRAMAS[clave]
    return d[0], ""


def _instruccion(clave):
    """Texto de como obtenerla de la fuente oficial."""
    if clave.startswith("lib:"):
        return f"PyPI, el repositorio oficial de Python: python -m pip install {clave[4:]}"
    _, pagina, comandos = PROGRAMAS[clave]
    return f"{comandos[SO]}\n         Pagina oficial: {pagina}"


def evaluar(funcion="todo"):
    obligatorios, recomendados = FUNCIONES[funcion]
    res = {"funcion": funcion, "obligatorios": {}, "recomendados": {}}
    for grupo, claves in (("obligatorios", obligatorios), ("recomendados", recomendados)):
        for c in claves:
            ok, det = estado(c)
            res[grupo][c] = {"ok": ok, "detalle": det}
    res["faltan"] = [c for c, v in res["obligatorios"].items() if not v["ok"]]
    res["faltan_recomendados"] = [c for c, v in res["recomendados"].items() if not v["ok"]]
    return res


def informe(res, solo_faltantes=False):
    lineas = []
    for grupo, titulo in (("obligatorios", "Necesarios"), ("recomendados", "Recomendados u opcionales")):
        items = res[grupo]
        if not items:
            continue
        lineas.append(f"{titulo} para «{res['funcion']}»:")
        for c, v in items.items():
            if solo_faltantes and v["ok"]:
                continue
            nombre, para = _descripcion(c)
            lineas.append(f"  [{'OK ' if v['ok'] else 'FALTA'}] {nombre}: {v['detalle']}" + (f"  ({para})" if para and not v["ok"] else ""))
    faltan = res["faltan"] + (res["faltan_recomendados"] if not solo_faltantes else [])
    if res["faltan"] or res["faltan_recomendados"]:
        lineas.append("")
        lineas.append("Para instalar lo que falta, siempre desde fuentes oficiales y con tu autorizacion:")
        for c in res["faltan"] + res["faltan_recomendados"]:
            nombre, _ = _descripcion(c)
            marca = "obligatorio" if c in res["faltan"] else "opcional"
            lineas.append(f"  - {nombre} ({marca}): {_instruccion(c)}")
    return "\n".join(lineas)


def exigir(funcion="html", extra=()):
    """Si falta algo obligatorio para `funcion` (o en `extra`: claves como 'lib:lxml'), muestra que falta, de donde
    se obtiene y termina con codigo 3, SIN instalar nada. Si no falta nada, no imprime nada."""
    res = evaluar(funcion)
    for c in extra:
        ok, det = estado(c)
        res["obligatorios"][c] = {"ok": ok, "detalle": det}
        if not ok and c not in res["faltan"]:
            res["faltan"].append(c)
    if not res["faltan"]:
        return res
    print(f"Falta software necesario para «{funcion}». No se instala nada sin tu autorizacion.\n", file=sys.stderr)
    print(informe(res, solo_faltantes=True), file=sys.stderr)
    print("\nAutorizá la instalacion desde las fuentes oficiales indicadas (o instalalo vos) y volve a ejecutar el "
          "comando. Para comprobar: python sistema-visual/estudio.py entorno", file=sys.stderr)
    sys.exit(3)


def instalar_pip(confirmado=False, funcion="todo"):
    faltan = [c[4:] for c in evaluar(funcion)["obligatorios"] if c.startswith("lib:") and not estado(c)[0]]
    faltan += [c[4:] for c in evaluar(funcion)["recomendados"] if c.startswith("lib:") and not estado(c)[0]]
    if not faltan:
        print("No falta ninguna biblioteca de Python.")
        return 0
    print("Se instalarian desde PyPI (repositorio oficial de Python): " + ", ".join(faltan))
    if not confirmado:
        if not sys.stdin.isatty():
            print("Sin confirmacion no se instala nada. Si la persona ya lo autorizo, volve a ejecutar con --si.")
            return 3
        if input("¿Instalarlas ahora? [s/N] ").strip().lower() not in ("s", "si", "sí", "y", "yes"):
            print("No se instalo nada.")
            return 3
    return subprocess.call([sys.executable, "-m", "pip", "install", *faltan])


if __name__ == "__main__":
    a = sys.argv[1:]
    funcion = "todo"
    if "--para" in a:
        funcion = a[a.index("--para") + 1]
        if funcion not in FUNCIONES:
            sys.exit(f"Funcion desconocida: {funcion}. Validas: {', '.join(FUNCIONES)}")
    if "--instalar-pip" in a:
        sys.exit(instalar_pip("--si" in a, funcion))
    res = evaluar(funcion)
    if "--json" in a:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        print(informe(res))
        if not res["faltan"] and not res["faltan_recomendados"]:
            print("\nTodo listo.")
    sys.exit(3 if res["faltan"] else 0)
