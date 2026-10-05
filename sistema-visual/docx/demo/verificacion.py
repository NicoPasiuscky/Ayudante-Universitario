"""verificacion.py - calculo independiente del TP de demostracion (tp-demo.md).

Ajusta una recta por minimos cuadrados, calcula los errores de la pendiente y de la
ordenada, el coeficiente de determinacion y el tiempo para llegar a 60 cm, y redondea
con las reglas de cifras significativas. Todos los numeros del .md salen de aca.

Uso: python demo/verificacion.py
"""
from decimal import ROUND_HALF_UP, Decimal

import numpy as np

t = np.array([0, 2, 4, 6, 8, 10.0])
h = np.array([10.2, 15.1, 19.8, 25.3, 30.1, 34.9])

pend, orden = np.polyfit(t, h, 1)
res = h - (pend * t + orden)
n = len(t)
s = np.sqrt(np.sum(res ** 2) / (n - 2))
sxx = np.sum((t - t.mean()) ** 2)
err_pend = s / np.sqrt(sxx)
err_orden = s * np.sqrt(1 / n + t.mean() ** 2 / sxx)
r2 = np.corrcoef(t, h)[0, 1] ** 2
t60 = (60 - orden) / pend
print(f"pendiente = {pend:.4f} +- {err_pend:.4f} cm/min   ordenada = {orden:.3f} +- {err_orden:.3f} cm")
print(f"R2 = {r2:.4f}   t(60 cm) = {t60:.2f} min")

# Comprobaciones: los numeros que aparecen en tp-demo.md
assert round(pend, 2) == 2.49 and round(err_pend, 2) == 0.02
assert round(orden, 1) == 10.1 and round(err_orden, 1) == 0.1
assert round(r2, 4) == 0.9996 and round(t60, 1) == 20.1


def redondeo(x, cs):
    """Redondeo a cs cifras significativas (mitad hacia arriba)."""
    d = Decimal(str(x))
    e = d.adjusted() - cs + 1
    return d.quantize(Decimal(1).scaleb(e), rounding=ROUND_HALF_UP)


print("Con 3 cifras significativas:", redondeo(pend, 3), "cm/min ;", redondeo(t60, 3), "min")
