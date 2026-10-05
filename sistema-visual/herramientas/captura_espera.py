"""captura_espera.py - capturas de una pagina con el navegador sin interfaz que haya instalado (Firefox, Chrome,
Edge, Brave, Chromium...; ver navegador.py y entorno.py), esperando a que termine de armarse: Paged.js pagina
despues del evento load, y el cuestionario necesita clics antes de capturar. Incluye tambien la captura rapida
(`capturar_rapida`, `--rapida`), que no espera nada.

Uso como modulo (herramientas/capturas.py):
    with Navegador(tema="claro") as nav:
        nav.capturar(url, "salida.png", ancho=1280, alto=900, completa=True,
                     esperar="document.documentElement.dataset.paginado=='1'",
                     guion="document.getElementById('btnStart').click()")
        nav.capturar(url, "celular.png", ancho=390, alto=844, celular=True)
    pausa_guion: segundos de espera despues del guion (para ver un temporizador avanzar).
(`Firefox` sigue existiendo como otro nombre de `Navegador`, por compatibilidad.)

Uso suelto (archivo .html/.svg o URL, salida, ancho y alto):
    python captura_espera.py <html|svg|url> <salida.png> [ancho=900] [alto=1200] [claro|oscuro] [completa 0/1] [celular 0/1]
    python captura_espera.py <html|svg|url> <salida.png> [ancho] [alto] --rapida
        --rapida: el propio navegador con `--headless --screenshot`, sin esperar (area visible; para un SVG o un
        HTML estatico); sin ella se usa el protocolo de control del navegador, que espera a Paged.js y sirve para
        paginas largas (por defecto captura la pagina completa; pasar completa=0 para el area visible).

Celular: un navegador sin interfaz no achica la ventana por debajo de cierto ancho (Firefox, unos 500 px). Para
ver el diseño de un telefono de verdad (390 px) la pagina se abre dentro de un <iframe> de ese ancho, se estira
el iframe al alto del contenido y se captura solo el iframe: las consultas de medios responden al ancho del iframe.

Todo lo temporal (perfil del navegador, pagina envoltorio) va a la carpeta temporal del sistema.
"""
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import entorno  # noqa: E402
from navegador import abrir_sesion  # noqa: E402

# Cualquier navegador automatizable sirve para capturas, PDF de la Hoja A4 y medidas (Firefox o basado en
# Chromium; ver INSTRUCCIONES.md, «Navegador y verificacion visual»).


def buscar_navegador():
    return entorno.navegador()[0]


def a_url(origen):
    if origen.lower().startswith(("http://", "https://", "file:")):
        return origen
    return pathlib.Path(os.path.abspath(origen)).as_uri()


def capturar_rapida(origen, salida, ancho=900, alto=1200, espera=90):
    """Captura de un .html/.svg o URL con `--headless --screenshot` del navegador (captura simple). No espera a
    Paged.js ni a scripts lentos: para eso, la clase Navegador. Solo captura el area visible (para una pagina
    larga, un alto grande).
    Navegador: `--screenshot <ruta>` no siempre escribe donde se le indica, asi que se corre en una carpeta de
    trabajo temporal propia con el nombre por defecto y despues se mueve el PNG; la primera ejecucion tarda 10 a
    15 s (crea el perfil), las siguientes unos 2 s. Basados en Chromium: escriben directo en la ruta pedida."""
    nav, familia = entorno.navegador()
    url = a_url(origen)
    salida = os.path.abspath(salida)
    if os.path.exists(salida):
        os.remove(salida)
    trabajo = tempfile.mkdtemp(prefix="captura_")
    perfil = tempfile.mkdtemp(prefix="nav_rapida_")
    try:
        if familia == "gecko":
            # Perfil temporal propio y --no-remote: sin esto Firefox usa el perfil por defecto y, si la
            # persona tiene su Firefox abierto, muestra «Firefox ya esta en uso» o se cuelga.
            subprocess.run([nav, "--headless", "--no-remote", "--profile", perfil, "--screenshot",
                            f"--window-size={ancho},{alto}", url],
                           cwd=trabajo, capture_output=True, text=True, timeout=espera)
            generado = os.path.join(trabajo, "screenshot.png")
            if os.path.exists(generado):
                shutil.move(generado, salida)
        else:
            args = [nav, "--headless=new", f"--user-data-dir={perfil}", "--no-first-run", "--hide-scrollbars",
                    "--allow-file-access-from-files", "--force-device-scale-factor=1",
                    f"--screenshot={salida}", f"--window-size={ancho},{alto}", url]
            if hasattr(os, "geteuid") and os.geteuid() == 0:
                args.insert(2, "--no-sandbox")
            subprocess.run(args, cwd=trabajo, capture_output=True, text=True, timeout=espera)
    finally:
        shutil.rmtree(trabajo, ignore_errors=True)
        shutil.rmtree(perfil, ignore_errors=True)
    if not os.path.exists(salida):
        raise SystemExit("La captura no se genero: " + url)
    return salida


# Compatibilidad: `Navegador` (y el viejo nombre `Firefox`) abren una sesion del navegador que haya instalado.
Navegador = abrir_sesion
Firefox = abrir_sesion


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if x != "--rapida"]
    rapida = "--rapida" in sys.argv[1:]
    if len(a) < 2:
        raise SystemExit(__doc__)
    ancho = int(a[2]) if len(a) > 2 else 900
    alto = int(a[3]) if len(a) > 3 else 1200
    if rapida:
        print(capturar_rapida(a[0], a[1], ancho, alto))
    else:
        with Navegador(a[4] if len(a) > 4 else "claro") as ff:
            print(ff.capturar(a[0], a[1], ancho, alto,
                              completa=(a[5] if len(a) > 5 else "1") == "1", celular=(a[6] if len(a) > 6 else "0") == "1",
                              esperar="!document.querySelector('.pagedjs_pages') && !window.PagedConfig || "
                                      "document.documentElement.dataset.paginado=='1'"))
