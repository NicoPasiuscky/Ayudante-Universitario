# Guía: estándares de resolución por área de conocimiento

Cada materia pertenece a una o más áreas. El estándar del área dice cómo se plantea, se resuelve y se presenta el contenido para que sea riguroso en esa disciplina. Se aplica en todos los flujos: al resumir (qué se desarrolla y qué gráficos se generan), al explicar, al resolver un TP y al redactar preguntas.

Las áreas que cubre la carrera de la persona están marcadas en `configuracion/proyecto.md`, y las que aplican a cada materia, en su `Materia.md`. Una materia puede combinar varias (por ejemplo, un laboratorio de física usa «Física y ciencias experimentales» y «Matemática»). Si la cátedra define un criterio propio (notación, signos, redondeo), **ese criterio manda** sobre el estándar general; se anota en `Materia.md`.

Principios comunes a todas las áreas:
- Planteo explícito: datos, incógnitas, condiciones de aplicabilidad y supuestos, antes del cálculo o del argumento.
- Nada sin sustento: no se completa con conocimiento no declarado; lo que no viene de la fuente se verifica en una fuente confiable (ver `INSTRUCCIONES.md`, «La fuente manda»).
- Terminología y notación exactas de la cátedra.
- Gráficos, diagramas y tablas reales cuando el contenido los pide (nunca descriptos en texto).
- Comprobación final del resultado (sentido, unidades, casos límite o coherencia con el marco teórico).

## Catálogo

### Matemática y cálculo
Análisis, álgebra, geometría, probabilidad, estadística teórica, análisis numérico, investigación operativa.
- Planteo formal: datos, incógnitas y condiciones de aplicabilidad.
- Interpretación geométrica previa al cálculo analítico, siempre con el gráfico real (`apoyo/graficos-matematicos.md`), nunca solo en palabras.
- Demostración de teoremas cuando el programa de la cátedra lo exige, con hipótesis y tesis explícitas.
- Desarrollo algebraico secuencial, sin omitir pasos intermedios.
- Comprobación analítica y verificación del sentido del resultado final (verificación simbólica con SymPy antes de graficar).
- Qué desarrolla más el resumen extenso: deducciones clave, hipótesis, significado geométrico y casos límite.

### Física y ciencias experimentales
Física, mecánica, termodinámica, electromagnetismo, óptica, laboratorios.
- Magnitudes con unidades en cada número; análisis dimensional de cada resultado.
- Leyes y fórmulas en forma simbólica primero, sustitución numérica después.
- Cifras significativas, incertidumbres y propagación de errores según el criterio de la cátedra.
- Diagramas físicos reales (cuerpo libre, montajes, circuitos, rayos), con convención de signos explícita.
- Cálculo independiente para verificar (`flujos/tp.md`) y revisión de casos límite.
- Qué desarrolla más el resumen extenso: deducciones, hipótesis del modelo, significado físico y análisis dimensional.

### Química
Química general, orgánica, analítica, fisicoquímica.
- Ecuaciones balanceadas con estados de agregación y condiciones.
- Cantidades con unidades y cifras significativas; estequiometría explícita paso a paso.
- Estructuras y mecanismos dibujados (no descriptos), con la notación de la cátedra.
- Seguridad y manejo de reactivos solo cuando la fuente lo trae.

### Programación y software
Algoritmos, estructuras de datos, lenguajes, paradigmas, desarrollo e ingeniería de software.
- Respetar el paradigma y el lenguaje oficial de la materia (no cambiarlo por conveniencia).
- Separar especificación (contrato), diseño e implementación.
- Expresar formalmente la complejidad en tiempo y espacio (O grande), invariantes de ciclo y casos límite.
- Casos de prueba: camino feliz, condiciones de borde y entradas inválidas.
- Código legible, arquitectura modular y documentación concisa de las interfaces; bloques de código con el lenguaje indicado.

**TP o proyecto con interfaz (web, escritorio o móvil).** La pila, los patrones y el estilo los fija la cátedra, y eso manda sobre cualquier guía de diseño. Si la persona usa una referencia de diseño de interfaces de terceros, consultá solo lo que hace falta y no la cargues entera: por ejemplo, `ui-ux-pro-max` (base local de guías por pila: React, Vue, Angular, JavaFX, WPF, Flutter, entre otras), `awesome-design-md` (un `DESIGN.md` por marca, solo si pide «con el estilo de X») o, de `taste-skill`, solo `redesign-skill` (mejorar una interfaz ya hecha) y `output-skill`; la skill principal de `taste-skill` es para landing y portfolio, no para tableros ni CRUD. Ninguna viene incluida en este proyecto: son de terceros (licencia MIT) y las instala la persona por su cuenta desde el repositorio oficial de cada una, conservando su licencia. Esto vale para el producto que entrega la persona; no cambia el sistema visual v4 de los resúmenes ni de los documentos de estudio.

### Sistemas, redes y arquitectura de computadoras
Arquitectura, sistemas operativos, comunicación de datos, redes, seguridad informática, análisis y diseño de sistemas de información.
- Estructuración por capas y niveles de abstracción.
- Diagramación real de paquetes, tramas, encabezados, estados, procesos (BPMN) y modelos UML consistentes entre sí (`apoyo/plantuml-diagramas.md`, o SVG a mano en diagramas chicos). Nunca ASCII art; Mermaid solo para borradores.
- Análisis de flujos de control, mecanismos de sincronización y protocolos.
- Diagnóstico metódico de fallas y escenarios de contingencia.
- Enfoque sociotécnico en sistemas de información: procesos, personas y tecnología; justificación económica y de ingeniería de cada decisión; riesgos y viabilidad.

### Datos, estadística e inteligencia artificial
Bases de datos, estadística aplicada, ciencia de datos, aprendizaje automático.
- Rigor en el diseño conceptual (modelo entidad-relación) y en las reglas de normalización relacional.
- Consultas SQL formateadas, legibles y comprobadas en su lógica de ejecución.
- En modelos: distinción nítida entre entrenamiento, validación y prueba; métricas apropiadas a la naturaleza del problema (exactitud, F1, área bajo la curva, error cuadrático, etc.).
- En estadística: tipo de variable, supuestos de cada método, tablas y gráficos de datos reales con unidades, y conclusiones en el contexto del problema.

### Ingeniería y diseño técnico
Mecánica, estructuras, materiales, electricidad y electrónica, procesos, industrial, civil.
- Planteo con esquema, datos, hipótesis simplificatorias y normas aplicables declaradas.
- Unidades coherentes en todo el cálculo; coeficientes de seguridad y márgenes explícitos cuando corresponda.
- Diagramas técnicos reales (esquemas de carga, circuitos, diagramas de flujo de proceso, planos simplificados).
- Verificación de resultados con un orden de magnitud o un caso conocido.

### Ciencias de la salud
Medicina, enfermería, kinesiología, nutrición, farmacia, biología.
- Terminología médica y biológica exacta, con la nomenclatura que use la cátedra.
- Distinguir evidencia (estudios, guías, consensos) de opinión; citar la fuente en `Materia.md`, no en el documento.
- Esquemas anatómicos y fisiológicos, algoritmos de decisión y tablas comparativas reales.
- Dosis, valores de referencia y criterios clínicos solo tal como los trae la fuente o una fuente confiable verificada; nunca inventar valores. El material de estudio no reemplaza una guía clínica vigente.

### Ciencias económicas, contables y de gestión
Economía, contabilidad, administración, finanzas, marketing, gestión.
- Supuestos económicos y contables declarados (moneda, período, tasa, método de valuación).
- Cálculos financieros con fórmulas explícitas, unidades de tiempo coherentes y redondeo según la cátedra.
- Tablas y estados (balance, flujo de fondos, cuadros de costos) reales, con totales comprobados.
- Gráficos de oferta y demanda, series y comparaciones con ejes rotulados y unidades.
- Marco normativo citado solo si la fuente lo trae.

### Derecho y ciencias sociales
Derecho, sociología, ciencia política, relaciones internacionales, trabajo social.
- Distinguir norma, doctrina y jurisprudencia; citar artículos y fallos exactamente como los trae la fuente.
- Esquemas, líneas de tiempo y cuadros comparativos de institutos o posiciones teóricas.
- Casos prácticos con método: hechos, problema jurídico o analítico, norma aplicable, análisis, conclusión.
- Vigencia de las normas: no afirmar vigencia sin verificarla en una fuente confiable.

### Humanidades, letras y educación
Filosofía, historia, letras, lingüística, psicología, ciencias de la educación.
- Fidelidad a los autores y a las posiciones: atribuir cada idea a quien corresponde, sin mezclar.
- Líneas de tiempo, mapas conceptuales y cuadros comparativos de corrientes o autores.
- Citas textuales entre comillas, con la referencia que pida la cátedra; paráfrasis claramente distinguidas.
- Argumentación explícita: tesis, premisas y conclusiones.

### Arquitectura, diseño y artes
Arquitectura, diseño gráfico e industrial, artes visuales y audiovisuales.
- Terminología proyectual y de historia del arte exacta.
- Imágenes y esquemas de referencia solo si la fuente los trae o son de elaboración propia; respetar derechos de autor y citar.
- Cuadros comparativos de movimientos, obras y autores; análisis formal ordenado (composición, materialidad, función, contexto).

## Cómo sumar un área nueva
Si la carrera usa un área que no está en el catálogo, pedile a la IA que la agregue. Una entrada nueva sigue esta forma y no pasa de ocho renglones:
```
### Nombre del área
Materias típicas.
- Cómo se plantea (datos, supuestos, marco).
- Cómo se resuelve o argumenta (método, rigor, pasos que no se omiten).
- Qué gráficos o diagramas son reales y obligatorios en esa área.
- Qué se verifica al final y contra qué fuente confiable.
```
Después se marca el área en `configuracion/proyecto.md`. Los estándares de las áreas son criterios de presentación y de rigor, no hechos de la disciplina: los hechos siempre salen de la fuente de la cátedra o de una fuente confiable verificada.
