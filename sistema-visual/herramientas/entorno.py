"""entorno.py - donde estan los programas externos que usa el sistema, en Windows, macOS y Linux.

Cada busqueda respeta una variable de entorno, por si el programa esta en un lugar poco comun:
    ESTUDIO_PANDOC     ruta de pandoc
    ESTUDIO_FIREFOX    ruta de firefox
    ESTUDIO_SOFFICE    ruta de soffice (LibreOffice), alternativa a Word para revisar un .docx

Uso:  python herramientas/entorno.py      muestra que se encontro y que falta
"""
import os
import shutil
import sys

sys.dont_write_bytecode = True


def _primero(variable, nombres, rutas=()):
    ruta = os.environ.get(variable)
    if ruta and os.path.exists(ruta):
        return ruta
    for n in nombres:
        hallado = shutil.which(n)
        if hallado:
            return hallado
    for r in rutas:
        r = os.path.expandvars(os.path.expanduser(r))
        if os.path.exists(r):
            return r
    return None


def pandoc():
    """Ruta de pandoc, o 'pandoc' si no se encontro (el error lo da el sistema al ejecutarlo)."""
    return _primero("ESTUDIO_PANDOC", ["pandoc"], [
        r"%LOCALAPPDATA%\Pandoc\pandoc.exe", r"C:\Program Files\Pandoc\pandoc.exe",
        "/opt/homebrew/bin/pandoc", "/usr/local/bin/pandoc"]) or "pandoc"


def mathml():
    """Opcion de Pandoc que pide formulas MathML: `--math-method=mathml` en las versiones nuevas,
    `--mathml` en las anteriores. Siempre MathML, nunca MathJax (depende de un CDN)."""
    import subprocess
    try:
        ayuda = subprocess.run([pandoc(), "--help"], capture_output=True, text=True, encoding="utf-8").stdout
    except OSError:
        ayuda = ""
    return "--math-method=mathml" if "--math-method" in ayuda else "--mathml"


def firefox(obligatorio=True):
    """Ruta de Firefox. Se usa para capturas, para imprimir la Hoja A4 a PDF y para medir margenes."""
    ruta = _primero("ESTUDIO_FIREFOX", ["firefox", "firefox-esr"], [
        r"%LOCALAPPDATA%\Microsoft\WindowsApps\firefox.exe", r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        "/Applications/Firefox.app/Contents/MacOS/firefox", "/snap/bin/firefox"])
    if not ruta and obligatorio:
        raise SystemExit("No se encontro Firefox. Instalalo o defini la variable ESTUDIO_FIREFOX con su ruta.")
    return ruta


def soffice():
    return _primero("ESTUDIO_SOFFICE", ["soffice", "libreoffice"], [
        r"C:\Program Files\LibreOffice\program\soffice.exe", "/Applications/LibreOffice.app/Contents/MacOS/soffice"])


if __name__ == "__main__":
    for nombre, f in (("pandoc", pandoc), ("firefox", lambda: firefox(False)), ("soffice (LibreOffice)", soffice)):
        r = f()
        print(f"{nombre:24} {r if r and os.path.exists(r) or r and shutil.which(r) else 'NO ENCONTRADO'}")
