"""nombres.py - nombre de todo archivo nuevo del proyecto (resumenes, cuestionarios, TP,
parciales y soluciones). UN solo modulo: todo archivo nuevo se nombra con
`nombre(...)`, nunca a mano.

Formato :

    [Nombre completo de la materia] ｜ [Tipo]꞉ Unidad x [｜ modo ｜ formato] [｜ Soluciones꞉ tipo]

Windows y Google Drive para escritorio no admiten `|` ni `:` en nombres de archivo; por eso se usan dos reemplazos parecidos que si se permiten:
    BARRA       U+FF5C  barra vertical de ancho completo   ｜  (un espacio a cada lado)
    DOSPUNTOS   U+A789  dos puntos de letra modificadora   ꞉  (un espacio despues)
Si algun dia hay que cambiarlos, se cambia SOLO aca (las dos constantes).

Ejemplos:
    Materia B ｜ Resumen꞉ Unidad 1 a 4 ｜ corto ｜ hoja A4.html
    Materia B ｜ Resumen꞉ Unidad 1 a 4 ｜ corto ｜ hoja A4.pdf   (mismo nombre base)
    Materia B ｜ Resumen꞉ Unidad 1 a 4 ｜ corto.md              (fuente: modo, sin formato)
    Materia A ｜ Parcial práctico꞉ Unidad 1 a 3 ｜ Soluciones꞉ resultados.html
    Materia A ｜ Resumen de tema corto ｜ corto ｜ hoja A4.html          (tema corto, no unidades)
    Materia A ｜ Tabla de fórmulas.pdf                              (sin modo ni formato: largo fijo, hoja A4)

Tipos: Resumen; Cuestionario teórico | práctico; Cuestionario (sin apellido: un solo banco que mezcla teoría y
cálculo, ); Trabajo práctico; Parcial teórico | práctico
(tambien los parciales para practicar).
Tema corto : cuando lo que se resume es un tema corto y no una o
varias unidades, el nombre no lleva "Unidad x": `Resumen de [tema]` (tipo="Resumen" con tema=) o
`Tabla de fórmulas` (tipo="Tabla de fórmulas", tema= opcional: "Tabla de fórmulas de [tema]").
Siguen siendo resumenes (flujo resumir). El mini resumen (`Resumen de [tema]`) lleva modo y formato
como cualquier resumen. La Tabla de fórmulas NO lleva sufijo de modo ni de formato: siempre
tiene un largo definido (todas las formulas de esos temas) y siempre es hoja A4; la extension
(.html, .pdf o .docx) distingue el archivo. No es un tipo de documento aparte: es solo una
forma de nombrar un resumen.
Soluciones (`subtipo`): resultados | resolución, al final, separado por ｜.
Solo los resumenes (y el mini resumen de un tema) llevan sufijo: modo (extenso | corto) y formato
(hoja A4 | pantalla | diapositivas | Word). Cuestionarios, TP, parciales y soluciones no llevan sufijo de
modo ni de formato: la extension distingue HTML, PDF y docx. El cuestionario es solo HTML (y su banco .json, que es la fuente).

Parametros de nombre():
    materia    nombre completo ("Materia B")
    tipo       uno de los tipos de arriba (sin tildes tambien vale)
    unidades   3, [1, 2, 3, 4] (rango "Unidad 1 a 4"), [1, 3] ("Unidad 1 y 3"), "1 a 4" o None
    modo       "extenso" | "corto" (solo resumen; obligatorio en resumen)
    formato    "hoja A4" | "pantalla" | "diapositivas" | "Word" (solo resumen; None = el .md fuente)
    subtipo    "resultados" | "resolución" (hojas de soluciones)
    detalle    (extra) distingue piezas del mismo tipo, por ejemplo "modelo A";
               va justo despues de las unidades
    tema       tema corto de un resumen ("tema corto"); con el, `unidades` tiene que ser None

Devuelve un objeto `Nombre` (es un str: el nombre base, sin extension) con:
    .archivo("html")          -> nombre con extension
    .ruta(carpeta, "pdf")     -> ruta completa; valida que la extension corresponda a la pieza

Uso:  python nombres.py --probar      corre los casos (sale con codigo 1 si alguno falla)
      python nombres.py --ejemplos    imprime ejemplos de cada tipo
Como modulo:  from nombres import nombre, BARRA, DOSPUNTOS
"""
import os
import re
import sys
import unicodedata

sys.dont_write_bytecode = True

# ---- Los dos caracteres: un cambio futuro se hace solo aca ----
BARRA = "｜"       # ｜ barra vertical de ancho completo (reemplaza "|")
DOSPUNTOS = "꞉"   # ꞉ dos puntos de letra modificadora (reemplaza ":")
SEP = f" {BARRA} "             # un espacio a cada lado
TIPO_SEP = f"{DOSPUNTOS} "     # un espacio despues

TIPOS = ["Resumen", "Tabla de fórmulas", "Cuestionario teórico", "Cuestionario práctico", "Cuestionario",
         "Trabajo práctico", "Parcial teórico", "Parcial práctico"]
RESUMENES = ("Resumen",)      # llevan sufijo de modo y formato (la Tabla de fórmulas no: largo fijo, siempre hoja A4)
MODOS = ["extenso", "corto"]
FORMATOS = ["hoja A4", "pantalla", "diapositivas", "Word"]
SUBTIPOS = {"resultados": "resultados", "resolucion": "resolución", "resolución": "resolución"}
ALIAS_FORMATO = {"a4": "hoja A4", "hoja a4": "hoja A4", "hoja": "hoja A4", "completo": "pantalla", "html completo": "pantalla",
                 "pantalla": "pantalla", "diapositivas": "diapositivas", "word": "Word", "docx": "Word"}
# extensiones validas segun la pieza
EXT_FORMATO = {"hoja A4": ("html", "pdf"), "pantalla": ("html",), "diapositivas": ("html",), "Word": ("docx",)}
EXT_TIPO = {"Cuestionario teórico": ("html", "json"), "Cuestionario práctico": ("html", "json"),
            "Cuestionario": ("html", "json")}   # .json = banco de preguntas (fuente)
EXT_GENERAL = ("html", "pdf", "docx", "md")

INVALIDOS = set('<>:"/\\|?*') | {chr(c) for c in range(32)}
RESERVADOS = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
LARGO_MAX = 180          # sin extension; deja margen para la ruta de Drive (limite de Windows: 260)


def _sin_tildes(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


def _canon(valor, opciones, que):
    clave = _sin_tildes(valor.strip())
    for o in opciones:
        if _sin_tildes(o) == clave:
            return o
    raise ValueError(f"{que} no valido: {valor!r} (validos: {', '.join(opciones)})")


def _texto_unidades(u):
    if u is None:
        return None
    if isinstance(u, str):
        t = re.sub(r"^\s*unidades?\s*", "", u.strip(), flags=re.I)
        if not t:
            raise ValueError("unidades vacias")
        return "Unidad " + re.sub(r"\s+", " ", t)
    if isinstance(u, int):
        u = [u]
    nums = sorted(set(int(x) for x in u))
    if not nums:
        raise ValueError("unidades vacias")
    if len(nums) == 1:
        return f"Unidad {nums[0]}"
    if nums == list(range(nums[0], nums[-1] + 1)):
        return f"Unidad {nums[0]} a {nums[-1]}"
    return "Unidad " + ", ".join(map(str, nums[:-1])) + f" y {nums[-1]}"


def validar_componente(texto, que="nombre"):
    """Levanta ValueError si `texto` tiene algun caracter que Windows o Drive no admiten."""
    malos = sorted({c for c in texto if c in INVALIDOS})
    if malos:
        raise ValueError(f"{que} con caracteres invalidos en Windows: {' '.join(repr(c) for c in malos)} en {texto!r}")
    if texto != texto.strip() or texto.endswith("."):
        raise ValueError(f"{que} no puede empezar ni terminar con espacio, ni terminar con punto: {texto!r}")
    if "  " in texto:
        raise ValueError(f"{que} con espacios dobles: {texto!r}")
    if texto.split(".")[0].strip().upper() in RESERVADOS:
        raise ValueError(f"{que} reservado de Windows: {texto!r}")
    if len(texto) > LARGO_MAX:
        raise ValueError(f"{que} demasiado largo ({len(texto)} caracteres, maximo {LARGO_MAX})")
    return texto


class Nombre(str):
    """Nombre base (sin extension) de una pieza; conoce que extensiones le corresponden."""
    tipo = formato = modo = None

    def extensiones(self):
        if self.tipo in EXT_TIPO:
            return EXT_TIPO[self.tipo]
        if self.tipo in RESUMENES:
            return ("md",) if self.formato is None else EXT_FORMATO[self.formato]
        return EXT_GENERAL

    def archivo(self, ext):
        ext = ext.lstrip(".").lower()
        if ext not in self.extensiones():
            raise ValueError(f"{str(self)!r}: la extension .{ext} no corresponde (validas: "
                             f"{', '.join('.' + e for e in self.extensiones())})")
        return validar_componente(f"{self}.{ext}", "archivo")

    def ruta(self, carpeta, ext):
        return os.path.join(carpeta, self.archivo(ext))


def nombre(materia, tipo, unidades, modo=None, formato=None, subtipo=None, detalle=None, tema=None):
    """Nombre base de una pieza nueva (ver la documentacion del modulo). Levanta ValueError
    si algo no corresponde o si quedaria un caracter invalido en Windows."""
    materia = re.sub(r"\s+", " ", (materia or "").strip())
    if not materia:
        raise ValueError("falta la materia")
    tipo = _canon(tipo, TIPOS, "tipo")
    es_resumen = tipo in RESUMENES
    if tipo == "Tabla de fórmulas" and (modo is not None or formato is not None):
        raise ValueError("la Tabla de fórmulas no lleva sufijo de modo ni de formato (largo fijo, siempre hoja A4)")
    tema = re.sub(r"\s+", " ", tema.strip()) if tema else None
    if tema and tipo != "Resumen" and tipo != "Tabla de fórmulas":
        raise ValueError(f"{tipo}: `tema` solo vale para un resumen de tema corto")
    if (tema or tipo == "Tabla de fórmulas") and unidades is not None:
        raise ValueError("un tema corto (Resumen de [tema], Tabla de fórmulas) no lleva Unidad x: unidades debe ser None")
    if es_resumen:
        if modo is None:
            raise ValueError("todo resumen lleva modo (extenso o corto)")
        modo = _canon(modo, MODOS, "modo")
        if formato is not None:
            f = ALIAS_FORMATO.get(_sin_tildes(formato.strip()))
            formato = f if f else _canon(formato, FORMATOS, "formato")
    elif modo is not None or formato is not None:
        raise ValueError(f"{tipo}: no lleva sufijo de modo ni de formato (solo los resumenes)")
    if subtipo is not None:
        s = SUBTIPOS.get(_sin_tildes(subtipo))
        if s is None:
            raise ValueError(f"subtipo no valido: {subtipo!r} (validos: resultados, resolución)")
        if es_resumen:
            raise ValueError("un resumen no lleva hoja de soluciones")
        subtipo = s
    u = _texto_unidades(unidades)
    if tipo == "Tabla de fórmulas":
        cabeza = materia + SEP + tipo + (f" de {tema}" if tema else "")
    elif tema:
        cabeza = materia + SEP + f"Resumen de {tema}"
    else:
        cabeza = materia + SEP + tipo + (TIPO_SEP + u if u else "")
    piezas = [cabeza]
    if detalle:
        piezas.append(re.sub(r"\s+", " ", detalle.strip()))
    if es_resumen:
        piezas.append(modo)
        if formato:
            piezas.append(formato)
    if subtipo:
        piezas.append("Soluciones" + TIPO_SEP + subtipo)
    base = SEP.join(piezas)
    validar_componente(base, "nombre")
    n = Nombre(base)
    n.tipo, n.modo, n.formato = tipo, modo, formato
    return n


# ---------------------------------------------------------------------------
# Casos de prueba y ejemplos
# ---------------------------------------------------------------------------
B, D = BARRA, DOSPUNTOS
CASOS = [
    # (argumentos, nombre base esperado)
    (dict(materia="Materia B", tipo="Resumen", unidades=[1, 2, 3, 4], modo="corto", formato="hoja A4"),
     f"Materia B {B} Resumen{D} Unidad 1 a 4 {B} corto {B} hoja A4"),
    (dict(materia="Materia B", tipo="Resumen", unidades=[1, 2, 3, 4], modo="corto"),
     f"Materia B {B} Resumen{D} Unidad 1 a 4 {B} corto"),
    (dict(materia="Materia B", tipo="Resumen", unidades="1 a 4", modo="Extenso", formato="pantalla"),
     f"Materia B {B} Resumen{D} Unidad 1 a 4 {B} extenso {B} pantalla"),
    (dict(materia="Materia A", tipo="Resumen", unidades=3, modo="extenso", formato="diapositivas"),
     f"Materia A {B} Resumen{D} Unidad 3 {B} extenso {B} diapositivas"),
    (dict(materia="Materia A", tipo="resumen", unidades=3, modo="corto", formato="word"),
     f"Materia A {B} Resumen{D} Unidad 3 {B} corto {B} Word"),
    (dict(materia="Análisis Matemático I", tipo="Cuestionario teórico", unidades=[1, 2]),
     f"Análisis Matemático I {B} Cuestionario teórico{D} Unidad 1 a 2"),
    (dict(materia="Análisis Matemático I", tipo="cuestionario practico", unidades=5),
     f"Análisis Matemático I {B} Cuestionario práctico{D} Unidad 5"),
    (dict(materia="Materia B", tipo="Cuestionario", unidades=[1, 2, 3, 4, 5]),
     f"Materia B {B} Cuestionario{D} Unidad 1 a 5"),
    (dict(materia="Materia A", tipo="Trabajo práctico", unidades=[4]),
     f"Materia A {B} Trabajo práctico{D} Unidad 4"),
    (dict(materia="Materia A", tipo="Trabajo práctico", unidades=None),
     f"Materia A {B} Trabajo práctico"),
    (dict(materia="Materia A", tipo="Parcial práctico", unidades=[1, 2, 3], detalle="modelo A"),
     f"Materia A {B} Parcial práctico{D} Unidad 1 a 3 {B} modelo A"),
    (dict(materia="Materia A", tipo="Parcial teórico", unidades=[1, 2, 3]),
     f"Materia A {B} Parcial teórico{D} Unidad 1 a 3"),
    (dict(materia="Materia A", tipo="Parcial práctico", unidades=[1, 2, 3], subtipo="resultados"),
     f"Materia A {B} Parcial práctico{D} Unidad 1 a 3 {B} Soluciones{D} resultados"),
    (dict(materia="Materia A", tipo="Parcial práctico", unidades=[1, 2, 3], subtipo="resolucion"),
     f"Materia A {B} Parcial práctico{D} Unidad 1 a 3 {B} Soluciones{D} resolución"),
    (dict(materia="Materia A", tipo="Resumen", unidades=None, tema="tema corto", modo="corto", formato="hoja A4"),
     f"Materia A {B} Resumen de tema corto {B} corto {B} hoja A4"),
    (dict(materia="Materia A", tipo="Tabla de fórmulas", unidades=None),
     f"Materia A {B} Tabla de fórmulas"),
    (dict(materia="Materia A", tipo="tabla de formulas", unidades=None, tema="tema B"),
     f"Materia A {B} Tabla de fórmulas de tema B"),
    (dict(materia="Materia A", tipo="Resumen", unidades=None, tema="otro tema", modo="corto"),
     f"Materia A {B} Resumen de otro tema {B} corto"),
    (dict(materia="Materia A", tipo="Parcial práctico", unidades=None, detalle="modelo B", subtipo="resolución"),
     f"Materia A {B} Parcial práctico {B} modelo B {B} Soluciones{D} resolución"),
    (dict(materia="Sistemas y Procesos de Negocio", tipo="Resumen", unidades=[1, 3, 5], modo="corto", formato="hoja A4"),
     f"Sistemas y Procesos de Negocio {B} Resumen{D} Unidad 1, 3 y 5 {B} corto {B} hoja A4"),
]
ERRORES = [
    (dict(materia="Materia: A", tipo="Resumen", unidades=1, modo="corto"), "caracteres invalidos"),
    (dict(materia="Materia | A", tipo="Resumen", unidades=1, modo="corto"), "caracteres invalidos"),
    (dict(materia="Materia", tipo="Resumen", unidades=1), "modo"),
    (dict(materia="Materia", tipo="Resumen", unidades=1, modo="medio"), "modo no valido"),
    (dict(materia="Materia", tipo="Resumen", unidades=1, modo="corto", formato="pdf"), "formato no valido"),
    (dict(materia="Materia", tipo="Parcial práctico", unidades=1, modo="corto"), "no lleva sufijo"),
    (dict(materia="Materia", tipo="Examen", unidades=1), "tipo no valido"),
    (dict(materia="Materia", tipo="Resumen", unidades=1, modo="corto", subtipo="resultados"), "soluciones"),
    (dict(materia="Materia", tipo="Parcial práctico", unidades=1, subtipo="otro"), "subtipo"),
    (dict(materia="", tipo="Resumen", unidades=1, modo="corto"), "materia"),
    (dict(materia="Materia?", tipo="Resumen", unidades=1, modo="corto"), "caracteres invalidos"),
    (dict(materia="Materia", tipo="Formulario", unidades=1), "tipo no valido"),
    (dict(materia="Materia", tipo="Resumen", unidades=2, tema="tema corto", modo="corto"), "no lleva Unidad"),
    (dict(materia="Materia", tipo="Tabla de fórmulas", unidades=2), "no lleva Unidad"),
    (dict(materia="Materia", tipo="Tabla de fórmulas", unidades=None, modo="corto"), "no lleva sufijo"),
    (dict(materia="Materia", tipo="Tabla de fórmulas", unidades=None, formato="hoja A4"), "no lleva sufijo"),
    (dict(materia="Materia", tipo="Parcial práctico", unidades=1, tema="tema corto"), "tema"),
    (dict(materia="CON", tipo="Trabajo práctico", unidades=None, detalle="x" * 10), None),  # "CON ｜ ..." no es reservado: debe pasar
]


def _ext_ok(base, ext, ok):
    try:
        base.archivo(ext)
        return ok
    except ValueError:
        return not ok


def probar(callar=False):
    fallas = []
    for kw, esperado in CASOS:
        try:
            n = nombre(**kw)
        except Exception as e:  # noqa: BLE001
            fallas.append(f"{kw}: levanto {e}")
            continue
        if str(n) != esperado:
            fallas.append(f"{kw}: {n!r} != {esperado!r}")
        if any(c in str(n) for c in '|:<>"/\\?*'):
            fallas.append(f"{n!r}: quedo un caracter invalido")
        if (SEP not in str(n) and TIPO_SEP not in str(n)) or ("Unidad" in str(n) and TIPO_SEP not in str(n)):
            fallas.append(f"{n!r}: faltan los caracteres sustitutos")
    for kw, frag in ERRORES:
        try:
            nombre(**kw)
            if frag is not None:
                fallas.append(f"{kw}: debia fallar ({frag})")
        except ValueError as e:
            if frag is None or frag.lower() not in str(e).lower():
                fallas.append(f"{kw}: fallo con otro mensaje: {e}")
    # extensiones por pieza
    rs = nombre("Materia A", "Resumen", 3, "corto", "hoja A4")
    rm = nombre("Materia A", "Resumen", 3, "corto")
    rp = nombre("Materia A", "Resumen", 3, "corto", "pantalla")
    rw = nombre("Materia A", "Resumen", 3, "corto", "Word")
    cu = nombre("Materia A", "Cuestionario teórico", 3)
    tp = nombre("Materia A", "Trabajo práctico", 4)
    tf = nombre("Materia A", "Tabla de fórmulas", None)
    for base, ext, ok in ((rs, "html", True), (rs, "pdf", True), (rs, "docx", False), (rm, "md", True), (rm, "html", False),
                          (rp, "html", True), (rp, "pdf", False), (rw, "docx", True), (cu, "html", True),
                          (cu, "json", True), (cu, "pdf", False), (cu, "docx", False), (tp, "html", True), (tp, "pdf", True), (tp, "docx", True),
                          (tf, "html", True), (tf, "pdf", True), (tf, "docx", True)):
        if not _ext_ok(base, ext, ok):
            fallas.append(f"{str(base)!r}: .{ext} deberia {'valer' if ok else 'rechazarse'}")
    # el PDF de una hoja A4 usa el mismo nombre base que su HTML
    if rs.archivo("pdf")[:-4] != rs.archivo("html")[:-5]:
        fallas.append("el PDF de la hoja A4 no comparte el nombre base con su HTML")
    # largo y nombres reservados
    for malo in ("a" * (LARGO_MAX + 1), "NUL", "termina.", " empieza", "doble  espacio", "con:dos"):
        try:
            validar_componente(malo)
            fallas.append(f"validar_componente acepto {malo!r}")
        except ValueError:
            pass
    validar_componente(f"Materia A {B} Resumen{D} Unidad 1")
    if not callar:
        for f in fallas:
            print("FALLA:", f)
        print(f"nombres.py: {len(CASOS)} nombres, {len(ERRORES)} rechazos y extensiones: " + ("TODO OK" if not fallas else f"{len(fallas)} fallas"))
    return not fallas


def ejemplos():
    for kw, _ in CASOS:
        n = nombre(**kw)
        ext = ("md" if n.tipo in RESUMENES and not kw.get("formato") else "pdf" if n.tipo == "Tabla de fórmulas" else
               "docx" if str(kw.get("formato", "")).lower() == "word" else "html")
        print(n.archivo(ext))
    n = nombre("Materia B", "Resumen", [1, 2, 3, 4], "corto", "hoja A4")
    print(n.archivo("pdf") + "   (PDF de la hoja A4: mismo nombre base)")


if __name__ == "__main__":
    if "--probar" in sys.argv:
        sys.exit(0 if probar() else 1)
    if "--ejemplos" in sys.argv:
        sys.stdout.reconfigure(encoding="utf-8")
        ejemplos()
        sys.exit(0)
    print(__doc__)
