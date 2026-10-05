"""captura_docx.py - abre un .docx en Microsoft Word (sin interfaz, solo
lectura; en macOS y Linux, o sin Word, usa LibreOffice), lo exporta a PDF y saca una captura PNG por hoja. Sirve para mirar
de verdad como queda un .docx y para comprobar la incrustacion de fuentes: la
lista de fuentes del PDF dice con que letra dibujo Word cada texto (si
aparece "EstudioSans" sin tenerla instalada en Windows, Word uso la fuente
incrustada en el .docx).

Uso:
    python herramientas/captura_docx.py TP.docx CARPETA [--prefijo tp] [--ppp 110] [--pdf salida.pdf]

No toca el .docx. Si Word ya estaba abierto, no lo cierra: solo cierra el
documento que abrio. El PDF intermedio va a la carpeta temporal, salvo que se
pida con --pdf.
"""
import argparse
import os
import subprocess
import sys
import tempfile

import pymupdf

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PS = r"""
$ErrorActionPreference = 'Stop'
$yaAbierto = @(Get-Process WINWORD -ErrorAction SilentlyContinue).Count -gt 0
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
  $d = $w.Documents.Open('%(docx)s', $false, $true, $false)
  $d.Repaginate()
  $d.ExportAsFixedFormat('%(pdf)s', 17)
  Write-Output ("hojas: " + $d.ComputeStatistics(2))
  $d.Close(0)
} finally {
  if (-not $yaAbierto) { $sc = 0; $w.Quit([ref]$sc) }
  [System.Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
}
"""


def exportar_libreoffice(docx, pdf):
    """Alternativa sin Word: LibreOffice sin interfaz. Mismo resultado para revisar el .docx, aunque
    puede dibujar algun detalle distinto de Word (campos como STYLEREF)."""
    import entorno
    soffice = entorno.soffice()
    if not soffice:
        raise SystemExit("No hay Word ni LibreOffice para revisar el .docx. Instala LibreOffice o define ESTUDIO_SOFFICE.")
    with tempfile.TemporaryDirectory() as tmp:
        p = subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", tmp, os.path.abspath(docx)],
                           capture_output=True, text=True, timeout=240)
        generado = os.path.join(tmp, os.path.splitext(os.path.basename(docx))[0] + ".pdf")
        if p.returncode or not os.path.exists(generado):
            raise SystemExit("LibreOffice no pudo exportar el PDF:\n" + p.stdout + p.stderr)
        os.replace(generado, pdf) if os.path.splitdrive(pdf)[0] == os.path.splitdrive(generado)[0] else (
            open(pdf, "wb").write(open(generado, "rb").read()))
    return "exportado con LibreOffice"


def exportar(docx, pdf):
    if sys.platform != "win32" or not __import__("shutil").which("powershell"):
        return exportar_libreoffice(docx, pdf)
    script = PS % {"docx": os.path.abspath(docx).replace("'", "''"), "pdf": os.path.abspath(pdf).replace("'", "''")}
    p = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                       capture_output=True, text=True, timeout=240)
    if p.returncode or not os.path.exists(pdf):
        # Sin Word instalado (o con error de COM), se prueba con LibreOffice
        return exportar_libreoffice(docx, pdf)
    return p.stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docx")
    ap.add_argument("carpeta")
    ap.add_argument("--prefijo", default=None)
    ap.add_argument("--ppp", type=int, default=110)
    ap.add_argument("--pdf", default=None)
    a = ap.parse_args()
    os.makedirs(a.carpeta, exist_ok=True)
    prefijo = a.prefijo or os.path.splitext(os.path.basename(a.docx))[0]
    with tempfile.TemporaryDirectory() as tmp:
        pdf = a.pdf or os.path.join(tmp, "word.pdf")
        print(exportar(a.docx, pdf))
        d = pymupdf.open(pdf)
        fuentes = sorted({f[3] for pg in d for f in pg.get_fonts()})
        print("fuentes en el PDF de Word:", ", ".join(fuentes))
        for i, pg in enumerate(d, 1):
            ruta = os.path.join(a.carpeta, f"{prefijo}-hoja{i}.png")
            pg.get_pixmap(dpi=a.ppp).save(ruta)
            print(ruta)
        d.close()


if __name__ == "__main__":
    main()
