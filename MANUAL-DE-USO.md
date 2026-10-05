# Manual de uso

Cómo estudiar con el Ayudante Universitario una vez instalado. Si todavía no lo instalaste, empezá por `MANUAL-DE-IMPLEMENTACION.md`.

## 1. La idea en un minuto
Le das el material de tu cátedra (apuntes, presentaciones, guías, parciales viejos) y la IA lo convierte en cosas que te sirven para estudiar: resúmenes, explicaciones, trabajos prácticos resueltos y cuestionarios para autoevaluarte. Tres reglas que no cambian:
- **La fuente manda.** Todo sale de tu material. Si la IA completa algo con conocimiento propio (solo en el modo extenso), lo verifica contra una fuente confiable y te lo informa aparte, no dentro del documento.
- **Nada se inventa.** Si el material no alcanza, la IA te lo dice; no rellena.
- **Tu material no se toca.** La IA solo lee las carpetas de fuente y escribe en carpetas de salida separadas.

## 2. Cómo se empieza
1. Abrí tu herramienta de IA en la carpeta del proyecto.
2. La primera vez, la IA te pregunta por tu universidad, tu carrera y dónde guardás el material (la «puesta en marcha»). Respondé una vez; queda anotado en `configuracion/proyecto.md`.
3. La primera vez que trabajás con una materia, te pregunta cuáles son sus carpetas de teoría, práctica y programa, y dónde guardar los resultados. Confirmás una vez; queda anotado en el `Materia.md` de esa materia y no vuelve a preguntar.

Después de eso, cada pedido es una frase.

## 3. Los cuatro flujos
Podés pedirlos con palabras comunes. Si tu herramienta tiene comandos, también `/resumir`, `/tp`, `/explicar` y `/cuestionario`.

### 3.1 Resumir
Para tener un documento guardado de una unidad, de varias, de la materia entera o de un tema corto.

Ejemplos de pedido:
- «Resumí la unidad 3 de [materia] en modo extenso, en hoja A4, para imprimir.»
- «Hacé un resumen corto de las unidades 1 a 4 en diapositivas.»
- «Armame una tabla de fórmulas de [tema].»

La IA te va a preguntar lo que no hayas dicho:
- **Formato**: HTML completo (para leer en pantalla o en el celular, con modo oscuro), Hoja A4 (para imprimir, con PDF), Diapositivas HTML (una idea por diapositiva, solo pantalla) o Word.
- **Modo**: **extenso y explicativo** para empezar a estudiar una unidad, o **corto y rápido** para repasar antes de un parcial. El corto se arma a partir del extenso, así que conviene hacer primero el extenso.
- **Índice** (en extensos de HTML completo o A4).
- **Si lo vas a imprimir**: si sí, los márgenes quedan espejados para imprimir de los dos lados y encarpetar; si es solo digital, iguales en todas las hojas.

Qué recibís: el documento en la carpeta de resúmenes de la materia, con un nombre uniforme (por ejemplo `Materia ｜ Resumen꞉ Unidad 3 ｜ extenso ｜ hoja A4.pdf`), el Markdown fuente, y en el chat la lista de **agregados propios** (lo que la IA sumó a tu fuente y cómo lo verificó) y las ambigüedades de la fuente que encontró.

Opcional: «con preguntas de práctica» agrega, marcadas como material de práctica, preguntas previas y «Probá sin mirar».

### 3.2 Explicar
Para repasar en el chat, sin archivos: «Explicame la unidad 4 de [materia] porque no entiendo [tema]». Si ya hay un resumen de esa unidad, la IA explica a partir de él; si no, lo hace desde tu fuente. Podés abarcar varias unidades de una vez. Si en algún momento querés guardarlo, decí «guardalo como resumen» y sigue con el flujo de resumir sin repetir el trabajo.

### 3.3 TP (trabajo práctico)
Para ayuda con un entregable de cursada: «Ayudame con el TP 2 de [materia]» y pegá la consigna (o decile dónde está). La IA te pregunta, en cada TP:
- si querés la resolución **paso a paso** o **solo resultados con su verificación**;
- si se imprime o es digital;
- el formato de entrega (HTML, HTML + PDF, solo PDF o Word);
- los datos de la carátula: número, curso e integrantes con nombre y legajo. **Estos datos los pasás por el chat cada vez; el proyecto no los guarda.**
Si el TP es de laboratorio, **vos pasás las mediciones**: la IA no inventa datos medidos.

Qué recibís: el informe con carátula, desarrollo, gráficos y tablas reales, resultados con cifras significativas y una verificación independiente de los cálculos.

### 3.4 Cuestionario
Para autoevaluarte: «Armame un cuestionario de las unidades 1 a 3 de [materia]». Es una página HTML que se abre en el navegador y funciona sin conexión. Tiene dos niveles, que no se mezclan:
- **Nivel unidad**: preguntas de repaso conceptual, basadas en las unidades de la materia.
- **Nivel parcial**: preguntas más exigentes, calibradas con tus parciales viejos de la materia (se inventan preguntas nuevas con esa dificultad; no se copian los ejercicios).

Cómo se usa el cuestionario terminado: al abrirlo elegís un modo.
- **Práctica**: sin límite de tiempo; repite más las preguntas que fallaste (repetición espaciada).
- **Parcial**: simula un examen con tiempo (30, 60, 90 o 120 minutos, o el que quieras), con o sin la posibilidad de volver atrás, y te da la nota sobre 10.
Tiene preguntas de opción múltiple, selección múltiple, verdadero o falso, cálculo con respuesta numérica, completar frases y ejercicios con varias partes, con fórmulas, tablas y figuras. Tu mejor resultado queda guardado en tu navegador.

Se pueden agregar preguntas más tarde: «Sumá preguntas de la unidad 4 al cuestionario»; la IA continúa el mismo banco, sin repetir.

## 4. Material para practicar con parciales
Aunque no sea un flujo con nombre, lo podés pedir:
- **Digitalizar un parcial viejo**: «Pasá a limpio este parcial» (con el PDF o la foto). Sale en hoja A4 con el texto fiel al original, figuras redibujadas y sin tus datos personales. Las erratas del original se mantienen y te las avisa.
- **Modelos de práctica**: «Armame dos modelos de parcial práctico de las unidades 1 a 3». Son ejercicios distintos a los del parcial, tomados de otros problemas de tu guía.
- **Soluciones**: siempre en dos documentos aparte, uno de resultados y otro con la resolución paso a paso, para que puedas practicar sin verlas.

## 5. Cómo sacarle el mejor provecho
- **Una unidad por vez.** Es más preciso y gasta menos. Si el trabajo es grande, la IA te da un «prompt» para continuar en otra conversación; copialo y pegalo en una nueva.
- **Primero el extenso, después el corto.** El corto sale del extenso ya verificado, sin releer la fuente.
- **Dale buena fuente.** Los PDF con texto funcionan mejor que los escaneados; los escaneados se pasan por reconocimiento de texto y conviene mirar el resultado. Las fórmulas pegadas como imagen son las que más se leen mal: si la IA te avisa que una página tiene «fórmula fragmentada», revisá lo que tomó.
- **Contale tu criterio de la cátedra**: cómo se redondea, qué signos se usan, qué notación. Quedan anotados en el `Materia.md` y valen para siempre.
- **Revisá lo que te avisa.** Las ambigüedades de la fuente y los agregados propios no verificados son lo único que puede estar mal; el resto sale contrastado con tu material.
- **Mirá los documentos antes de imprimir.** La IA los revisa, pero la última mirada es tuya.

## 6. Dónde queda todo
En la carpeta de cada materia (la que indicaste en la puesta en marcha):
- `Materia.md`: el estado de la materia (unidades resumidas, preferencias, agregados propios, ambigüedades).
- Carpeta de resúmenes (y dentro, una de HTML y Markdown si las separaste, y otra de figuras).
- Carpeta de cuestionarios, de TP y de parciales.
Nada se guarda dentro del proyecto salvo archivos temporales de trabajo (`trabajo/`), que se pueden borrar.

## 7. Límites que conviene conocer
- La IA puede equivocarse. El sistema está armado para detectarlo (verificación separada, contraste con la fuente, cálculos recalculados), pero no es infalible. **Para un parcial o un final, los resultados de cálculo y las definiciones clave se contrastan con tu cátedra.**
- Si la fuente tiene un error, el resumen lo hereda. La IA te lo avisa cuando lo detecta, pero no lo corrige en silencio.
- Los gráficos y las fórmulas salen del contenido de tu fuente; si la fuente no los trae, la IA los genera y los verifica, pero conviene mirarlos.
- Respetá las reglas de tu universidad sobre el uso de herramientas de IA en trabajos y exámenes. Este proyecto es una ayuda de estudio; qué se puede entregar como propio lo decide tu cátedra.

## 8. Frases útiles
| Querés... | Decí... |
|---|---|
| Ver qué podés pedir | «¿Qué flujos tenés?» |
| Cambiar una preferencia para siempre | «Anotá que en [materia] prefiero siempre [formato/modo]» |
| Rehacer solo el formato | «Pasá ese resumen a diapositivas» (no redacta de nuevo, solo exporta) |
| Que explique de otra forma | «Explicámelo con un ejemplo cotidiano» |
| Ver de dónde sale algo | «¿De dónde sacaste esto?» (te dice si es de la fuente o un agregado propio) |
| Corregir un error | «Esto está mal: [qué]. La fuente dice [qué]» |
