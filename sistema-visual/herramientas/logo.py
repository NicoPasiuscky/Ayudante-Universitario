"""logo.py - logo opcional de la caratula del TP (Word y HTML A4).

El JSON de datos del TP puede traer, dentro de "caratula":
    "logo": "ruta/al/logo.png"     ruta absoluta o relativa al JSON
    "logo_alto_cm": 2.2            opcional; por defecto 2,2 cm, maximo 4 cm

`preparar` valida el archivo, calcula el ancho respetando la proporcion y deja una copia
en la carpeta de trabajo (el original, por ejemplo el de Drive, nunca se toca ni se mueve).
Devuelve None si el JSON no pide logo.
"""
import json
import os
import shutil

ALTO_DEFECTO_CM = 2.2
ALTO_MAXIMO_CM = 4.0
ANCHO_MAXIMO_CM = 16.0      # area util de 180 mm menos aire


def preparar(datos, destino):
    if not datos:
        return None
    with open(datos, encoding="utf-8-sig") as f:
        car = json.load(f).get("caratula", {})
    ruta = str(car.get("logo", "")).strip()
    if not ruta:
        return None
    if not os.path.isabs(ruta):
        ruta = os.path.join(os.path.dirname(os.path.abspath(datos)), ruta)
    if not os.path.isfile(ruta):
        raise SystemExit("logo: no existe " + ruta)
    from PIL import Image
    with Image.open(ruta) as im:
        w, h = im.size
    alto = min(float(car.get("logo_alto_cm", ALTO_DEFECTO_CM)), ALTO_MAXIMO_CM)
    ancho = alto * w / h
    if ancho > ANCHO_MAXIMO_CM:
        ancho = ANCHO_MAXIMO_CM
        alto = ancho * h / w
    copia = os.path.join(destino, "logo" + os.path.splitext(ruta)[1].lower())
    shutil.copyfile(ruta, copia)
    return {"ruta": copia.replace("\\", "/"), "alto_cm": alto, "ancho_cm": ancho}
