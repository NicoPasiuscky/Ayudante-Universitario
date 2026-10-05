#!/usr/bin/env python3
"""estudio.py - interfaz unica para generar los documentos del sistema visual v4.

Es una envoltura fina de construir.py, imprimir_a4.py, construir_docx.py y nombres.py: hace
lo mismo que los comandos largos de apoyo/generar-html.md, apoyo/material-a4.md y flujos/tp.md,
pero con una sola linea. Corre en Windows, macOS y Linux. Requiere Pandoc y, para PDF o Word,
Firefox (ver MANUAL-DE-IMPLEMENTACION.md).

Subcomandos:

  resumen   Markdown de resumen -> HTML completo, Hoja A4 (con PDF opcional) o diapositivas
      python sistema-visual/estudio.py resumen unidad.md --formato a4 --modo extenso \\
          --salida html+pdf --carpeta "Resumenes" --nombre "Materia A ｜ Resumen꞉ Unidad 1 ｜ extenso ｜ hoja A4" \\
          [--indice] [--sin-espejo] [--practica]

  material  Markdown de parcial o soluciones -> HTML A4 (y PDF opcional)
      python sistema-visual/estudio.py material parcial.md --salida html+pdf --carpeta "Parciales" --nombre "..."

  tp        Markdown + JSON de caratula -> HTML A4 (y PDF opcional)
      python sistema-visual/estudio.py tp tp.md --datos tp.json --salida pdf --carpeta "TPs" --nombre "..."

  docx      Markdown -> Word
      python sistema-visual/estudio.py docx unidad.md --tipo resumen --modo corto -o salida.docx [--indice] [--practica] [--sin-espejo]
      python sistema-visual/estudio.py docx tp.md --tipo tp --datos tp.json -o tp.docx

  nombre    Nombre de archivo correcto (con las barras y los dos puntos especiales), para no escribirlo a mano
      python sistema-visual/estudio.py nombre "Materia A" Resumen --unidades 1 2 3 --modo corto --formato "hoja A4"
      python sistema-visual/estudio.py nombre "Materia A" "Trabajo práctico" --unidades 4

  entorno   Que programas encontro (Pandoc, Firefox, LibreOffice)

--formato:  completo | a4 | diapositivas        --modo: extenso | corto
--salida:   html | html+pdf | pdf  (solo Hoja A4, material y TP; en HTML completo y diapositivas es siempre HTML)
Con `--salida pdf` el HTML se arma en un directorio temporal y en --carpeta queda solo el PDF.
Si no se da --nombre, se usa el nombre del .md sin extension.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "herramientas"))


def _nombre_base(a, md):
    return a.nombre or os.path.splitext(os.path.basename(md))[0]


def _entregar(html, a, md, espejo):
    import imprimir_a4
    escritas, hojas = imprimir_a4.entregar(html, a.carpeta, _nombre_base(a, md), a.salida, espejo=espejo)
    for e in escritas:
        print("  listo:", e)
    if hojas:
        print("  hojas del PDF:", hojas)


def cmd_resumen(a):
    import construir as c
    md = os.path.abspath(a.md)
    espejo = not a.sin_espejo
    extra = ("practica=true",) if a.practica else ()
    if a.formato == "a4":
        with tempfile.TemporaryDirectory(prefix="estudio_") as tmp:
            html = os.path.join(tmp, "x.html")
            c.resumen(md, html, "a4", a.modo, indice=a.indice, extra_meta=extra, espejo=espejo)
            _entregar(html, a, md, espejo)
    else:
        os.makedirs(a.carpeta, exist_ok=True)
        destino = os.path.join(a.carpeta, _nombre_base(a, md) + ".html")
        c.resumen(md, destino, a.formato, a.modo, indice=a.indice and a.formato == "completo", extra_meta=extra)
        print("  listo:", destino)


def cmd_material(a):
    import construir as c
    md = os.path.abspath(a.md)
    with tempfile.TemporaryDirectory(prefix="estudio_") as tmp:
        html = os.path.join(tmp, "x.html")
        c.material(md, html, espejo=not a.sin_espejo)
        _entregar(html, a, md, not a.sin_espejo)


def cmd_tp(a):
    import construir as c
    md = os.path.abspath(a.md)
    with tempfile.TemporaryDirectory(prefix="estudio_") as tmp:
        html = os.path.join(tmp, "x.html")
        c.tp(md, html, datos=a.datos, espejo=not a.sin_espejo)
        _entregar(html, a, md, not a.sin_espejo)


def cmd_docx(a):
    cmd = [sys.executable, os.path.join(RAIZ, "docx", "construir_docx.py"), os.path.abspath(a.md), "--tipo", a.tipo,
           "-o", os.path.abspath(a.o), "--chequeo"]
    if a.modo and a.tipo == "resumen":
        cmd += ["--modo", a.modo]
    if a.datos:
        cmd += ["--datos", os.path.abspath(a.datos)]
    for flag, activo in (("--indice", a.indice), ("--practica", a.practica), ("--sin-espejo", a.sin_espejo)):
        if activo:
            cmd.append(flag)
    sys.exit(subprocess.call(cmd))


def cmd_nombre(a):
    from nombres import nombre
    unidades = a.unidades
    if unidades and len(unidades) == 1 and not unidades[0].isdigit():
        unidades = unidades[0]
    elif unidades:
        unidades = [int(u) for u in unidades]
    n = nombre(a.materia, a.tipo, unidades or None, a.modo, a.formato, subtipo=a.subtipo, detalle=a.detalle, tema=a.tema)
    print(n)


def cmd_entorno(_):
    import entorno
    sys.exit(subprocess.call([sys.executable, os.path.join(RAIZ, "herramientas", "entorno.py")]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def comunes(p, con_salida=True):
        p.add_argument("--sin-espejo", action="store_true", help="documento solo digital: margenes iguales en todas las hojas")
        if con_salida:
            p.add_argument("--salida", choices=["html", "html+pdf", "pdf"], default="html")
            p.add_argument("--carpeta", required=True, help="carpeta de salida")
            p.add_argument("--nombre", help="nombre base del archivo (el de nombres.py)")

    p = sub.add_parser("resumen")
    p.add_argument("md")
    p.add_argument("--formato", choices=["completo", "a4", "diapositivas"], required=True)
    p.add_argument("--modo", choices=["extenso", "corto"], required=True)
    p.add_argument("--indice", action="store_true")
    p.add_argument("--practica", action="store_true")
    comunes(p)
    p.set_defaults(f=cmd_resumen)

    p = sub.add_parser("material")
    p.add_argument("md")
    comunes(p)
    p.set_defaults(f=cmd_material)

    p = sub.add_parser("tp")
    p.add_argument("md")
    p.add_argument("--datos", help="JSON de caratula")
    comunes(p)
    p.set_defaults(f=cmd_tp)

    p = sub.add_parser("docx")
    p.add_argument("md")
    p.add_argument("--tipo", choices=["tp", "resumen", "parcial", "soluciones"], default="resumen")
    p.add_argument("--modo", choices=["extenso", "corto"])
    p.add_argument("--datos")
    p.add_argument("--indice", action="store_true")
    p.add_argument("--practica", action="store_true")
    p.add_argument("-o", required=True, help="archivo .docx de salida")
    comunes(p, con_salida=False)
    p.set_defaults(f=cmd_docx)

    p = sub.add_parser("nombre")
    p.add_argument("materia")
    p.add_argument("tipo")
    p.add_argument("--unidades", nargs="*")
    p.add_argument("--modo")
    p.add_argument("--formato")
    p.add_argument("--subtipo")
    p.add_argument("--detalle")
    p.add_argument("--tema")
    p.set_defaults(f=cmd_nombre)

    p = sub.add_parser("entorno")
    p.set_defaults(f=cmd_entorno)

    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
