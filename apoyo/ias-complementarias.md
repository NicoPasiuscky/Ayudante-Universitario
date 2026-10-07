# IAs complementarias (opcional): Claude, Codex y Gemini en equipo

Esta función es **opcional y está apagada por defecto**. Se usa solo si la persona la decide, después de informarse y de probarla (sección «Cómo se decide»). Sin ella, el proyecto funciona completo: la verificación la hace el rol `verificador` propio y todo lo demás lo hace la IA principal.

## Qué es
Repartir el trabajo entre tres modelos de empresas distintas, cada uno en lo que mejor rindió en las pruebas del proyecto de origen:
- **La IA principal** (la que ya usás, por ejemplo Claude) redacta y coordina: resúmenes, TP, explicaciones, cuestionarios.
- **Codex** (OpenAI) **verifica**: revisa en solo lectura TP, resúmenes y cuestionarios contra la fuente de la cátedra. Un modelo distinto del que redactó atrapa errores que el redactor no ve. Herramienta: `sistema-visual/herramientas/verificar_codex.py`.
- **Gemini**, por Antigravity CLI (`agy`), **lee fuentes y deriva resúmenes cortos**: arma el mapeo de una fuente (rol `analista-fuente`) y escribe el resumen corto a partir de un extenso ya verificado. Herramienta: `sistema-visual/herramientas/gemini_agy.py`. No se usa para verificar.

Qué se gana: menos consumo de la IA principal (la lectura de fuentes largas y la verificación pasan a otras cuentas) y una segunda mirada independiente. Qué se pierde: más piezas que instalar y mantener, tiempos más largos (una verificación completa de Codex tarda entre 10 y 20 minutos, y la de Gemini unos minutos) y límites de uso de cada cuenta.

## Lo que se midió, y cuánto vale
Son pruebas del autor del proyecto, con muestras chicas (unos pocos TP, un resumen y un cuestionario). Sirven de orientación, no son una garantía, y los modelos y los planes cambian:
- Codex encontró en un TP, un resumen extenso y un cuestionario errores reales que la revisión de la IA principal no había visto (umbrales, condiciones de validez, cuentas escritas con valores redondeados). Pasó por alto metatexto y detalles de figuras, que ahora lleva el prompt. En cuestionarios encontró matices de redacción más que claves equivocadas.
- Gemini, para leer una fuente y derivar un corto, resultó fiel y rápido. Para verificar un cuestionario, sin herramientas de cálculo, dejó pasar casi todos los errores; con una calculadora segura y una pregunta por vez detectó la mitad. Por eso la verificación principal queda en Codex.
- Nada de esto se verificó con otras materias. La primera vez que lo uses en una materia nueva, confirmá los hallazgos igual (el rol `verificador` lo exige).

## Qué hay que saber antes de decidir
1. **Privacidad.** Lo que lee Codex o Gemini viaja a los servidores de OpenAI o de Google. Mandales solo material de la cátedra y resúmenes. Sin carátulas ni datos personales (nombres, legajos, correos). Los scripts les indican como carpeta de trabajo la de la materia; Gemini (`agy`) solo lee dentro de ella, pero no se garantiza que Codex, en solo lectura, no pueda leer fuera de ese directorio. Por eso, no dejes datos personales a su alcance.
2. **Permisos.** Corren en solo lectura y no pueden escribir en tu carpeta. Nunca se usa `--dangerously-skip-permissions` ni equivalentes. El informe o el borrador lo escribe el script en el directorio temporal; lo que pasa a tu carpeta lo decide la IA principal después de confirmarlo.
3. **Cuentas, planes y cupos.** Cada herramienta usa tu cuenta y su plan. Los límites y los modelos disponibles dependen del plan y cambian: consultalos en la página oficial de cada proveedor antes de contar con ellos. Si una herramienta falla o no tiene cupo, el trabajo **no queda verificado**: la IA te avisa y vos elegís entre esperar o usar el verificador propio.
4. **Política de la cátedra.** Revisá si tu cátedra o tu universidad limitan el uso de IA en lo que entregás. Es tu responsabilidad.
5. **Costo.** Algunos planes son pagos o tienen cupo limitado. El proyecto no instala ni contrata nada por vos.

## Cómo se prepara (si la persona dice que le interesa)
La IA te guía, pero las cuentas y las instalaciones las hacés vos, con su permiso explícito en cada paso (regla de `INSTRUCCIONES.md`, «Dependencias»). Nada se descarga de sitios de terceros.
1. **Codex**: instalalo siguiendo las instrucciones oficiales de OpenAI (la aplicación o el programa de línea de comandos `codex`) e iniciá sesión con tu cuenta. Comprobación: `codex --version` tiene que responder, y la sesión tiene que estar iniciada. Si el ejecutable no está en el `PATH`, definí la variable `ESTUDIO_CODEX` con su ruta.
2. **Gemini por Antigravity**: instalá Antigravity y su programa de línea de comandos `agy` siguiendo las instrucciones oficiales de Google e iniciá sesión. Comprobación: `agy models` tiene que listar modelos. Si no está en el `PATH`, definí `ESTUDIO_AGY`. El modelo por defecto es `gemini-3.8-flash`; para otro, `ESTUDIO_GEMINI_MODELO` o `--modelo`.
3. **Prueba corta, con vos presente**: la IA corre cada herramienta sobre un material chico y sin datos personales (por ejemplo, un resumen corto de una unidad) y te muestra el resultado y el tiempo. Los códigos de salida están en el encabezado de cada script (0 listo; 2 no está instalado; 3 sin sesión o sin cupo; 4 falló).
4. **Si querés darle cálculo a Gemini** (opcional): `sistema-visual/herramientas/calculadora_segura.py` evalúa una sola expresión matemática, sin archivos, sin importaciones y con topes de tamaño y de tiempo. Autorizarla en la configuración de permisos de `agy` es una decisión tuya y se hace a mano: la IA no toca esa configuración sin que se lo pidas.

## Cómo se decide
Esta es la regla que sigue la IA, en orden:
1. **Informar, una sola vez** (al final de la puesta en marcha, o antes si la persona pregunta cómo gastar menos o cómo verificar mejor): decir en pocas líneas que existe esta función, qué hacen Codex y Gemini y qué implica (privacidad, cuentas, tiempos). Ofrecer esta guía.
2. **Preguntar si le interesa.** Si responde que no, anotar «no» en `configuracion/proyecto.md` y no volver a ofrecerlo, salvo que la persona lo pida.
3. **Si le interesa, explicar cómo se hace** (sección anterior) y ayudar a prepararlo y a probarlo, con permiso en cada paso.
4. **Decisión final, de la persona**: después de la prueba, preguntar «¿la dejamos activada?» y qué activar: Codex, Gemini o las dos. Solo con un sí claro se anota en `configuracion/proyecto.md` y se empieza a usar. Cualquier otra respuesta equivale a «no por ahora».
5. **Revocable**: la persona puede apagarla o cambiarla cuando quiera, y se actualiza el archivo.

## Cómo se usa cuando está activada
- **Verificación** (`roles/verificador.md`, `flujos/resumir.md`, `flujos/tp.md`): con Codex activado, el `verificador` corre `verificar_codex.py` en segundo plano y después **confirma cada hallazgo contra la fuente** antes de corregir, sin releer todo el documento: un modelo revisor también se equivoca.
- **Mapeo de fuentes** (`roles/analista-fuente.md`) y **resumen corto derivado de un extenso verificado** (`flujos/resumir.md`): con Gemini activado, se corre `gemini_agy.py`. Un corto escrito por Gemini pasa por el `verificador` como cualquier otro.
- **Si una herramienta falla**: se avisa, el trabajo queda sin verificar o sin derivar, y la persona decide si sigue con el procedimiento propio. Nunca se da por verificado lo que no se verificó.
