"""construir_indice.py - arma indice.html (la pagina que muestra el sistema) desde
herramientas/indice.md, con el mismo sistema: Pandoc, estudio.lua y el formato
"HTML completo". Si ya hay capturas en capturas/, incrusta cuatro
miniaturas; si no, la pagina sale igual sin ellas.

Uso:  python herramientas/construir_indice.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import entorno  # noqa: E402

PANDOC = entorno.pandoc()
MINIATURAS = {"resumen-completo.jpg": "resumen-completo-extenso-escritorio.png",
              "resumen-a4.jpg": "resumen-a4-extenso-hoja2.png",
              "diapositivas.jpg": "diapositivas-escritorio-claro.png",
              "cuestionario.jpg": "cuestionario-resultado.png"}


def main():
    trabajo = tempfile.mkdtemp(prefix="indice_v4_")
    try:
        shutil.copy(os.path.join(AQUI, "indice.md"), trabajo)
        os.makedirs(os.path.join(trabajo, "miniaturas"))
        for destino, origen in MINIATURAS.items():
            ruta = os.path.join(RAIZ, "capturas", origen)
            im = Image.open(ruta).convert("RGB") if os.path.exists(ruta) else Image.new("RGB", (480, 600), "#E8E9EC")
            w = 480
            h = min(int(im.height * w / im.width), 640)
            im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS).crop((0, 0, w, h))
            im.save(os.path.join(trabajo, "miniaturas", destino), quality=78)
        r = lambda *p: os.path.join(RAIZ, *p)  # noqa: E731
        cmd = [PANDOC, "indice.md", "--standalone", "--embed-resources", entorno.mathml(),
               "--syntax-highlighting=pygments", "--lua-filter=" + r("incluir", "estudio.lua"), "-M", "formato=completo", "-M", "modo=extenso",
               "--include-in-header=" + r("incluir", "fuentes.html"),
               "--css=" + r("css", "tokens.css"), "--css=" + r("css", "tokens-oscuro.css"),
               "--css=" + r("css", "resumen-base.css"),
               "--css=" + r("css", "resumen-pantalla.css"), "--css=" + r("css", "resumen-completo.css"),
               "--css=" + r("css", "indice.css"),
               "--include-before-body=" + r("incluir", "tema.html"),
               "--include-after-body=" + r("incluir", "formulas-rectas.html"),
               "-o", r("indice.html")]
        p = subprocess.run(cmd, cwd=trabajo, capture_output=True, text=True, encoding="utf-8")
        if p.stderr.strip():
            print(p.stderr.strip())
        if p.returncode:
            raise SystemExit("fallo pandoc")
        print("indice.html", round(os.path.getsize(r("indice.html")) / 1024), "KB")
    finally:
        shutil.rmtree(trabajo, ignore_errors=True)


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    main()
