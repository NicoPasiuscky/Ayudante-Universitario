"""Tareas de lectura y resumen con Gemini via Antigravity CLI (`agy`). OPCIONAL: solo si la
persona lo decidio (ver apoyo/ias-complementarias.md; configuracion/proyecto.md, «IAs complementarias»).

Modelo por defecto: gemini-3.8-flash (se cambia con la variable ESTUDIO_GEMINI_MODELO o con
--modelo). El nivel de razonamiento por defecto sale de una medicion hecha en el proyecto de
origen sobre el capitulo de una fuente real:
  mapeo -> low     (igual deteccion de erratas que high, completo, ~3 min)
  corto -> medium  (fiel y con mini ejemplos, ~2 min)
NO sirve para verificar (en la prueba de un cuestionario dejo pasar casi todos los errores):
para eso, `verificar_codex.py` o el rol `verificador` propio.

Privacidad: el contenido de los archivos que lee viaja a los servidores de Google. Usarlo solo
con material de catedra y resumenes, sin caratulas ni datos personales.

Uso:
  python gemini_agy.py --tarea mapeo --fuente "<ruta al PDF>" --paginas "<que leer>" --salida <mapeo.txt>
  python gemini_agy.py --tarea corto --fuente "<ruta al resumen extenso .md>" --salida <corto.md>
      --materia "Materia de ejemplo" --sigla MEJ --unidad 3 --titulo "Variación y tasa de cambio"
      [--nivel low|medium|high] [--extra "<texto>"] [--cwd <carpeta>] [--timeout 1800]

En la tarea `corto` el script arma el encabezado del documento (YAML y titulo de unidad) y
Gemini escribe el cuerpo DIRECTAMENTE con los componentes del sistema v4 (definicion,
clave, ojo, ejemplo, tablas): sale listo para `construir.resumen` y para `verificador`.

`agy` en modo sin interfaz solo lee dentro de su carpeta de trabajo y no puede pedir
permisos: por eso la carpeta de trabajo es el ancestro comun de las fuentes y el prompt
prohibe usar shell. Nunca se usa --dangerously-skip-permissions.

Donde esta agy: variable ESTUDIO_AGY (ruta), o `agy` en el PATH, o, en Windows, su carpeta de
instalacion por defecto (%LOCALAPPDATA%\\agy\\bin).

Codigos de salida: 0 listo; 2 no se encontro agy; 3 sin sesion; 4 fallo o salida vacia.
En 2 a 4 la tarea NO se hizo: avisar a la persona.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

MODELO = os.environ.get("ESTUDIO_GEMINI_MODELO", "gemini-3.8-flash")
NIVEL_POR_TAREA = {"mapeo": "low", "corto": "medium"}

SIN_SHELL = ("No ejecutes comandos de shell: usá solo tu herramienta de lectura de archivos, "
             "con las rutas que te doy. No modifiques ningún archivo.\n\n")

# Guia de formato del sistema v4 para el modo corto (sintaxis de Pandoc que lee estudio.lua)
FORMATO_CORTO = r"""
FORMATO OBLIGATORIO (Markdown de Pandoc con los componentes del sistema; NO uses ningún otro):
- Tu respuesta final es únicamente el cuerpo en Markdown: sin planes, sin artefactos, sin comentarios y sin pedir confirmación.
- Entregá SOLO el cuerpo, sin encabezado YAML ni título de unidad (los agrega el sistema). Empezá directamente con una sección `## Nombre {#sec:uN-slug}` (uN = número de la unidad; slug en minúsculas, sin tildes ni espacios). Subsecciones con `###`.
- Definición, una por concepto y de una sola línea:
::: {.definicion #def:slug titulo="nombre del concepto"}
Texto de la definición en una línea, con $fórmulas$ en línea si hace falta.
:::
- Fórmula clave (la única con recuadro; una por tema; `\dfrac` para los cocientes, decimales con coma como 0{,}5 dentro de las fórmulas, funciones como `\Pr`, `\sqrt`):
::: clave
::: {.ecuacion #ec:slug}
$$ fórmula $$
:::
:::
- Si la fórmula clave es larga (más de unos 70 caracteres), partila en una igualdad por línea con `\begin{aligned} a &= b \\ c &= d \end{aligned}` dentro del `$$`, para que no se salga del recuadro.
- Recuadro de error típico, una o dos líneas, uno por tema como máximo:
::: ojo
Texto del error típico.
:::
- Mini ejemplo numérico tomado del extenso (datos y resultado):
::: {.ejemplo #ej:slug titulo="descripción corta"}
Enunciado breve y resolución en pocas líneas, con las cifras del extenso.
:::
- Tabla (solo si el extenso trae una tabla que haga falta), con título debajo y dentro del bloque:
::: {#tbl:slug}
| Col A | Col B |
|-------|-------|
| a     | b     |

Table: Título de la tabla.
:::
- Los identificadores (#def:, #ec:, #ej:, #tbl:, #sec:) son únicos, en minúsculas, sin tildes ni espacios. Cada `:::` de apertura lleva su `:::` de cierre en una línea sola. No uses listas de definición, HTML ni imágenes. No numeres a mano.
- EJEMPLO de una sección completa:

## Tasa de variación promedio {#sec:u3-tasa-promedio}

::: {.definicion #def:tasa-promedio titulo="tasa de variación promedio"}
Cociente entre la variación neta de una magnitud y el tiempo transcurrido.
:::

::: clave
::: {.ecuacion #ec:tasa-promedio}
$$\bar{r} = \dfrac{y_f - y_i}{t_f - t_i}$$
:::
:::

::: ojo
Sumar los cambios en valor absoluto en lugar de usar la variación neta: la tasa promedio conserva el signo.
:::

::: {.ejemplo #ej:tasa-promedio titulo="calentamiento de una muestra"}
Con $y_i = 20$ °C, $y_f = 56$ °C y $\Delta t = 12$ min, $\bar{r} = \dfrac{56 - 20}{12} = 3$ °C/min.
:::
"""

PROMPTS = {
    "mapeo": (
        "Sos un analista de fuentes universitarias. Leé el archivo: {fuente}\n"
        "Qué leer: {paginas}\nMirá como imagen las páginas con fórmulas, tablas o gráficos si el texto "
        "no alcanza. Producí un mapeo estructurado SIN resumir ni opinar: por cada sección y subsección "
        "con su página impresa, listá los conceptos y definiciones, cada fórmula escrita tal cual, las "
        "tablas, los gráficos o figuras, los ejemplos resueltos con sus datos y resultados, y toda errata "
        "o inconsistencia que notes (valores que no coinciden entre el texto y el dibujo, fórmulas con "
        "signo o variable equivocados, notación mezclada, cuentas que no dan lo que dicen). Entregá solo "
        "el mapeo, en texto plano."
    ),
    "corto": (
        "Leé el resumen extenso ya verificado: {fuente}\n"
        "Derivá de ÉL (sin releer ninguna otra fuente) un resumen CORTO, en español rioplatense "
        "académico, para repasar y fijar antes de un parcial, escrito directamente en el formato del "
        "sistema que se describe abajo. Reglas de contenido: "
        "(1) claramente más corto que el extenso; el largo exacto es orientativo (una a dos hojas A4 por "
        "unidad), no un tope: no recortes contenido que haga falta; "
        "(2) cada tema con su definición en una línea, la fórmula clave, un recuadro «ojo» con el error "
        "típico y un mini ejemplo numérico tomado del extenso; "
        "(3) sin glosario, sin demostraciones y sin comentarios metatextuales (nada de «según la fuente», "
        "«el resumen extenso dice», «la cátedra escribe»); "
        "(4) no debe decir NADA que el extenso no diga: no agregues datos, fórmulas ni ejemplos propios; "
        "(5) cubrí todos los temas del extenso y respetá las condiciones de validez de cada fórmula tal "
        "como figuran en él.\n" + FORMATO_CORTO
    ),
}


def buscar_agy():
    """Ruta del ejecutable de agy: ESTUDIO_AGY, o `agy` en el PATH, o su carpeta por defecto en Windows."""
    forzado = os.environ.get("ESTUDIO_AGY")
    if forzado:
        return forzado if os.path.exists(forzado) else shutil.which(forzado)
    en_path = shutil.which("agy")
    if en_path:
        return en_path
    cand = os.path.join(os.environ.get("LOCALAPPDATA", ""), "agy", "bin", "agy.exe")
    return cand if os.path.exists(cand) else None


def bloques_balanceados(texto):
    """Comprueba que cada ::: de apertura tenga su cierre (solo ::: en una linea)."""
    nivel = 0
    for linea in texto.split("\n"):
        s = linea.strip()
        if not s.startswith(":::"):
            continue
        if s == ":::":
            nivel -= 1
            if nivel < 0:
                return False
        else:
            nivel += 1
    return nivel == 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tarea", required=True, choices=sorted(PROMPTS))
    p.add_argument("--fuente", required=True, nargs="+", help="archivo(s) a leer (dentro de la carpeta de trabajo)")
    p.add_argument("--paginas", default="todo el documento")
    p.add_argument("--salida", required=True)
    p.add_argument("--nivel", choices=["low", "medium", "high"])
    p.add_argument("--modelo", default=MODELO, help="modelo base, sin el nivel (por defecto %(default)s)")
    p.add_argument("--extra", default="")
    p.add_argument("--cwd")
    p.add_argument("--timeout", type=int, default=1800)
    # solo para la tarea corto: encabezado del documento
    p.add_argument("--materia")
    p.add_argument("--sigla")
    p.add_argument("--unidad")
    p.add_argument("--titulo")
    a = p.parse_args()

    if a.tarea == "corto" and not (a.materia and a.unidad and a.titulo):
        print("La tarea corto necesita --materia, --unidad y --titulo (y opcionalmente --sigla).")
        return 4
    agy = buscar_agy()
    if not agy:
        print("No se encontró agy (Antigravity CLI).")
        return 2

    fuentes = [os.path.abspath(f) for f in a.fuente]
    cwd = os.path.abspath(a.cwd) if a.cwd else os.path.commonpath([os.path.dirname(f) for f in fuentes])
    nivel = a.nivel or NIVEL_POR_TAREA[a.tarea]
    modelo = f"{a.modelo}-{nivel}"

    # reemplazo simple (no str.format): el formato del sistema lleva llaves {#sec:...}
    prompt = SIN_SHELL + PROMPTS[a.tarea].replace("{fuente}", "; ".join(fuentes)).replace("{paginas}", a.paginas)
    if a.extra:
        prompt += "\n\n" + a.extra

    os.makedirs(os.path.dirname(os.path.abspath(a.salida)), exist_ok=True)
    try:
        r = subprocess.run([agy, "--print", prompt, "--model", modelo, "--mode", "plan",
                            "--output-format", "text"], cwd=cwd, capture_output=True, timeout=a.timeout)
    except subprocess.TimeoutExpired:
        print(f"agy no terminó en {a.timeout} s; no se hizo la tarea.")
        return 4

    salida = r.stdout.decode("utf-8", "replace").strip()
    err = r.stderr.decode("utf-8", "replace")
    low = (salida + err).lower()
    if any(k in low for k in ("not logged in", "login required", "sign in", "unauthenticated", "401")) and not salida:
        print("agy sin sesión iniciada; abrí Antigravity o ejecutá `agy` una vez.")
        print(err[-500:])
        return 3
    if r.returncode != 0 or len(salida) < 300 or "no output produced" in low:
        print(f"agy falló (código {r.returncode}) o devolvió una salida vacía o negada.")
        print((err or salida)[-600:])
        return 4

    aviso = ""
    if a.tarea == "corto":
        # quitar cercas de codigo y cualquier encabezado que Gemini haya agregado
        salida = re.sub(r"^```[a-zA-Z]*\n", "", salida)
        salida = re.sub(r"\n```\s*$", "", salida)
        salida = re.sub(r"\A---\n.*?\n---\n", "", salida, flags=re.S)
        # el modo plan de agy a veces antepone texto de «plan»: el cuerpo empieza en la primera seccion
        m = re.search(r"(?m)^## ", salida)
        if m:
            salida = salida[m.start():]
        else:
            print("La respuesta no contiene secciones `## ...`; no es un resumen en el formato esperado.")
            return 4
        cab = ["---", f'pagetitle: "{a.materia}, unidad {a.unidad}, resumen corto"', "lang: es", f'materia: "{a.materia}"']
        if a.sigla:
            cab.append(f'sigla: "{a.sigla}"')
        cab += [f'unidad: "{a.unidad}"', "---", "", f"# {a.titulo} {{unidad={a.unidad}}}", ""]
        salida = "\n".join(cab) + "\n" + salida
        if not bloques_balanceados(salida):
            aviso = " ATENCIÓN: hay bloques ::: sin cerrar o de más; revisar antes de construir."
    with open(a.salida, "w", encoding="utf-8", newline="\n") as f:
        f.write(salida + "\n")
    print(f"Listo: {a.salida} ({len(salida):,} caracteres) con {modelo}.{aviso}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
