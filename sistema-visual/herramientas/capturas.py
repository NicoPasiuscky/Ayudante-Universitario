"""capturas.py - todas las capturas de verificacion del sistema v4, con Firefox
sin interfaz (herramientas/captura_espera.py). Los margenes de la hoja impresa
(regla 22) ya no salen de aca: los mide verificar_margenes.py sobre los PDF que
imprime imprimir_a4.py.

Uso:  python herramientas/capturas.py        (tarda unos 4 minutos)
      python herramientas/capturas.py --solo-impresion     hojas A4 (resumenes y material) y sus medidas
      python herramientas/capturas.py --solo-diapositivas  capturas y medidas de las diapositivas (solo pantalla)
      python herramientas/capturas.py --solo-indice

Salida en capturas/:
  resumen-completo-extenso-escritorio / -oscuro      HTML completo, compu y modo oscuro
  resumen-completo-corto-celular                     HTML completo, modo corto, celular de 390 px
  resumen-a4-extenso-hoja<n>, resumen-a4-corto-hoja<n>   cada hoja del A4 recortada por su caja real
  resumen-a4-oscuro-hoja1                            la vista A4 en pantalla con el modo oscuro
  resumen-boton-oscuro                               modo oscuro elegido con el boton (sistema claro)
  resumen-practica                                   componentes opcionales de practica
  diapositivas-portada, -escritorio-claro, -escritorio-oscuro, -celular-vertical, -celular-horizontal,
  diapositivas-general (vista general)
  cuestionario-*                                     inicio, pregunta, confirmacion, resultado, parcial, celular
  parcial-hoja<n>, soluciones-resultados-hoja<n>, soluciones-resolucion-hoja<n>, tp-hoja<n>                                   cada hoja del material A4 recortada por su caja real
  gris-*                                             prueba en escala de grises (regla 16)
  indice-escritorio, indice-celular
  medidas.json                                       caracteres por linea, cuerpo e interlineado (regla 15),
                                                     y las
                                                     medidas de las diapositivas en tres tamanos (reglas 24 y 25)
                                                     que lee verificar_reglas.py
"""
import base64
import json
import os
import pathlib
import shutil
import sys
import tempfile
import time

sys.dont_write_bytecode = True
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
from captura_espera import Firefox  # noqa: E402
import verificar_margenes as vm  # noqa: E402
import pymupdf  # noqa: E402
from PIL import Image, ImageOps  # noqa: E402

K = os.path.join(RAIZ, "capturas")
os.makedirs(K, exist_ok=True)
DEMO = os.path.join(RAIZ, "demo")


def d(n):
    return os.path.join(DEMO, n)


def k(n):
    return os.path.join(K, n)


PAGINADO = "document.documentElement.dataset.paginado=='1'"
EMPEZAR = "document.getElementById('btnStart').click();"
PARCIAL = "document.querySelector('input[name=modo][value=parcial]').click();"
PARCIAL_1MIN = (PARCIAL + "var i=document.getElementById('minLibre');i.value='1';"
                "i.dispatchEvent(new Event('input'));" + EMPEZAR +
                "document.querySelectorAll('#qOptions input')[1].click();")
MARCAR = EMPEZAR + "document.querySelectorAll('#qOptions input')[1].click();"
CONFIRMAR = MARCAR + "document.getElementById('btnFinish').click();"
# Responde con errores de los tres tipos: una incorrecta, una seleccion
# multiple incompleta y una sin responder
RESOLVER = (EMPEZAR +
            "var n=document.querySelectorAll('.navdot').length;"
            "for(var i=0;i<n;i++){var o=document.querySelectorAll('#qOptions input');"
            " var tipo=document.getElementById('qTypeBadge').textContent;"
            " if(i<n-1){ if(tipo=='selección múltiple'){o[0].click();} else {o[(i+1)%o.length].click();} }"
            " document.getElementById('btnNext').click();}"
            "document.getElementById('btnFinish').click();"
            "if(!document.getElementById('confirmModal').hidden) document.getElementById('btnModalConfirm').click();")

# Medidas tipograficas reales (regla 15): ancho de la columna de texto,
# caracteres por linea estimados con el ancho medio de la letra real,
# cuerpo e interlineado computados.
MEDIR = """
var ps = Array.from(document.querySelectorAll('.libro .enunciado > p'));
var p = ps.filter(function(e){ return !e.closest('.par-texto'); })[0] || ps[0];
var cs = getComputedStyle(p);
var mm = function(e){ return e ? Math.round(e.getBoundingClientRect().width * 25.4 / 96 * 10) / 10 : null; };
var pt = document.querySelector('.par-texto'), pn = document.querySelector('.par-notas'), fc = document.querySelector('figcaption');
var c = document.createElement('canvas').getContext('2d');
c.font = cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily;
var muestra = 'La velocidad promedio de una partícula es su desplazamiento dividido entre el intervalo de tiempo durante el que ocurre.';
var ancho = c.measureText(muestra).width / muestra.length;
var col = p.getBoundingClientRect().width;
return {ancho_columna_px: Math.round(col), cuerpo_px: parseFloat(cs.fontSize),
        interlineado: Math.round(parseFloat(cs.lineHeight) / parseFloat(cs.fontSize) * 100) / 100,
        caracteres_por_linea: Math.round(col / ancho),
        ancho_texto_mm: mm(p), ancho_cuerpo_con_nota_mm: mm(pt), ancho_nota_mm: mm(pn), ancho_epigrafe_mm: mm(fc)};
"""


def cajas_a4(ff):
    return ff.js("return Array.from(document.querySelectorAll('.pagedjs_page')).map(function(p){"
                 "var r=p.getBoundingClientRect();return [r.left+window.scrollX,r.top+window.scrollY,r.width,r.height];});")


def recortar_hojas(png, cajas, prefijo):
    im = Image.open(png).convert("RGB")
    for i, (x, y, w, h) in enumerate(cajas, 1):
        im.crop((int(x) - 10, int(y) - 10, int(x + w) + 10, int(y + h) + 10)).save(k(f"{prefijo}-hoja{i}.png"))
    return len(cajas)


def gris(nombre):
    ImageOps.grayscale(Image.open(k(nombre + ".png")).convert("RGB")).save(k("gris-" + nombre + ".png"))


def solo_indice():
    """Despues de reconstruir indice.html con las miniaturas nuevas."""
    with Firefox("claro") as ff:
        ff.capturar(os.path.join(RAIZ, "indice.html"), k("indice-escritorio.png"), 1280, 900)
        ff.capturar(os.path.join(RAIZ, "indice.html"), k("indice-celular.png"), 390, 844, celular=True)


# ---------------------------------------------------------------------------
# Diapositivas: medidas en tres tamanos (regla 24 y 25) y capturas
# ---------------------------------------------------------------------------
TAMANOS = [("escritorio", 1280, 720), ("celular vertical", 390, 844), ("celular horizontal", 844, 390)]

# Por cada diapositiva: se activa, se mide si necesita desplazarse (con los
# plegables cerrados), se abren los plegables y se busca todo lo que sobresale
# a los costados fuera de un bloque que se desplace a lo ancho, la letra
# minima (texto de la diapositiva y de la barra; en las figuras, con la escala
# del SVG) y el contraste real entre el color del texto y el de su fondo.
JS_DIAPOSITIVAS = """
var diaps = Array.prototype.slice.call(document.querySelectorAll('.diapositiva'));
var o = {diapositivas: diaps.length, desbordan: [], desplazan_vertical: 0, desplazan_horizontal: 0,
         letra_min: 999, letra_min_donde: '', contraste_min: 99, contraste_donde: ''};
function num(s) { return (s.match(/[\\d.]+/g) || []).map(Number); }
function lum(c) {
  var a = c.slice(0, 3).map(function (v) { v = v / 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); });
  return .2126 * a[0] + .7152 * a[1] + .0722 * a[2];
}
function fondo(el) {
  while (el) {
    var m = num(window.getComputedStyle(el).backgroundColor);
    if (m.length >= 3 && (m.length < 4 || m[3] > .5)) return m;
    el = el.parentElement;
  }
  return [255, 255, 255];
}
function enDesplazable(el, tope) {
  for (var p = el.parentElement; p && p !== tope; p = p.parentElement) {
    var ox = window.getComputedStyle(p).overflowX;
    if ((ox === 'auto' || ox === 'scroll') && p.scrollWidth > p.clientWidth + 1) return true;
  }
  return false;
}
function textos(raiz) {
  var w = document.createTreeWalker(raiz, 4), n;
  while ((n = w.nextNode())) {
    if (!n.textContent.trim()) continue;
    var el = n.parentElement;
    if (!el) continue;
    var rg = document.createRange(); rg.selectNodeContents(n);
    var rc = rg.getBoundingClientRect();
    if (rc.width === 0 || rc.height === 0) continue;
    var cs = window.getComputedStyle(el), fs = parseFloat(cs.fontSize);
    var sv = el.closest('svg');
    if (sv && el.getScreenCTM) { var m = el.getScreenCTM(); if (m) fs = fs * m.a; }
    if (!el.closest('math') && !el.closest('.solo-lectura') && fs < o.letra_min) {
      o.letra_min = Math.round(fs * 10) / 10; o.letra_min_donde = n.textContent.trim().slice(0, 30);
    }
    var l1 = lum(num(cs.color)), l2 = lum(fondo(el));
    var r = (Math.max(l1, l2) + .05) / (Math.min(l1, l2) + .05);
    if (r < o.contraste_min) { o.contraste_min = Math.round(r * 100) / 100; o.contraste_donde = n.textContent.trim().slice(0, 30); }
  }
}
diaps.forEach(function (d, i) {
  diaps.forEach(function (x) { x.removeAttribute('data-activa'); });
  d.setAttribute('data-activa', '');
  var pleg = Array.prototype.slice.call(d.querySelectorAll('details'));
  pleg.forEach(function (x) { x.open = false; });
  if (d.scrollHeight > d.clientHeight + 1) o.desplazan_vertical++;
  pleg.forEach(function (x) { x.open = true; });
  var R = d.getBoundingClientRect();
  if (d.scrollWidth > d.clientWidth + 1) o.desbordan.push((i + 1) + ': la diapositiva');
  Array.prototype.forEach.call(d.querySelectorAll('*'), function (el) {
    var r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) return;
    if ((r.right > R.right + 1 || r.left < R.left - 1) && !enDesplazable(el, d)) o.desbordan.push((i + 1) + ': ' + el.tagName + '.' + el.className);
    if (el.scrollWidth > el.clientWidth + 1) {
      var ox = window.getComputedStyle(el).overflowX;
      if ((ox === 'auto' || ox === 'scroll') && el !== d) o.desplazan_horizontal++;
    }
  });
  textos(d);
  pleg.forEach(function (x) { x.open = false; });
});
var ui = document.querySelector('.deck-ui');
if (ui) { textos(ui); if (ui.scrollWidth > ui.clientWidth + 1) o.desbordan.push('barra de navegacion'); }
o.desbordan = o.desbordan.slice(0, 8);
return o;
"""


def medir_diapositivas(medidas):
    """Regla 24 (nada desborda en los tres tamanos) y 25 (letra minima y contraste)."""
    res = {}
    for tema in ("claro", "oscuro"):
        with Firefox(tema) as ff:
            for modo in ("extenso", "corto"):
                for nombre, w, h in TAMANOS:
                    if tema == "oscuro" and nombre != "escritorio":
                        continue
                    res[f"{modo}, {nombre}, {tema}"] = ff.medir(d(f"resumen-{modo}-diapositivas.html"), w, h, JS_DIAPOSITIVAS)
    medidas["diapositivas"] = res


def capturar_diapositivas():
    """Seis capturas representativas: portada, escritorio claro y oscuro,
    celular vertical y horizontal y la vista general."""
    ext, cor = d("resumen-extenso-diapositivas.html"), d("resumen-corto-diapositivas.html")
    ir = lambda n: f"window.location.hash='{n}';"  # noqa: E731
    with Firefox("claro") as ff:
        ff.capturar(ext, k("diapositivas-portada.png"), 1280, 720, completa=False, celular=True, guion=ir(1))
        ff.capturar(ext, k("diapositivas-escritorio-claro.png"), 1280, 720, completa=False, celular=True, guion=ir(6))
        ff.capturar(cor, k("diapositivas-celular-vertical.png"), 390, 844, completa=False, celular=True, guion=ir(6))
        ff.capturar(cor, k("diapositivas-celular-horizontal.png"), 844, 390, completa=False, celular=True, guion=ir(5))
    with Firefox("oscuro") as ff:
        ff.capturar(ext, k("diapositivas-escritorio-oscuro.png"), 1280, 720, completa=False, celular=True,
                    guion=ir(9) + "setTimeout(function(){document.querySelector('.diapositiva[data-activa] summary').click();},300);",
                    pausa_guion=1.2)
        ff.capturar(ext, k("diapositivas-general.png"), 1280, 720, completa=False, celular=True,
                    guion=ir(4) + "setTimeout(function(){document.getElementById('dGeneral').click();},300);", pausa_guion=1.2)
    gris("diapositivas-escritorio-claro")


def a4_de(ff, archivo, prefijo, sufijo, medidas):
    """Hojas A4 recortadas, medidas tipograficas y recuadros por hoja de un resumen A4."""
    tmp = k("_a4.png")
    ff.capturar(d(archivo), tmp, 1000, 1200, esperar=PAGINADO)
    for f in [x for x in os.listdir(K) if x.startswith(prefijo + "-hoja")]:
        os.remove(k(f))
    n = recortar_hojas(tmp, cajas_a4(ff), prefijo)
    os.remove(tmp)
    medidas["A4" + sufijo] = ff.js(MEDIR)
    medidas["A4" + sufijo]["hojas"] = n
    # Regla 12: recuadros (formula clave) por hoja
    medidas["A4" + sufijo]["recuadros_por_hoja"] = ff.js(
        "return Array.from(document.querySelectorAll('.pagedjs_page')).map(function(p){"
        "return p.querySelectorAll('.clave:not([data-split-from])').length;});")


MATERIAL = ("parcial", "soluciones-resultados", "soluciones-resolucion", "tp")


def capturar_material(ff, medidas):
    """Cada hoja del material A4 (parcial, soluciones, TP), recortada por su caja real."""
    tmp = k("_m.png")
    for nombre in MATERIAL:
        ff.capturar(d(nombre + ".html"), tmp, 1000, 1200, esperar=PAGINADO)
        for f in [x for x in os.listdir(K) if x.startswith(nombre + "-hoja")]:
            os.remove(k(f))
        medidas[nombre + ", hojas"] = recortar_hojas(tmp, cajas_a4(ff), nombre)
    os.remove(tmp)
    for clave in [x for x in medidas if x.startswith("margenes A4") or x.endswith(".pdf, hojas")]:
        del medidas[clave]   # restos de cuando los margenes salian del DOM y el material era PDF


def main():
    medidas = {}
    with Firefox("claro") as ff:
        ff.capturar(d("resumen-extenso-completo.html"), k("resumen-completo-extenso-escritorio.png"), 1280, 900)
        medidas["completo, compu"] = ff.js(MEDIR)
        ff.capturar(d("resumen-corto-completo.html"), k("resumen-completo-corto-celular.png"), 390, 844, celular=True)
        a4_de(ff, "resumen-extenso-a4.html", "resumen-a4-extenso", "", medidas)
        a4_de(ff, "resumen-corto-a4.html", "resumen-a4-corto", " corto", medidas)
        capturar_material(ff, medidas)
        # Boton: con el sistema en claro, se elige oscuro y se recarga (se recuerda)
        ff.capturar(d("resumen-extenso-completo.html"), k("resumen-boton-oscuro.png"), 1280, 900, completa=False,
                    guion="document.getElementById('temaBoton').click();")
        ff.cmd("WebDriver:Refresh", {})
        ff.esperar("document.readyState=='complete'")
        medidas["boton: tema recordado despues de recargar"] = ff.js("return document.documentElement.getAttribute('data-theme');")
        ff.js("try{localStorage.removeItem('estudio-v4-tema')}catch(e){} return 1;")
        ff.capturar(d("resumen-extenso-completo-con-practica.html"), k("resumen-practica.png"), 1280, 900, completa=False,
                    guion="document.querySelector('.practica').scrollIntoView(); window.scrollBy(0,-120);")
        ff.capturar(os.path.join(RAIZ, "indice.html"), k("indice-escritorio.png"), 1280, 900)
        ff.capturar(os.path.join(RAIZ, "indice.html"), k("indice-celular.png"), 390, 844, celular=True)
    with Firefox("oscuro") as ff:
        ff.capturar(d("resumen-extenso-completo.html"), k("resumen-completo-extenso-oscuro.png"), 1280, 900)
        ff.capturar(d("cuestionario.html"), k("cuestionario-inicio.png"), 1280, 1280, completa=False, guion=PARCIAL)
        ff.capturar(d("cuestionario.html"), k("cuestionario-pregunta.png"), 1280, 860, completa=False, guion=MARCAR)
        ff.capturar(d("cuestionario.html"), k("cuestionario-confirmar.png"), 1280, 860, completa=False, guion=CONFIRMAR)
        ff.capturar(d("cuestionario.html"), k("cuestionario-resultado.png"), 1280, 900, guion=RESOLVER,
                    antes="try{localStorage.clear()}catch(e){}")
        ff.capturar(d("cuestionario.html"), k("cuestionario-parcial-poco-tiempo.png"), 1280, 860, completa=False,
                    guion=PARCIAL_1MIN, antes="try{localStorage.clear()}catch(e){}", pausa_guion=50)
        ff.capturar(d("cuestionario.html"), k("cuestionario-parcial-resultado.png"), 1280, 900,
                    guion=PARCIAL + RESOLVER, antes="try{localStorage.clear()}catch(e){}")
        ff.capturar(d("cuestionario.html"), k("cuestionario-celular-parcial.png"), 390, 844, completa=False,
                    celular=True, guion=PARCIAL + MARCAR, antes="try{localStorage.clear()}catch(e){}")
        ff.capturar(d("cuestionario.html"), k("cuestionario-celular-pregunta.png"), 390, 844, completa=False,
                    celular=True, guion=MARCAR)
        ff.capturar(d("cuestionario.html"), k("cuestionario-celular-resultado.png"), 390, 844, celular=True,
                    guion=RESOLVER)
    capturar_diapositivas()
    medir_diapositivas(medidas)
    for n in ("resumen-a4-extenso-hoja2", "resumen-a4-extenso-hoja3", "resumen-a4-corto-hoja1", "cuestionario-resultado",
              "parcial-hoja1", "soluciones-resultados-hoja1", "soluciones-resolucion-hoja2",
              "resumen-completo-extenso-oscuro"):
        if os.path.exists(k(n + ".png")):
            gris(n)
    with open(k("medidas.json"), "w", encoding="utf-8") as f:
        json.dump(medidas, f, ensure_ascii=False, indent=1)
    print(json.dumps({x: medidas[x] for x in medidas if x in ("A4", "A4 corto", "diapositivas")}, ensure_ascii=False, indent=1))
    print(len([x for x in os.listdir(K) if x.endswith(".png")]), "capturas en capturas/")


def solo_impresion():
    """Solo lo que depende de la hoja impresa: hojas A4 de los dos modos (con
    sus medidas) y el material A4 (parcial, soluciones, TP). Conserva el resto de medidas.json. Para no rehacer
    capturas de pantalla que no cambiaron. Los margenes (regla 22) los mide
    verificar_margenes.py sobre los PDF de imprimir_a4.py."""
    ruta = k("medidas.json")
    medidas = json.load(open(ruta, encoding="utf-8")) if os.path.exists(ruta) else {}
    with Firefox("claro") as ff:
        a4_de(ff, "resumen-extenso-a4.html", "resumen-a4-extenso", "", medidas)
        a4_de(ff, "resumen-corto-a4.html", "resumen-a4-corto", " corto", medidas)
        capturar_material(ff, medidas)
    for n in ("resumen-a4-extenso-hoja2", "resumen-a4-extenso-hoja3", "resumen-a4-corto-hoja1", "parcial-hoja1",
              "soluciones-resultados-hoja1", "soluciones-resolucion-hoja2"):
        if os.path.exists(k(n + ".png")):
            gris(n)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(medidas, f, ensure_ascii=False, indent=1)
    print(json.dumps({x: medidas[x] for x in ("A4", "A4 corto")}, ensure_ascii=False))


def solo_diapositivas():
    """Solo las diapositivas: capturas y medidas de los tres tamanos."""
    ruta = k("medidas.json")
    medidas = json.load(open(ruta, encoding="utf-8")) if os.path.exists(ruta) else {}
    capturar_diapositivas()
    medir_diapositivas(medidas)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(medidas, f, ensure_ascii=False, indent=1)
    print(json.dumps({x: medidas[x] for x in ("diapositivas",)}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    if "--solo-indice" in sys.argv:
        solo_indice()
    elif "--solo-impresion" in sys.argv:
        solo_impresion()
    elif "--solo-diapositivas" in sys.argv:
        solo_diapositivas()
    else:
        main()
