# Configuración del proyecto

Este es el único archivo que una persona completa para adaptar el Ayudante Universitario a su universidad, su carrera y su manera de trabajar. La IA lo lee antes de cada pedido (ver `INSTRUCCIONES.md`). Mientras haya campos con `[completar]`, hace la puesta en marcha: te pregunta lo que falta y lo anota acá.

Podés completarlo a mano o dejar que la IA lo haga conversando con vos. No pongas acá contraseñas ni datos que no quieras que se compartan: si compartís el proyecto con otras personas, este archivo viaja con él.

## Identidad académica
- Universidad: [completar]
- Facultad, departamento o escuela: [completar]
- Carrera: [completar]
- Plan de estudios (año o código): [completar]
- Año o nivel que cursás ahora: [completar]
- Idioma de los documentos: español
- Variante del idioma (por ejemplo rioplatense, mexicano, neutro, de España): [completar]
- Forma de escribir los decimales en los documentos: coma («1,5»)

## Carpetas
La IA solo necesita saber dónde está tu material. Usá rutas absolutas del sistema donde trabajás (ejemplos: `C:\Users\Ana\Documents\Universidad`, `/Users/ana/Universidad`, `/home/ana/universidad`). Si tu material está en una carpeta sincronizada con la nube (Drive, OneDrive, Dropbox), usá la ruta local de esa carpeta; si hay una copia vieja que no sincroniza, anotala acá para no usarla por error.

- Carpeta raíz de la universidad: [completar]
- Cómo está organizada por dentro (marcá lo que corresponda o describilo): `[Año o cuatrimestre]/[Materia]/` · `[Materia]/` directamente · otra: [completar]
- Rutas que NO se deben usar (copias viejas, papelera, etc.): [ninguna]

### Nombres de las carpetas de salida
Dentro de la carpeta de cada materia. Podés cambiarlos; la IA usa exactamente estos.
- Resúmenes: `Resúmenes`
- HTML y Markdown cuando se separan de los PDF: `HTML y MD`
- Figuras: `Figuras` (dentro de `Resúmenes`)
- Cuestionarios: `Cuestionarios`
- Trabajos prácticos: `TPs`
- Parciales digitalizados: `Parciales digitalizados`
- Parciales para practicar: `Parciales para practicar`

### Carpetas de fuente de la cátedra (solo lectura)
Los nombres varían de una materia a otra; la IA los resuelve la primera vez con vos y los anota en el `Materia.md` de cada materia. Si ya sabés los nombres más comunes en tu universidad, escribilos acá para que los reconozca de entrada: [completar, por ejemplo Programa, Teoría, Práctica, Material de cátedra]

## Preferencias por defecto
Valen para todas las materias salvo que el `Materia.md` de una materia diga otra cosa. «Preguntar cada vez» es una respuesta válida.
- Formato de los resúmenes (HTML completo / Hoja A4 / Diapositivas HTML / Word / preguntar cada vez): preguntar cada vez
- Modo (extenso y explicativo / corto y rápido / preguntar cada vez): preguntar cada vez
- Índice en los extensos (sí / no / preguntar cada vez): preguntar cada vez
- ¿Se imprime? (se imprime / solo digital / preguntar cada vez): preguntar cada vez
- ¿HTML y MD en una carpeta aparte y los PDF afuera, o todo junto? (aparte / todo junto / preguntar cada vez): preguntar cada vez
- Márgenes de impresión: los de carpeta por defecto (interior 20 mm, exterior 10, superior 15, inferior 5). Si usás otros, anotalos acá y cambialos en `sistema-visual/css/tokens.css`: [por defecto]

## Áreas de conocimiento de tu carrera
La IA aplica el estándar de resolución de cada área (ver `apoyo/estandares-por-area.md`). Marcá las que tu carrera cubre o escribí las tuyas; si tu carrera usa un área que no está en el catálogo, la IA te ayuda a sumarla.
- [ ] Matemática y cálculo
- [ ] Física y ciencias experimentales
- [ ] Química
- [ ] Programación y software
- [ ] Sistemas, redes y arquitectura de computadoras
- [ ] Datos, estadística e inteligencia artificial
- [ ] Ingeniería y diseño (mecánica, civil, eléctrica, industrial)
- [ ] Ciencias de la salud
- [ ] Ciencias económicas, contables y de gestión
- [ ] Derecho y ciencias sociales
- [ ] Humanidades, letras y educación
- [ ] Arquitectura, diseño y artes
- [ ] Otra: [completar]

## Trabajos prácticos
- Modelo de carátula de tu cátedra (campos que pide): número y título, materia, año, curso y tabla de integrantes (nombre y legajo o identificador). Si tu universidad pide otros, anotalos: [por defecto]
- Nombre de la columna de identificación de cada estudiante (legajo, matrícula, DNI, número de alumno): [Legajo]
- Logo de la institución para la carátula (ruta de un PNG, opcional): [sin logo]
- Los datos de los integrantes **no se anotan acá**: se pasan por el chat en cada trabajo.

## Herramientas instaladas en tu equipo
Anotá lo que ya tenés para que la IA no intente reinstalarlo. La guía de instalación está en `MANUAL-DE-IMPLEMENTACION.md`.
- Sistema operativo: [completar]
- Python 3.10 o superior: [completar sí/no]
- Pandoc 3.8 o superior: [completar sí/no]
- Navegador (Firefox, Chrome, Edge, Brave u otro basado en Chromium): [completar cuál]
- Graphviz / PlantUML (solo para diagramas grandes): [completar sí/no]
- Word o LibreOffice (para revisar `.docx`): [completar]

## Modelo de IA y herramienta
- Herramienta que usás (por ejemplo un asistente de programación en terminal, un editor con IA, un chat con proyectos): [completar]
- Modelo de uso diario y modelo para revisiones difíciles: [completar]
- ¿Permite subagentes o ejecutar comandos? [completar sí/no]

## Notas propias
Cualquier regla personal que quieras que valga siempre (se anota acá y no en la memoria de la herramienta, para que viaje con el proyecto):
-
