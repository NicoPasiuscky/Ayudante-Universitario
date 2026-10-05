"""construir.py - reproduce todo el sistema v4 desde las fuentes (Markdown, JSON,
CSS, filtro y plantillas). Documentado en LEEME.md, seccion "Como se usa".

Uso (desde cualquier carpeta):
    python construir.py              resumenes, cuestionario, material A4, indice y verificacion
    python construir.py --fuentes    ademas regenera fonts/web e incluir/fuentes.html
    python construir.py --capturas   ademas saca todas las capturas de Firefox y exporta el
                                     .docx con Word (tarda ~5 min)
    python construir.py --pdf        ademas deja en el directorio temporal el PDF de cada hoja A4
                                     (verificacion; el PDF de entrega lo arma imprimir_a4.entregar)

Pasos:
  1. (--fuentes) herramientas/construir_fuentes.py
  2. demo/figuras/generar_figuras.py            figura 3-1 y figura del parcial en SVG
  3. Pandoc: demo/resumen-extenso.md y demo/resumen-corto.md en los 3 formatos (6 combos),
     mas una variante con practica
  4. cuestionario/construir_plantilla.py y demo/construir_cuestionario.py
  5. demo/material/*.md -> demo/*.html           parcial y las dos hojas de soluciones en HTML A4
                                                 (Pandoc + material.lua + Paged.js);
                                                 demo/material/calculos.py recalcula sus numeros
  6. docx/: verificacion SymPy, figuras, los reference-*.docx, el TP de demostracion y una
     demostracion por tipo de Word (resumen extenso, parcial, soluciones: resolucion)
  7. herramientas/construir_indice.py            indice.html
  8. (--capturas) herramientas/capturas.py y herramientas/captura_docx.py (Word -> PDF -> PNG)
  9. herramientas/probar_tema.py                 modo claro u oscuro medido en Firefox (reglas 32 a 34)
 10. herramientas/verificar_reglas.py            (la regla 22, margenes: imprimir_a4.py imprime cada hoja A4
                                                 a PDF con Firefox y verificar_margenes.py lo mide)

Los archivos de trabajo (PDF de verificacion, perfil de Firefox) van a la carpeta
temporal del sistema; en esta carpeta solo quedan las salidas.
"""
import os
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RAIZ, "herramientas"))
import entorno  # noqa: E402

PANDOC = entorno.pandoc()
MATHML = entorno.mathml()
PY = sys.executable
ENTORNO = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")


def r(*partes):
    return os.path.join(RAIZ, *partes)


def correr(cmd, cwd=RAIZ):
    print("  >", " ".join(os.path.basename(c) if os.path.isabs(c) else c for c in cmd[:3]), "...")
    p = subprocess.run(cmd, cwd=cwd, env=ENTORNO, capture_output=True, text=True, encoding="utf-8")
    if p.stdout.strip():
        print("   ", p.stdout.strip().replace("\n", "\n    "))
    if p.stderr.strip():
        print("   ", p.stderr.strip().replace("\n", "\n    "))
    if p.returncode:
        raise SystemExit(f"fallo: {cmd}")


def resumen(md, salida, formato, modo, indice=False, extra_meta=(), espejo=True):
    """La cadena de generar-html con el filtro y las hojas del sistema v4.
    formato: completo | a4 | diapositivas; modo: extenso | corto.
    espejo: solo Hoja A4. True (por defecto) = margenes espejados a doble faz, para imprimir;
    False = margenes iguales en todas las hojas (izquierdo 20 mm, derecho 10 mm) y "Hoja n de N"
    siempre del mismo lado, para un documento que no se imprime (metadato -M espejo=false)."""
    cmd = [PANDOC, md, "--standalone", "--embed-resources", MATHML,
           "--syntax-highlighting=pygments", "--lua-filter=" + r("incluir", "estudio.lua"),
           "-M", "formato=" + formato, "-M", "modo=" + modo,
           "--include-in-header=" + r("incluir", "fuentes.html"),
           "--css=" + r("css", "tokens.css")]
    if formato != "a4":
        # Modo claro u oscuro con boton: solo HTML completo y diapositivas. La Hoja A4 sale
        # siempre clara, sin tokens oscuros ni boton.
        cmd += ["--css=" + r("css", "tokens-oscuro.css"), "--include-before-body=" + r("incluir", "tema.html")]
    cmd += ["--css=" + r("css", "resumen-base.css"),
            "--include-after-body=" + r("incluir", "formulas-rectas.html")]
    for m in extra_meta:
        cmd += ["-M", m]
    if formato == "a4" and not espejo:
        cmd += ["-M", "espejo=false"]
    if formato == "a4":
        cmd += ["--css=" + r("css", "resumen-a4.css"),
                "--include-in-header=" + r("incluir", "a4-pagina.html"),
                "--include-in-header=" + r("incluir", "paged-init.html")]
    elif formato == "diapositivas":
        cmd += ["--css=" + r("css", "resumen-diapositivas.css"),
                "--include-after-body=" + r("incluir", "diapositivas.html")]
    else:
        cmd += ["--css=" + r("css", "resumen-pantalla.css"), "--css=" + r("css", "resumen-completo.css")]
    if indice:
        # Indice propio del filtro (nunca --toc): con enlaces en pantalla y
        # como lista simple, sin enlaces, en la hoja A4. Solo modo extenso.
        cmd += ["-M", "indice=true"]
    cmd += ["-o", salida]
    # Pandoc resuelve las imagenes contra la carpeta actual: correr en la del .md
    correr(cmd, cwd=os.path.dirname(os.path.abspath(md)))


def material(md, salida, espejo=True):
    """Material impreso en HTML A4 (parcial digitalizado, modelos y hojas de
    soluciones): Paged.js, mismos tokens y letra que el resumen A4, mas
    material.lua y material-a4.css. Si se quiere PDF, se imprime el HTML desde
    Firefox (herramientas/imprimir_a4.py lo hace sin interfaz).
    espejo=False: margenes iguales en todas las hojas (no se imprime); ver resumen()."""
    cmd = [PANDOC, md, "--standalone", "--embed-resources", MATHML,
           "--lua-filter=" + r("incluir", "material.lua"),
           "--include-in-header=" + r("incluir", "fuentes.html"),
           "--css=" + r("css", "tokens.css"), "--css=" + r("css", "material-a4.css"),
           "--include-in-header=" + r("incluir", "a4-pagina.html"),
           "--include-in-header=" + r("incluir", "paged-init.html"),
           "--include-after-body=" + r("incluir", "formulas-rectas.html"),
           "-o", salida]
    if not espejo:
        cmd[-2:-2] = ["-M", "espejo=false"]
    correr(cmd, cwd=os.path.dirname(os.path.abspath(md)))


def tp(md, salida, datos=None, espejo=True):
    """Trabajo practico en HTML A4 (Paged.js): el mismo Markdown y el mismo JSON de
    caratula que el .docx (docx/construir_docx.py), mas incluir/tp.lua y css/tp-a4.css.
    Para PDF se imprime ese HTML con herramientas/imprimir_a4.py (entregar).
    espejo=False: margenes iguales en todas las hojas (el TP no se imprime, p. ej. aula virtual)."""
    md, salida = os.path.abspath(md), os.path.abspath(salida)
    cmd = [PANDOC, md, "--standalone", "--embed-resources", MATHML,
           "--syntax-highlighting=pygments", "--lua-filter=" + r("incluir", "tp.lua")]
    if datos:
        cmd += ["--metadata-file=" + os.path.abspath(datos)]
    cmd += ["--include-in-header=" + r("incluir", "fuentes.html"),
            "--css=" + r("css", "tokens.css"), "--css=" + r("css", "tp-a4.css"),
            "--include-in-header=" + r("incluir", "a4-pagina.html"),
            "--include-in-header=" + r("incluir", "paged-init.html"),
            "--include-after-body=" + r("incluir", "formulas-rectas.html"),
            "-o", salida]
    if not espejo:
        cmd[-2:-2] = ["-M", "espejo=false"]
    # Logo opcional de la caratula (caratula.logo del JSON): copia en una carpeta temporal
    sys.path.insert(0, r("herramientas"))
    import logo as _logo
    with tempfile.TemporaryDirectory(prefix="estudio_logo_") as tmp:
        lg = _logo.preparar(datos, tmp)
        if lg:
            cmd[-2:-2] = ["-M", "logo_ruta=" + lg["ruta"], "-M", f"logo_alto_mm={lg['alto_cm'] * 10:.1f}"]
        correr(cmd, cwd=os.path.dirname(os.path.abspath(md)))


MATERIALES = ("parcial", "soluciones-resultados", "soluciones-resolucion")


def materiales():
    for nombre in MATERIALES:
        material(r("demo", "material", nombre + ".md"), r("demo", nombre + ".html"))


# (markdown, --tipo, opciones, nombre de salida) de las demostraciones de Word, una por tipo
DOCX_DEMOS = [(("demo", "resumen-extenso.md"), "resumen", ["--modo", "extenso", "--indice"], "resumen-extenso"),
              (("demo", "material", "parcial.md"), "parcial", [], "parcial"),
              (("demo", "material", "soluciones-resolucion.md"), "soluciones", [], "soluciones-resolucion")]

FORMATOS = ("completo", "a4", "diapositivas")
MODOS = ("extenso", "corto")


def resumenes():
    """Los 6 combos (3 formatos x 2 modos) de la unidad de demostracion, mas
    la variante con practica del HTML completo extenso."""
    for modo in MODOS:
        md = r("demo", "resumen-" + modo + ".md")
        for formato in FORMATOS:
            # El indice solo va en HTML completo y A4, modo extenso
            resumen(md, r("demo", f"resumen-{modo}-{formato}.html"), formato, modo,
                    indice=(modo == "extenso" and formato != "diapositivas"))
    resumen(r("demo", "resumen-extenso.md"), r("demo", "resumen-extenso-completo-con-practica.html"),
            "completo", "extenso", extra_meta=("practica=true",))


def main():
    args = set(sys.argv[1:])
    if "--fuentes" in args:
        print("1. fuentes")
        correr([PY, r("herramientas", "construir_fuentes.py")])
    print("2. figuras")
    correr([PY, r("demo", "figuras", "generar_figuras.py")])
    print("3. resumenes: 3 formatos x 2 modos, mas la variante con practica")
    resumenes()
    print("4. cuestionario")
    correr([PY, r("cuestionario", "construir_plantilla.py")])
    correr([PY, r("demo", "construir_cuestionario.py")])
    print("5. material A4: parcial y soluciones")
    correr([PY, r("demo", "material", "calculos.py")])
    materiales()
    if "--pdf" in args:
        correr([PY, r("herramientas", "imprimir_a4.py"), "--todo"])
    print("5b. TP en HTML A4 (el mismo Markdown y JSON que el Word)")
    tp(r("docx", "demo", "tp-demo.md"), r("demo", "tp.html"), datos=r("docx", "demo", "tp-demo.json"))
    print("6. TP en Word (docx)")
    correr([PY, r("docx", "demo", "verificacion.py")])
    correr([PY, r("docx", "demo", "figuras.py")])
    correr([PY, r("docx", "construir_docx.py"), "--referencia", r("docx", "demo", "tp-demo.md"),
            "--datos", r("docx", "demo", "tp-demo.json"), "--chequeo"])
    for md, tipo, extra, salida in DOCX_DEMOS:
        correr([PY, r("docx", "construir_docx.py"), r(*md), "--tipo", tipo, "-o", r("docx", "demo", salida + ".docx"),
                "--chequeo"] + extra)
    print("7. indice")
    correr([PY, r("herramientas", "construir_indice.py")])
    if "--capturas" in args:
        print("8. capturas")
        correr([PY, r("herramientas", "capturas.py")])
        # el .docx se exporta con Word (hace falta Microsoft Word instalado)
        correr([PY, r("herramientas", "captura_docx.py"), r("docx", "demo", "tp-demo.docx"),
                r("docx", "capturas"), "--prefijo", "tp-demo", "--pdf", r("docx", "demo", "tp-demo.pdf")])
        for _, _, _, salida in DOCX_DEMOS:
            correr([PY, r("herramientas", "captura_docx.py"), r("docx", "demo", salida + ".docx"),
                    r("docx", "capturas"), "--prefijo", salida, "--pdf", r("docx", "demo", salida + ".pdf")])
        # el indice lleva miniaturas de las capturas: se rearma y se vuelve a capturar
        correr([PY, r("herramientas", "construir_indice.py")])
        correr([PY, r("herramientas", "capturas.py"), "--solo-indice"])
    print("9. modo claro u oscuro en Firefox (HTML completo y diapositivas con boton; A4 y material siempre claros)")
    correr([PY, r("herramientas", "probar_tema.py")])
    print("10. verificacion de reglas (incluye la 22, margenes, y la 32 a 34, tema claro u oscuro)")
    correr([PY, r("herramientas", "verificar_reglas.py")])


if __name__ == "__main__":
    main()
