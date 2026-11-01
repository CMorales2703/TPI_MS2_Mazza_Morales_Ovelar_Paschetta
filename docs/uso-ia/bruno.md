# Declaración de uso de IA — Bruno Maza

## Registro

| Integrante | Herramienta | Para qué la usó | Grado de intervención | Evidencia |
|---|---|---|---|---|
| Bruno Maza | Claude (Anthropic) | **Diagnóstico de la Fase 1:** análisis del código de mi parte, definición de los casos de prueba y redacción de la ficha de smells y de la tabla de resultados | **Alto.** La IA analizó las tres funciones, ejecutó los endpoints en su propio entorno para verificar los resultados esperados y redactó los dos documentos, incluido el análisis de cada hallazgo (impacto, riesgo, prioridad y principio). Yo ejecuté los 19 casos en mi entorno, capturé las 34 evidencias, verifiqué que cada resultado coincidiera y detecté un hallazgo adicional que el análisis no había previsto | `anexo/ia/bruno_claude_01_diagnostico.pdf` |

## Detalle

Usé Claude (Anthropic) para el diagnóstico de mi parte del sistema (`buscar`, `getSolicitud` y `reporte`, líneas 201–248 y 323–361).

La IA analizó el código, levantó el sistema en su propio entorno y ejecutó los endpoints para determinar qué devolvía cada caso. A partir de eso redactó la tabla de casos de prueba con los resultados esperados y la ficha de smells con el análisis de cada hallazgo.

Mi trabajo consistió en ejecutar los 19 casos en mi entorno desde Swagger UI, capturar las 34 evidencias, verificar que cada resultado coincidiera con lo esperado y revisar los hallazgos con el código a la vista.

Durante la ejecución del caso 2 escribí el estado en minúscula (`pend` en lugar de `PEND`) y el sistema devolvió una lista vacía. Ese resultado no estaba previsto en el análisis inicial: la búsqueda distingue mayúsculas y no avisa cuando el filtro no coincide, de modo que responde igual ante un error de tipeo que ante una búsqueda sin resultados. Se incorporó como caso 2b en la tabla y como hallazgo 11 en la ficha.

Los casos 17 y 18 no pueden reproducirse desde la interfaz, porque requieren cargar en la base una solicitud con la fecha mal formada. La IA escribió los dos scripts (`preparar_caso17.py` y `preparar_caso18.py`) y yo los ejecuté y capturé los tracebacks resultantes.

La ejecución confirmó los tres defectos principales del análisis: la inyección SQL en `buscar` (el filtro `estado=RES` devuelve 1 solicitud y `estado=' OR '1'='1` devuelve 6), el error 500 ante una comilla simple y el error 500 del reporte ante una fecha no parseable, con dos variantes distintas según el dato.
