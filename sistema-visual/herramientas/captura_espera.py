"""captura_espera.py - captura con Firefox sin interfaz via Marionette, esperando
a que la pagina termine de armarse: Paged.js pagina despues del evento load, y el
cuestionario necesita clics antes de capturar. Incluye tambien la captura rapida
(`capturar_rapida`, `--rapida`), que no espera nada.

Uso como modulo (herramientas/capturas.py):
    with Firefox(tema="claro") as ff:
        ff.capturar(url, "salida.png", ancho=1280, alto=900, completa=True,
                    esperar="document.documentElement.dataset.paginado=='1'",
                    guion="document.getElementById('btnStart').click()")
        ff.capturar(url, "celular.png", ancho=390, alto=844, celular=True)
    pausa_guion: segundos de espera despues del guion (para ver un temporizador avanzar).

Uso suelto (archivo .html/.svg o URL, salida, ancho y alto):
    python captura_espera.py <html|svg|url> <salida.png> [ancho=900] [alto=1200] [claro|oscuro] [completa 0/1] [celular 0/1]
    python captura_espera.py <html|svg|url> <salida.png> [ancho] [alto] --rapida
        --rapida: `firefox --headless --screenshot` sin esperar (area visible; para un SVG o un HTML
        estatico); sin ella se usa Marionette, que espera a Paged.js y sirve para paginas largas
        (por defecto captura la pagina completa; pasar completa=0 para el area visible).

Celular: Firefox sin interfaz no achica la ventana por debajo de ~500 px. Para
ver el diseño de un telefono de verdad (390 px) la pagina se abre dentro de un
<iframe> de ese ancho, se estira el iframe al alto del contenido y se captura
solo el iframe: las consultas de medios responden al ancho del iframe.

Todo lo temporal (perfil de Firefox, pagina envoltorio) va a la carpeta
temporal del sistema.
"""
import base64
import json
import os
import pathlib
import shutil
import socket
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import entorno  # noqa: E402

# Navegador de produccion: Firefox (capturas, PDF de la Hoja A4 y medidas). Chrome o Chromium se usan
# solo para comprobar a mano la compatibilidad (ver INSTRUCCIONES.md, «Navegador y verificacion visual»).


def buscar_navegador():
    return entorno.firefox()


def a_url(origen):
    if origen.lower().startswith(("http://", "https://", "file:")):
        return origen
    return pathlib.Path(os.path.abspath(origen)).as_uri()


def capturar_rapida(origen, salida, ancho=900, alto=1200, espera=90):
    """Captura de un .html/.svg o URL con `firefox --headless --screenshot` (captura simple). No espera a Paged.js ni a scripts lentos: para eso, la
    clase Firefox. Solo captura el area visible (para una pagina larga, un alto grande).
    Detalles resueltos: `--screenshot <ruta>` no siempre escribe donde se le indica, asi que se
    corre en una carpeta de trabajo temporal propia con el nombre por defecto y despues se mueve
    el PNG; la primera ejecucion tarda 10 a 15 s (crea el perfil), las siguientes unos 2 s."""
    nav = buscar_navegador()
    url = a_url(origen)
    salida = os.path.abspath(salida)
    if os.path.exists(salida):
        os.remove(salida)
    trabajo = tempfile.mkdtemp(prefix="captura_")
    perfil = tempfile.mkdtemp(prefix="ff_rapida_")
    try:
        # Perfil temporal propio y --no-remote: sin esto Firefox usa el perfil por defecto y, si el
        # persona tiene su Firefox abierto, muestra «Firefox ya esta en uso» o se cuelga.
        subprocess.run([nav, "--headless", "--no-remote", "--profile", perfil, "--screenshot",
                        f"--window-size={ancho},{alto}", url],
                       cwd=trabajo, capture_output=True, text=True, timeout=espera)
        generado = os.path.join(trabajo, "screenshot.png")
        if os.path.exists(generado):
            shutil.move(generado, salida)
    finally:
        shutil.rmtree(trabajo, ignore_errors=True)
        shutil.rmtree(perfil, ignore_errors=True)
    if not os.path.exists(salida):
        raise SystemExit("La captura no se genero: " + url)
    return salida


class Firefox:
    def __init__(self, tema="claro"):
        self.tema = tema

    def __enter__(self):
        nav = buscar_navegador()
        self.perfil = tempfile.mkdtemp(prefix="ff_marionette_")
        self.port = 28000 + os.getpid() % 1000
        with open(os.path.join(self.perfil, "user.js"), "w") as f:
            f.write(f'user_pref("marionette.port", {self.port});\n')
            f.write('user_pref("layout.css.prefers-color-scheme.content-override", %d);\n'
                    % (0 if self.tema == "oscuro" else 1))
            f.write('user_pref("ui.systemUsesDarkTheme", %d);\n' % (1 if self.tema == "oscuro" else 0))
            f.write('user_pref("browser.shell.checkDefaultBrowser", false);\n')
            f.write('user_pref("security.fileuri.strict_origin_policy", false);\n')
            f.write('user_pref("layout.css.devPixelsPerPx", "1.0");\n')
        self.p = subprocess.Popen([nav, "--headless", "--marionette", "--no-remote", "--profile", self.perfil],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(160):
            try:
                self.s = socket.create_connection(("127.0.0.1", self.port), timeout=90)
                break
            except OSError:
                time.sleep(.5)
        else:
            raise SystemExit("Marionette no respondio")
        self.id = 0
        self._leer()
        self.cmd("WebDriver:NewSession", {"capabilities": {}})
        return self

    def __exit__(self, *a):
        try:
            self.cmd("Marionette:Quit", {})
        except Exception:
            pass
        time.sleep(1)
        self.p.kill()
        shutil.rmtree(self.perfil, ignore_errors=True)

    def _leer(self):
        n = b""
        while not n.endswith(b":"):
            n += self.s.recv(1)
        largo = int(n[:-1])
        datos = b""
        while len(datos) < largo:
            datos += self.s.recv(largo - len(datos))
        return json.loads(datos)

    def cmd(self, nombre, params=None):
        self.id += 1
        m = json.dumps([0, self.id, nombre, params or {}]).encode()
        self.s.sendall(str(len(m)).encode() + b":" + m)
        r = self._leer()
        if r[2]:
            raise RuntimeError(r[2])
        return r[3]

    def js(self, codigo):
        return self.cmd("WebDriver:ExecuteScript", {"script": codigo, "args": []}).get("value")

    def esperar(self, condicion, maximo=60):
        t0 = time.time()
        while time.time() - t0 < maximo:
            try:
                if self.js("return !!(" + condicion + ");"):
                    return True
            except RuntimeError:
                pass
            time.sleep(.4)
        print("  aviso: no se cumplio la espera:", condicion)
        return False

    def medir(self, html, ancho, alto, codigo, pausa=.8):
        """Abre la pagina dentro de un <iframe> de ancho x alto exactos (el mismo
        mecanismo que el modo celular de capturar) y devuelve lo que devuelve
        `codigo`: JavaScript con `return`, que ve `document` y `window` de la
        pagina (usar window.getComputedStyle, no getComputedStyle a secas)."""
        url = html if html.startswith(("http", "file:")) else pathlib.Path(os.path.abspath(html)).as_uri()
        envoltorio = os.path.join(tempfile.gettempdir(), "envoltorio_medir.html")
        with open(envoltorio, "w", encoding="utf-8") as f:
            f.write('<!doctype html><html><body style="margin:0;background:#888">'
                    f'<iframe id="tel" src="{url}" style="border:0;display:block;width:{ancho}px;height:{alto}px"></iframe>'
                    '</body></html>')
        self.cmd("WebDriver:SetWindowRect", {"width": max(ancho + 60, 600), "height": alto + 240})
        self.cmd("WebDriver:Navigate", {"url": pathlib.Path(envoltorio).as_uri()})
        self.esperar("document.getElementById('tel').contentDocument && "
                     "document.getElementById('tel').contentDocument.readyState=='complete'")
        self.js("return document.getElementById('tel').contentDocument.fonts.ready.then(function(){return 1});")
        time.sleep(pausa)
        return self.js("var w=document.getElementById('tel').contentWindow;"
                       "return (function(document,window){" + codigo + "})(w.document,w);")

    def capturar(self, html, png, ancho=1280, alto=900, completa=True, esperar=None, guion=None,
                 pausa=.8, celular=False, antes=None, pausa_guion=None):
        url = html if html.startswith(("http", "file:")) else pathlib.Path(os.path.abspath(html)).as_uri()
        if celular:
            envoltorio = os.path.join(tempfile.gettempdir(), "envoltorio_celular.html")
            with open(envoltorio, "w", encoding="utf-8") as f:
                f.write('<!doctype html><html><body style="margin:0;background:#888">'
                        f'<iframe id="tel" src="{url}" style="border:0;display:block;width:{ancho}px;height:{alto}px"></iframe>'
                        '</body></html>')
            self.cmd("WebDriver:SetWindowRect", {"width": max(ancho + 60, 600), "height": alto + 240})
            self.cmd("WebDriver:Navigate", {"url": pathlib.Path(envoltorio).as_uri()})
            self.esperar("document.getElementById('tel').contentDocument && "
                         "document.getElementById('tel').contentDocument.readyState=='complete'")
            doc = "document.getElementById('tel').contentDocument"
            self.js(f"return {doc}.fonts.ready.then(function(){{return 1}});")
            time.sleep(pausa)
            envolver = ("var w=document.getElementById('tel').contentWindow;"
                        "(function(document,window,localStorage){%s})(w.document,w,w.localStorage);return 1;")
            if antes:
                self.js(envolver % antes)
            if guion:
                self.js(envolver % guion)
                time.sleep(pausa_guion or pausa)
            if completa:
                h = self.js(f"return {doc}.documentElement.scrollHeight;")
                self.js(f"document.getElementById('tel').style.height='{h}px'; return 1;")
                self.cmd("WebDriver:SetWindowRect", {"width": max(ancho + 60, 600), "height": h + 240})
                time.sleep(.6)
            el = self.cmd("WebDriver:FindElement", {"using": "css selector", "value": "#tel"})
            eid = list(el["value"].values())[0] if isinstance(el.get("value"), dict) else list(el.values())[0]
            r = self.cmd("WebDriver:TakeScreenshot", {"id": eid, "full": False, "hash": False})
        else:
            self.cmd("WebDriver:SetWindowRect", {"width": ancho, "height": alto})
            self.cmd("WebDriver:Navigate", {"url": url})
            self.esperar("document.readyState=='complete'")
            self.js("return document.fonts.ready.then(function(){return 1});")
            if esperar:
                self.esperar(esperar)
            time.sleep(pausa)
            if antes:
                self.js(antes)
            if guion:
                self.js(guion)
                time.sleep(pausa_guion or pausa)
            r = self.cmd("WebDriver:TakeScreenshot", {"full": completa, "hash": False})
        with open(png, "wb") as f:
            f.write(base64.b64decode(r["value"]))
        return png


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
        with Firefox(a[4] if len(a) > 4 else "claro") as ff:
            print(ff.capturar(a[0], a[1], ancho, alto,
                              completa=(a[5] if len(a) > 5 else "1") == "1", celular=(a[6] if len(a) > 6 else "0") == "1",
                              esperar="!document.querySelector('.pagedjs_pages') && !window.PagedConfig || "
                                      "document.documentElement.dataset.paginado=='1'"))
