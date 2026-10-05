# Cómo contribuir

Las mejoras son bienvenidas. Este proyecto tiene una persona responsable (`@NicoPasiuscky`) y **ningún cambio entra al repositorio original sin su aprobación**: todo se propone con un *pull request* y se fusiona solo si lo aprueba.

## Cómo proponer un cambio
1. Hacé un fork del repositorio y creá una rama con un nombre descriptivo.
2. Hacé el cambio. Mantenelo acotado: un tema por pull request.
3. Si tocaste `sistema-visual/`, corré `python sistema-visual/construir.py` (necesita Pandoc 3.8 o superior y un navegador; ver `MANUAL-DE-IMPLEMENTACION.md`) y confirmá que las reglas siguen pasando. Si no pudiste correrlo, decilo en el pull request.
4. Abrí el pull request y completá la plantilla.
5. Puede haber preguntas o pedidos de ajuste. La decisión final es de quien mantiene el proyecto, que puede aceptar, pedir cambios o rechazar con una explicación.

## Qué se busca
- Estándares de áreas de conocimiento que faltan (`apoyo/estandares-por-area.md`), ideal si los escribe alguien que cursa o ejerce esa disciplina.
- Adaptadores para otras herramientas de IA (`adaptadores/`).
- Traducciones de los textos fijos de los documentos a otros idiomas.
- Correcciones y mejoras de los manuales y de los flujos, con evidencia de que funcionan mejor (por ejemplo, un caso que fallaba y ya no).
- Mejoras de portabilidad y de los programas de `sistema-visual/`.

## Qué no se acepta
- Datos personales o material de cátedra de terceros (apuntes, parciales, trabajos de nadie). Las demostraciones usan contenido inventado.
- Cambios que debiliten la regla de que la fuente manda o que hagan que el sistema dependa de un modelo o de una empresa en particular.
- Dependencias nuevas con licencias incompatibles con la del proyecto, sin discutirlo antes.
- Código o textos generados con IA que no se hayan revisado y probado: quien propone el cambio es responsable de su contenido.

## Licencia de los aportes
Al abrir un pull request aceptás que tu aporte se publique bajo las licencias del proyecto: **MIT** para el código (`LICENSE`) y **CC BY 4.0** para los textos (`LICENSE-TEXTOS.md`). No hace falta firmar ningún otro documento. Si tu aporte incluye código o material de otras personas, indicá su origen y su licencia en el pull request.

## Reglas de convivencia
Se espera un trato respetuoso. Los comentarios agresivos o discriminatorios se eliminan, y quien los escriba puede ser bloqueado.
