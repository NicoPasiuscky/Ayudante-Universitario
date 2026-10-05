"""entorno.py - donde estan los programas externos que usa el sistema, en Windows, macOS y Linux.

Cada busqueda respeta una variable de entorno, por si el programa esta en un lugar poco comun:
    ESTUDIO_PANDOC     ruta de pandoc
    ESTUDIO_NAVEGADOR  ruta o nombre del navegador a usar (Firefox, Chrome, Edge, Brave, Chromium...)
    ESTUDIO_FIREFOX    ruta de firefox (compatibilidad; si no hay ESTUDIO_NAVEGADOR se prefiere Firefox)
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


_CHROMIUM = [
    # (nombres en el PATH, rutas habituales)
    (["google-chrome", "google-chrome-stable", "chrome"], [
        r"%ProgramFiles%\Google\Chrome\Application\chrome.exe", r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe",
        r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]),
    (["chromium", "chromium-browser"], ["/Applications/Chromium.app/Contents/MacOS/Chromium"]),
    (["microsoft-edge", "microsoft-edge-stable", "msedge"], [
        r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe", r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]),
    (["brave-browser", "brave"], [
        r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"]),
    (["opera"], [r"%LOCALAPPDATA%\Programs\Opera\opera.exe", "/Applications/Opera.app/Contents/MacOS/Opera"]),
    (["vivaldi", "vivaldi-stable"], [r"%LOCALAPPDATA%\Vivaldi\Application\vivaldi.exe",
                                     "/Applications/Vivaldi.app/Contents/MacOS/Vivaldi"]),
]


def _familia(ruta):
    nombre = os.path.basename(ruta).lower()
    if "safari" in nombre or "webkit" in nombre or "epiphany" in nombre or "orion" in nombre:
        raise SystemExit(f"{ruta}: este navegador no tiene modo sin interfaz automatizable. Usá Firefox o uno basado en "
                         "Chromium (Chrome, Edge, Brave, Chromium...). Los documentos se ven igual en cualquier navegador.")
    return "gecko" if "firefox" in nombre else "chromium"


def _firefox_ruta():
    return _primero("ESTUDIO_FIREFOX", ["firefox", "firefox-esr"], [
        r"%LOCALAPPDATA%\Microsoft\WindowsApps\firefox.exe", r"%ProgramFiles%\Mozilla Firefox\firefox.exe",
        r"%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe",
        "/Applications/Firefox.app/Contents/MacOS/firefox", "/snap/bin/firefox"])


def navegadores():
    """Todos los navegadores automatizables que hay, como [(ruta, familia)], en orden de preferencia."""
    hallados = []
    f = _firefox_ruta()
    if f:
        hallados.append((f, "gecko"))
    for nombres, rutas in _CHROMIUM:
        r = _primero("__NO_EXISTE__", nombres, rutas)
        if r:
            hallados.append((r, "chromium"))
    return hallados


def navegador(obligatorio=True):
    """(ruta, familia) del navegador que se usa para PDF, capturas y medidas. familia: 'gecko' (Firefox) o
    'chromium' (Chrome, Edge, Brave y demas). Se elige, en este orden: ESTUDIO_NAVEGADOR (ruta o nombre del
    programa), ESTUDIO_FIREFOX (compatibilidad), Firefox si esta instalado y despues el primer navegador basado
    en Chromium que se encuentre."""
    elegido = os.environ.get("ESTUDIO_NAVEGADOR")
    if elegido:
        ruta = elegido if os.path.exists(elegido) else shutil.which(elegido)
        if not ruta:
            raise SystemExit(f"ESTUDIO_NAVEGADOR apunta a {elegido!r}, que no existe ni esta en el PATH.")
        return ruta, _familia(ruta)
    hallados = navegadores()
    if hallados:
        return hallados[0]
    if obligatorio:
        raise SystemExit("No se encontro ningun navegador compatible (Firefox, Chrome, Edge, Brave, Chromium...). "
                         "Instalá uno o definí ESTUDIO_NAVEGADOR con la ruta de su programa.")
    return None


def firefox(obligatorio=True):
    """Compatibilidad: ruta del navegador elegido (ya no tiene que ser Firefox; ver navegador())."""
    n = navegador(obligatorio)
    return n[0] if n else None


def soffice():
    return _primero("ESTUDIO_SOFFICE", ["soffice", "libreoffice"], [
        r"C:\Program Files\LibreOffice\program\soffice.exe", "/Applications/LibreOffice.app/Contents/MacOS/soffice"])


if __name__ == "__main__":
    print(f"{'pandoc':24} {pandoc()}")
    hallados = navegadores()
    if os.environ.get("ESTUDIO_NAVEGADOR"):
        print(f"{'navegador elegido':24} {navegador()[0]}  (por ESTUDIO_NAVEGADOR)")
    elif hallados:
        print(f"{'navegador elegido':24} {hallados[0][0]}  ({'Firefox' if hallados[0][1] == 'gecko' else 'basado en Chromium'})")
        for r, fam in hallados[1:]:
            print(f"{'tambien disponible':24} {r}")
    else:
        print(f"{'navegador':24} NO ENCONTRADO (Firefox, Chrome, Edge, Brave o Chromium)")
    r = soffice()
    print(f"{'soffice (LibreOffice)':24} {r if r else 'NO ENCONTRADO (opcional)'}")
