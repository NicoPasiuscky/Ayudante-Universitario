"""calculos.py - regla de material-a4: todos los numeros de las soluciones se calculan
con Python ANTES de escribirlos, y esta comprobacion vuelve a calcularlos y falla si
alguno de los que aparecen en los Markdown de soluciones no coincide.

Parcial: parcial de demostracion (tasa de variacion).
Uso:  python demo/material/calculos.py         (lo corre construir.py)
      python demo/material/calculos.py --ver   imprime los valores
"""
import os
import sys

sys.dont_write_bytecode = True
AQUI = os.path.dirname(os.path.abspath(__file__))


def c(x, d=2):
    """Numero con coma decimal, en formato de Markdown con math: 3{,}00."""
    return f"{x:.{d}f}".replace(".", "{,}")


# 1) calentamiento de una muestra
y_i, y_f, dt1 = 20.0, 56.0, 12.0
dy1 = y_f - y_i
r1 = dy1 / dt1
t1c = (80.0 - 20.0) / r1
# 2) tanque que se llena y se vacia
entra, sale, dt2 = 40.0, 15.0, 13.0
dV2 = entra - sale
r2 = dV2 / dt2
rT2 = (entra + sale) / dt2
# 3) recta con dos puntos
tP, vP, tQ, vQ = 2.0, 14.0, 10.0, 46.0
r3 = (vQ - vP) / (tQ - tP)
V6 = vP + r3 * (6.0 - tP)

# (texto que debe aparecer en las soluciones, valor)
ESPERADOS = [
    ("\\Delta y = " + c(dy1, 1), dy1), ("\\bar{r} = " + c(r1), r1), ("t = " + c(t1c, 1), t1c),
    ("\\Delta V = " + c(dV2, 1), dV2), ("\\bar{r} = " + c(r2), r2), ("\\bar{r}_{T} = " + c(rT2), rT2),
    ("\\bar{r} = " + c(r3), r3), ("V = " + c(V6, 1), V6),
    (c(entra + sale, 1), entra + sale),
]

if __name__ == "__main__":
    if "--ver" in sys.argv:
        for t, v in ESPERADOS:
            print(f"{t:>22}  {v:.5f}")
        sys.exit(0)
    texto = ""
    for n in ("soluciones-resultados.md", "soluciones-resolucion.md"):
        texto += open(os.path.join(AQUI, n), encoding="utf-8").read()
    faltan = [t for t, _ in ESPERADOS if t not in texto]
    if faltan:
        raise SystemExit("calculos.py: no aparecen en las soluciones: " + "; ".join(faltan))
    print("calculos.py: los", len(ESPERADOS), "valores de las soluciones coinciden con Python")
