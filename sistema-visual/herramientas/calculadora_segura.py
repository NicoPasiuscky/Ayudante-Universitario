"""Calculadora segura para que un modelo recalcule cifras sin tener shell.

Evalua UNA expresion matematica y escribe el resultado. No puede leer ni escribir
archivos, ni importar, ni usar atributos, ni llamar a nada que no este en la lista blanca:
solo numeros, + - * / // % **, comparaciones, y las funciones de abajo. Con topes de
tamano (exponentes, rangos, factoriales) y 5 segundos de tiempo maximo. Pensada para
`agy` (Antigravity CLI): se le da UNA regla de permiso con esta calculadora y nada mas
(`command(python <ruta>\\calculadora_segura.py)`), en vez de permitir `python` a secas.

Uso:
  python calculadora_segura.py "<expresion>" [decimales]
Ejemplos:
  python calculadora_segura.py "7/11" 4                       -> 0.6364
  python calculadora_segura.py "1 - exp(-0.5)" 4              -> 0.3935
  python calculadora_segura.py "Phi((124-100)/15)" 4          -> 0.9452
  python calculadora_segura.py "sum(comb(10,k)*0.5**10 for k in range(2,5))" 4
Funciones: sqrt exp log ln log10 sin cos tan atan factorial comb perm erf abs round min max
sum len range pow; normal estandar: Phi(z) (acumulada), phi(z) (densidad); constantes pi, e.
"""
import ast
import math
import os
import sys
import threading

LIM_RANGE = 200000      # elementos de un range
LIM_EXP = 5000          # |exponente|
LIM_DIGITOS = 20000     # digitos de un entero resultante
LIM_N = 5000            # n de factorial, comb y perm
TIEMPO = 5              # segundos


class Tope(Exception):
    pass


def _pot(a, b):
    if abs(b) > LIM_EXP:
        raise Tope("exponente demasiado grande")
    if isinstance(a, int) and isinstance(b, int) and b > 0 and a not in (0, 1, -1):
        if b * math.log10(abs(a)) > LIM_DIGITOS:
            raise Tope("resultado demasiado grande")
    return a ** b


def _rango(*args):
    r = range(*args)
    if len(r) > LIM_RANGE:
        raise Tope("range demasiado grande")
    return r


def _tope_n(f):
    def g(*args):
        if any(isinstance(x, int) and abs(x) > LIM_N for x in args):
            raise Tope("argumento demasiado grande")
        return f(*args)
    return g


CONST = {"pi": math.pi, "e": math.e}
FUNC = {
    "sqrt": math.sqrt, "exp": math.exp, "log": math.log, "ln": math.log, "log10": math.log10,
    "sin": math.sin, "cos": math.cos, "tan": math.tan, "atan": math.atan,
    "factorial": _tope_n(math.factorial), "comb": _tope_n(math.comb), "perm": _tope_n(math.perm),
    "erf": math.erf, "abs": abs, "round": round, "min": min, "max": max, "sum": sum, "len": len,
    "range": _rango, "pow": _pot,
    "Phi": lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2))),
    "phi": lambda z: math.exp(-z * z / 2) / math.sqrt(2 * math.pi),
}
OPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow, ast.USub, ast.UAdd)
CMP = (ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq)


def revisar(nodo, locales=()):
    if isinstance(nodo, ast.Expression):
        return revisar(nodo.body, locales)
    if isinstance(nodo, ast.Constant):
        if isinstance(nodo.value, (int, float, bool)):
            return
        raise ValueError("solo se permiten numeros")
    if isinstance(nodo, ast.Name):
        if nodo.id in CONST or nodo.id in locales:
            return
        raise ValueError(f"nombre no permitido: {nodo.id}")
    if isinstance(nodo, ast.BinOp):
        if not isinstance(nodo.op, OPS):
            raise ValueError("operador no permitido")
        revisar(nodo.left, locales); revisar(nodo.right, locales); return
    if isinstance(nodo, ast.UnaryOp):
        if not isinstance(nodo.op, OPS):
            raise ValueError("operador no permitido")
        revisar(nodo.operand, locales); return
    if isinstance(nodo, ast.Compare):
        if not all(isinstance(o, CMP) for o in nodo.ops):
            raise ValueError("comparacion no permitida")
        revisar(nodo.left, locales)
        for c in nodo.comparators:
            revisar(c, locales)
        return
    if isinstance(nodo, ast.Call):
        if not isinstance(nodo.func, ast.Name) or nodo.func.id not in FUNC or nodo.keywords:
            raise ValueError("llamada no permitida")
        for a in nodo.args:
            revisar(a, locales)
        return
    if isinstance(nodo, (ast.Tuple, ast.List)):
        for x in nodo.elts:
            revisar(x, locales)
        return
    if isinstance(nodo, (ast.GeneratorExp, ast.ListComp)):
        locs = set(locales)
        for g in nodo.generators:
            if not isinstance(g.target, ast.Name) or g.is_async:
                raise ValueError("comprension no permitida")
            revisar(g.iter, tuple(locs))
            locs.add(g.target.id)
            for c in g.ifs:
                revisar(c, tuple(locs))
        revisar(nodo.elt, tuple(locs)); return
    raise ValueError(f"construccion no permitida: {type(nodo).__name__}")


class ReemplazaPotencia(ast.NodeTransformer):
    """a ** b pasa por _pot, que pone topes al tamano."""
    def visit_BinOp(self, nodo):
        self.generic_visit(nodo)
        if isinstance(nodo.op, ast.Pow):
            return ast.copy_location(ast.Call(func=ast.Name(id="_pot", ctx=ast.Load()),
                                              args=[nodo.left, nodo.right], keywords=[]), nodo)
        return nodo


def evaluar(expr, resultado):
    try:
        arbol = ast.parse(expr, mode="eval")
        revisar(arbol)
        arbol = ast.fix_missing_locations(ReemplazaPotencia().visit(arbol))
        entorno = dict(CONST, **FUNC)
        entorno["_pot"] = _pot
        # todo el entorno va como globals: las comprensiones no ven los locals
        entorno["__builtins__"] = {}
        resultado.append(eval(compile(arbol, "<expr>", "eval"), entorno))
    except Exception as e:  # incluye Tope, ValueError, ZeroDivisionError, OverflowError
        resultado.append(e)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    expr = sys.argv[1]
    dec = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    if len(expr) > 600:
        print("ERROR: expresion demasiado larga")
        return 2
    resultado = []
    hilo = threading.Thread(target=evaluar, args=(expr, resultado), daemon=True)
    hilo.start()
    hilo.join(TIEMPO)
    if hilo.is_alive():
        print(f"ERROR: tardo mas de {TIEMPO} s")
        sys.stdout.flush()
        os._exit(1)
    r = resultado[0]
    if isinstance(r, Exception):
        print(f"ERROR: {r}")
        return 1
    if isinstance(r, (int, float)) and not isinstance(r, bool):
        print(f"{r!r}  (redondeado a {dec} decimales: {round(float(r), dec)})")
    else:
        print(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
