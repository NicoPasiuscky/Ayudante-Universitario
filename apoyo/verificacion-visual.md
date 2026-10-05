# Guía: verificación visual (no asumir, mirar)

Se aplica después de generar cualquier diagrama (Graphviz, PlantUML o SVG), gráfico matemático o documento, antes de darlo por terminado. Renderizá, inspeccioná visualmente de verdad (no asumas) y corregí, con un máximo de 3 intentos.

Regla de fondo de todo este proyecto: un archivo generado puede tener toda la sintaxis correcta y aun así verse mal. Nunca entregues un diagrama, un gráfico o un documento sin haberlo mirado de verdad. Si tu modelo no puede ver imágenes, pedile a la persona que abra el archivo y te cuente qué ve, o usá las medidas automáticas de `verificar_reglas.py` y `verificar_margenes.py` como mínimo.

## Cómo mirar el resultado
- **PNG suelto** (salida `-Tpng`, `-tpng` o `dpi=300` para un `.docx` puntual): abrir directo con la herramienta de lectura de imágenes.
- **SVG suelto, o el HTML completo del resumen ya armado** (para ver cómo queda el diagrama insertado, con el CSS real alrededor): navegador sin interfaz, con el script único `sistema-visual/herramientas/captura_espera.py` y su variante `--rapida` (`firefox --headless --screenshot` sin esperar nada; alcanza para un SVG o un HTML estático). No depende de que ninguna extensión del navegador esté conectada:
  ```
  python sistema-visual/herramientas/captura_espera.py "/ruta/al/archivo.svg-o-html" "<ruta temporal>/verificacion.png" 900 2600 --rapida
  ```
  Después leer ese PNG con la herramienta de lectura de imágenes. **Firefox es el motor de verificación** (las medidas de las reglas salen de él). Chrome o Chromium se usan solo para comprobar compatibilidad, como dice `INSTRUCCIONES.md`, «Navegador y verificación visual». Las herramientas de Firefox usan perfil temporal propio, así que no chocan con el Firefox abierto de la persona.
  Detalles de Firefox que el script ya resuelve: `--screenshot <ruta>` no siempre escribe donde se le indica (usa la carpeta de trabajo y el nombre `screenshot.png`, y el script mueve el PNG), la primera ejecución tarda 10 a 15 s y las siguientes unos 2 s, y captura solo el área visible: para una página larga pasar un alto grande (2600) o capturar por tramos. **La captura es descartable: escribirla siempre en el directorio temporal, nunca en la carpeta de la persona ni en este proyecto.**
- **Páginas que se arman con JavaScript después de cargar** (Mermaid, hoja A4 con Paged.js, cuestionario) o que necesitan clics antes de capturar: el mismo `captura_espera.py` sin `--rapida` (Firefox sin interfaz vía Marionette; espera una condición, por ejemplo `data-paginado` en el A4, y puede correr un guion de clics):
  ```
  python sistema-visual/herramientas/captura_espera.py "<archivo.html>" "<ruta temporal>/captura.png" 1280 900 [claro|oscuro] [completa 0/1] [celular 0/1]
  ```
  **Modo celular**: Firefox sin interfaz no achica la ventana por debajo de unos 500 px; con `celular 1` la página se abre dentro de un `<iframe>` de 390 px (las consultas de medios responden a ese ancho). No es un teléfono real, pero alcanza para revisar el diseño angosto. Misma regla: la captura va al directorio temporal. Para tamaños exactos (diapositivas: 1280x720, 390x844 y 844x390) usar `Firefox.capturar(..., celular=True)` o `Firefox.medir(...)` de `captura_espera.py`; `python sistema-visual/herramientas/capturas.py --solo-diapositivas` saca las capturas y mide desborde, letra mínima y contraste (reglas 24 y 25).
- **Material impreso en HTML A4** (ver `apoyo/material-a4.md`): captura de Firefox de cada hoja (recorte de `.pagedjs_page`, `capturas.py`, función `capturar_material`), esperando a `document.documentElement.dataset.paginado=='1'` como indica `captura_espera.py`. Para revisar la hoja impresa, `herramientas/imprimir_a4.py` la imprime a PDF con Firefox al directorio temporal y `pagina.get_pixmap(dpi=105)` de PyMuPDF la rasteriza; ese PDF de verificación va al temporal (el PDF de entrega lo arma `imprimir_a4.entregar`).
- **Word**: `herramientas/captura_docx.py` exporta el `.docx` a PDF y saca un PNG por hoja (ver `apoyo/generar-docx.md`).
- Si no hay Firefox disponible, la alternativa mínima es `chromium --headless --screenshot=<png> --window-size=1280,900 <archivo.html>`; sirve para mirar, pero no reemplaza las medidas de las reglas.

## Qué revisar (checklist)
- Texto y etiquetas completos, ninguno cortado a la mitad.
- Nodos y cajas sin superponerse entre sí ni con las flechas.
- Flechas que no se cruzan de forma confusa (si se cruzan, reordenar nodos o cambiar `rankdir` o el diseño antes de aceptar).
- Si es un gráfico matemático: la parte relevante de la función está visible (dominio elegido con criterio, ver `apoyo/graficos-matematicos.md`).
- Si es un diagrama extraído de la fuente (ver `roles/profesor.md`): no quedó texto de un párrafo vecino colado en el recorte, y no falta ningún rótulo del original.

## Máximo 3 intentos
Si después de 3 ajustes el resultado sigue sin verse bien, no sigas iterando solo: mostrale a la persona el mejor resultado y señalá puntualmente qué quedó mal, en vez de forzar un cuarto intento a ciegas.
