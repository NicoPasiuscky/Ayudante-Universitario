"""navegador.py - maneja un navegador sin interfaz, sea cual sea el que tengas instalado.

El sistema necesita un navegador para cuatro cosas que ningun otro programa hace igual de bien: esperar a que
Paged.js arme las hojas A4, imprimir esas hojas a PDF, sacar capturas y medir la pagina (reglas de verificar_reglas.py)
y dibujar los SVG de los .docx. Este modulo ofrece una sola interfaz (`SesionBase`) con dos motores:

  * Gecko     Firefox, por su protocolo Marionette.
  * Chromium  Chrome, Chromium, Edge, Brave, Opera, Vivaldi y cualquier otro basado en Chromium, por el protocolo
              de depuracion remota (CDP), con un cliente WebSocket propio: no hay que instalar nada de Python.

Safari y otros navegadores sin modo sin interfaz no se pueden automatizar; los documentos que genera el sistema se
ven en cualquier navegador moderno, y el PDF se puede sacar a mano con Imprimir.

Eleccion del navegador (ver entorno.navegador): variable ESTUDIO_NAVEGADOR (ruta o nombre), o Firefox si esta
instalado, o el primer navegador basado en Chromium que se encuentre.

Uso:
    from navegador import Sesion
    with Sesion("claro") as nav:
        nav.ir("file:///ruta/a/pagina.html")
        nav.esperar("document.readyState=='complete'")
        png = nav.captura(completa=True)       # bytes
        pdf = nav.pdf()                         # bytes, A4 sin margenes (los pone el CSS)

Prueba rapida:  python herramientas/navegador.py     (abre el navegador, carga una pagina y la mide)
"""
import base64
import json
import os
import pathlib
import re
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.request

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import entorno  # noqa: E402

A4_PULGADAS = (8.2677, 11.6929)


def _url(origen):
    if origen.lower().startswith(("http://", "https://", "file:", "about:")):
        return origen
    return pathlib.Path(os.path.abspath(origen)).as_uri()


class SesionBase:
    """Interfaz comun. Las subclases implementan abrir, cerrar, ventana, ir, recargar, js, pdf y _png."""
    familia = "?"

    def __init__(self, tema="claro"):
        self.tema = tema

    def __enter__(self):
        self.abrir()
        return self

    def __exit__(self, *a):
        self.cerrar()

    # ---- a implementar por cada motor
    def abrir(self):
        raise NotImplementedError

    def cerrar(self):
        raise NotImplementedError

    def ventana(self, ancho, alto):
        raise NotImplementedError

    def ir(self, url):
        raise NotImplementedError

    def recargar(self):
        raise NotImplementedError

    def js(self, codigo):
        """Ejecuta el cuerpo de una funcion (con `return`) en la pagina y devuelve su valor."""
        raise NotImplementedError

    def pdf(self):
        """PDF de la pagina actual en A4, sin margenes propios, con fondos (bytes)."""
        raise NotImplementedError

    def _png(self, completa, elemento):
        raise NotImplementedError

    # ---- comunes
    def captura(self, completa=False, elemento=None):
        """PNG (bytes) del area visible, de la pagina completa o de un elemento (selector CSS)."""
        return self._png(completa, elemento)

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

    def _envoltorio(self, url, ancho, alto, nombre):
        ruta = os.path.join(tempfile.gettempdir(), nombre)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write('<!doctype html><html><body style="margin:0;background:#888">'
                    f'<iframe id="tel" src="{url}" style="border:0;display:block;width:{ancho}px;height:{alto}px"></iframe>'
                    '</body></html>')
        self.ventana(max(ancho + 60, 600), alto + 240)
        self.ir(pathlib.Path(ruta).as_uri())
        self.esperar("document.getElementById('tel').contentDocument && "
                     "document.getElementById('tel').contentDocument.readyState=='complete'")
        self.js("return document.getElementById('tel').contentDocument.fonts.ready.then(function(){return 1});")

    def medir(self, html, ancho, alto, codigo, pausa=.8):
        """Abre la pagina dentro de un <iframe> de ancho x alto exactos (el mismo mecanismo que el modo celular
        de capturar) y devuelve lo que devuelve `codigo`: JavaScript con `return`, que ve `document` y `window`
        de la pagina (usar window.getComputedStyle, no getComputedStyle a secas)."""
        self._envoltorio(_url(html), ancho, alto, "envoltorio_medir.html")
        time.sleep(pausa)
        return self.js("var w=document.getElementById('tel').contentWindow;"
                       "return (function(document,window){" + codigo + "})(w.document,w);")

    def capturar(self, html, png, ancho=1280, alto=900, completa=True, esperar=None, guion=None,
                 pausa=.8, celular=False, antes=None, pausa_guion=None):
        url = _url(html)
        if celular:
            self._envoltorio(url, ancho, alto, "envoltorio_celular.html")
            doc = "document.getElementById('tel').contentDocument"
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
                self.ventana(max(ancho + 60, 600), h + 240)
                time.sleep(.6)
            datos = self.captura(elemento="#tel")
        else:
            self.ventana(ancho, alto)
            self.ir(url)
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
            datos = self.captura(completa=completa)
        with open(png, "wb") as f:
            f.write(datos)
        return png


# ======================================================================================================
# Navegador: Marionette
# ======================================================================================================
class SesionGecko(SesionBase):
    familia = "gecko"

    def abrir(self):
        nav = entorno.navegador()[0]
        self.perfil = tempfile.mkdtemp(prefix="ff_marionette_")
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        self.port = s.getsockname()[1]
        s.close()
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
            self.cerrar()
            raise SystemExit("Marionette no respondio")
        self.id = 0
        self._leer()
        self.cmd("WebDriver:NewSession", {"capabilities": {}})

    def cerrar(self):
        try:
            self.cmd("Marionette:Quit", {})
        except Exception:
            pass
        time.sleep(1)
        try:
            self.p.kill()
        except Exception:
            pass
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

    def ventana(self, ancho, alto):
        self.ventana(ancho, alto)

    def ir(self, url):
        self.ir(_url(url))

    def recargar(self):
        self.recargar()

    def pdf(self):
        r = self.cmd("WebDriver:Print", {"page": {"width": 21.0, "height": 29.7},
                                         "margin": {"top": 0, "bottom": 0, "left": 0, "right": 0},
                                         "shrinkToFit": False, "background": True})
        return base64.b64decode(r["value"])

    def _png(self, completa, elemento):
        if elemento:
            el = self.cmd("WebDriver:FindElement", {"using": "css selector", "value": elemento})
            eid = list(el["value"].values())[0] if isinstance(el.get("value"), dict) else list(el.values())[0]
            r = self.cmd("WebDriver:TakeScreenshot", {"id": eid, "full": False, "hash": False})
        else:
            r = self.cmd("WebDriver:TakeScreenshot", {"full": bool(completa), "hash": False})
        return base64.b64decode(r["value"])


# ======================================================================================================
# Chrome, Chromium, Edge, Brave y demas: protocolo de depuracion remota (CDP) sobre WebSocket
# ======================================================================================================
class _WebSocket:
    """Cliente WebSocket minimo (RFC 6455), solo lo que hace falta para hablar con el navegador."""

    def __init__(self, url, timeout=180):
        m = re.match(r"ws://([^:/]+):(\d+)(/.*)$", url)
        if not m:
            raise ValueError("direccion WebSocket no valida: " + url)
        host, port, ruta = m.group(1), int(m.group(2)), m.group(3)
        self.s = socket.create_connection((host, port), timeout=timeout)
        clave = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((f"GET {ruta} HTTP/1.1\r\nHost: {host}:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                        f"Sec-WebSocket-Key: {clave}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        resp = b""
        while b"\r\n\r\n" not in resp:
            trozo = self.s.recv(4096)
            if not trozo:
                raise ConnectionError("el navegador cerro la conexion")
            resp += trozo
        cabecera, _, self.buf = resp.partition(b"\r\n\r\n")
        if b" 101 " not in cabecera.split(b"\r\n")[0]:
            raise ConnectionError("el navegador rechazo el WebSocket: " + cabecera.split(b"\r\n")[0].decode(errors="replace"))

    def _n(self, n):
        while len(self.buf) < n:
            trozo = self.s.recv(1 << 20)
            if not trozo:
                raise ConnectionError("conexion cerrada")
            self.buf += trozo
        dato, self.buf = self.buf[:n], self.buf[n:]
        return dato

    def _enviar_trama(self, opcode, dato):
        n = len(dato)
        cab = bytearray([0x80 | opcode])
        if n < 126:
            cab.append(0x80 | n)
        elif n < 65536:
            cab.append(0x80 | 126)
            cab += struct.pack(">H", n)
        else:
            cab.append(0x80 | 127)
            cab += struct.pack(">Q", n)
        mascara = os.urandom(4)
        cab += mascara
        if n:
            relleno = (mascara * (n // 4 + 1))[:n]
            dato = (int.from_bytes(dato, "big") ^ int.from_bytes(relleno, "big")).to_bytes(n, "big")
        self.s.sendall(bytes(cab) + dato)

    def enviar(self, texto):
        self._enviar_trama(0x1, texto.encode("utf-8"))

    def recibir(self):
        """Devuelve el siguiente mensaje de texto completo."""
        partes, tipo = [], None
        while True:
            b0, b1 = self._n(2)
            fin, opcode, largo = b0 & 0x80, b0 & 0x0F, b1 & 0x7F
            if largo == 126:
                largo = struct.unpack(">H", self._n(2))[0]
            elif largo == 127:
                largo = struct.unpack(">Q", self._n(8))[0]
            if b1 & 0x80:                       # los servidores no enmascaran, pero por las dudas
                mascara = self._n(4)
                dato = bytes(b ^ mascara[i % 4] for i, b in enumerate(self._n(largo)))
            else:
                dato = self._n(largo)
            if opcode == 0x8:
                raise ConnectionError("el navegador cerro la conexion")
            if opcode == 0x9:                   # ping
                self._enviar_trama(0xA, dato)
                continue
            if opcode == 0xA:                   # pong
                continue
            if opcode in (0x1, 0x2):
                tipo = opcode
            partes.append(dato)
            if fin:
                texto = b"".join(partes)
                return texto.decode("utf-8") if tipo == 0x1 else texto

    def cerrar(self):
        try:
            self.s.close()
        except OSError:
            pass


class SesionChromium(SesionBase):
    familia = "chromium"

    def abrir(self):
        nav = entorno.navegador()[0]
        self.perfil = tempfile.mkdtemp(prefix="cr_cdp_")
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        self.port = s.getsockname()[1]
        s.close()
        args = [nav, "--headless=new", f"--remote-debugging-port={self.port}", "--remote-debugging-address=127.0.0.1",
                f"--user-data-dir={self.perfil}", "--no-first-run", "--no-default-browser-check",
                "--disable-extensions", "--disable-background-networking", "--disable-sync", "--mute-audio",
                "--hide-scrollbars", "--force-device-scale-factor=1",
                # las paginas del sistema son archivos locales que se leen entre si (iframes, localStorage)
                "--allow-file-access-from-files", "--disable-web-security", "about:blank"]
        if hasattr(os, "geteuid") and os.geteuid() == 0:        # root (contenedores): Chromium lo exige
            args.append("--no-sandbox")
        self.p = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        abridor = urllib.request.build_opener(urllib.request.ProxyHandler({}))     # sin proxy: es local
        destino = None
        for _ in range(160):
            try:
                with abridor.open(f"http://127.0.0.1:{self.port}/json/list", timeout=5) as r:
                    paginas = [t for t in json.load(r) if t.get("type") == "page"]
                if paginas:
                    destino = paginas[0]["webSocketDebuggerUrl"]
                    break
            except Exception:
                pass
            if self.p.poll() is not None:
                break
            time.sleep(.25)
        if not destino:
            self.cerrar()
            raise SystemExit("El navegador no respondio (protocolo de depuracion). Si es un Chromium instalado como "
                             "paquete snap o flatpak, instalá otra copia o definí ESTUDIO_NAVEGADOR con otro navegador.")
        self.ws = _WebSocket(destino)
        self.id = 0
        self.cmd("Page.enable")
        self.cmd("Emulation.setEmulatedMedia", {"features": [
            {"name": "prefers-color-scheme", "value": "dark" if self.tema == "oscuro" else "light"}]})

    def cerrar(self):
        try:
            self.ws.cerrar()
        except Exception:
            pass
        try:
            self.p.terminate()
            self.p.wait(timeout=10)
        except Exception:
            try:
                self.p.kill()
            except Exception:
                pass
        time.sleep(.5)
        shutil.rmtree(self.perfil, ignore_errors=True)

    def cmd(self, metodo, params=None):
        self.id += 1
        mi_id = self.id
        self.ws.enviar(json.dumps({"id": mi_id, "method": metodo, "params": params or {}}))
        while True:
            m = json.loads(self.ws.recibir())
            if m.get("id") == mi_id:
                if "error" in m:
                    raise RuntimeError(f"{metodo}: {m['error'].get('message')}")
                return m.get("result", {})

    def js(self, codigo):
        r = self.cmd("Runtime.evaluate", {"expression": "(function(){" + codigo + "\n})()",
                                          "awaitPromise": True, "returnByValue": True})
        if "exceptionDetails" in r:
            det = r["exceptionDetails"]
            raise RuntimeError((det.get("exception") or {}).get("description") or det.get("text", "error de JavaScript"))
        return r.get("result", {}).get("value")

    def ventana(self, ancho, alto):
        self.cmd("Emulation.setDeviceMetricsOverride", {"width": int(ancho), "height": int(alto),
                                                       "deviceScaleFactor": 1, "mobile": False})

    def ir(self, url):
        # Chromium comparte el localStorage entre todos los archivos locales (Firefox lo separa por archivo): se
        # vacia antes de cada navegacion para que una pagina no herede el estado de la anterior.
        url = _url(url)
        if url.startswith("file:"):
            try:
                self.cmd("Storage.clearDataForOrigin", {"origin": "file://", "storageTypes": "local_storage,session_storage"})
            except RuntimeError:
                pass
        self.cmd("Page.navigate", {"url": url})
        time.sleep(.2)

    def recargar(self):
        self.cmd("Page.reload")
        time.sleep(.2)

    def pdf(self):
        r = self.cmd("Page.printToPDF", {"paperWidth": A4_PULGADAS[0], "paperHeight": A4_PULGADAS[1],
                                         "marginTop": 0, "marginBottom": 0, "marginLeft": 0, "marginRight": 0,
                                         "printBackground": True, "preferCSSPageSize": True,
                                         "displayHeaderFooter": False, "scale": 1})
        return base64.b64decode(r["data"])

    def _png(self, completa, elemento):
        params = {"format": "png"}
        if elemento:
            x, y, w, h = self.js("var r=document.querySelector(" + json.dumps(elemento) + ").getBoundingClientRect();"
                                 "return [r.left+window.scrollX, r.top+window.scrollY, r.width, r.height];")
            params.update(clip={"x": x, "y": y, "width": w, "height": h, "scale": 1}, captureBeyondViewport=True)
        elif completa:
            m = self.cmd("Page.getLayoutMetrics")
            tam = m.get("cssContentSize") or m["contentSize"]
            params.update(clip={"x": 0, "y": 0, "width": tam["width"], "height": tam["height"], "scale": 1},
                          captureBeyondViewport=True)
        return base64.b64decode(self.cmd("Page.captureScreenshot", params)["data"])


def abrir_sesion(tema="claro"):
    """Una sesion del navegador que haya (Firefox o basado en Chromium), segun entorno.navegador()."""
    familia = entorno.navegador()[1]
    return (SesionGecko if familia == "gecko" else SesionChromium)(tema)


Sesion = abrir_sesion      # `with Sesion("claro") as nav:` elige el motor segun el navegador instalado


if __name__ == "__main__":
    ruta, familia = entorno.navegador()
    print(f"navegador: {ruta} ({'Firefox, Marionette' if familia == 'gecko' else 'basado en Chromium, CDP'})")
    html = os.path.join(tempfile.gettempdir(), "prueba_navegador.html")
    with open(html, "w", encoding="utf-8") as f:
        f.write("<!doctype html><meta charset=utf-8><title>prueba</title><body style='font:20px sans-serif'>"
                "<h1 id=t>Hola</h1><p>Paso " + "1 " * 300 + "</p><script>document.documentElement.dataset.listo='1'</script>")
    with abrir_sesion("oscuro") as nav:
        nav.ventana(900, 600)
        nav.ir(html)
        nav.esperar("document.documentElement.dataset.listo=='1'")
        print("titulo:", nav.js("return document.getElementById('t').textContent"))
        print("modo oscuro:", nav.js("return window.matchMedia('(prefers-color-scheme: dark)').matches"))
        png = nav.captura(completa=True)
        pdf = nav.pdf()
        print(f"captura PNG: {len(png)} bytes, PDF: {len(pdf)} bytes, cabecera PDF: {pdf[:5]!r}")
