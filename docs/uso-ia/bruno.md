# Declaración de uso de IA — Bruno Maza

## Registro

| Integrante | Herramienta | Para qué la usó | Grado de intervención | Evidencia |
|---|---|---|---|---|
| Bruno Maza | Claude (Anthropic) | **Diagnóstico de la Fase 1:** análisis del código de mi parte, definición de los casos de prueba y redacción de la ficha de smells y de la tabla de resultados | **Alto.** La IA analizó las tres funciones, ejecutó los endpoints en su propio entorno para verificar los resultados esperados y redactó los dos documentos, incluido el análisis de cada hallazgo (impacto, riesgo, prioridad y principio). Yo ejecuté los 19 casos en mi entorno, capturé las 34 evidencias, verifiqué que cada resultado coincidiera y detecté un hallazgo adicional que el análisis no había previsto | `anexo/ia/bruno_registro_ia.md` |
| Bruno Maza | Claude (Anthropic) | **Pruebas de la Fase 2:** escritura de los 25 tests de mis tres endpoints y su posterior integración con el `conftest.py` del grupo | **Alto.** La IA escribió los tres archivos de tests a partir de los casos que yo había ejecutado en la Fase 1, y después los adaptó al fixture del grupo. Yo corrí la suite en mi entorno, resolví el merge con `dev`, verifiqué los 38 en verde y fijé la convención de nombre de la carpeta `tests` | `anexo/ia/bruno_registro_ia.md` |
| Bruno Maza | Claude (Anthropic) | **Refactoring de la Fase 3:** las cuatro extracciones sobre `app/routers/consultas.py`, la prueba de mutación previa y los 3 tests de cobertura que faltaban | **Alto.** La IA detectó con una prueba de mutación que el cálculo de vencidas no estaba cubierto, escribió los tests que lo cubren y aplicó las extracciones. Yo apliqué los cambios en mi entorno, corrí la suite después de cada paso (67 en verde), ordené los commits y abrí el PR | `anexo/ia/bruno_registro_ia.md` |

## Detalle

### Fase 1 — Diagnóstico

Usé Claude (Anthropic) para el diagnóstico de mi parte del sistema (`buscar`, `getSolicitud` y `reporte`, líneas 201–248 y 323–361).

La IA analizó el código, levantó el sistema en su propio entorno y ejecutó los endpoints para determinar qué devolvía cada caso. A partir de eso redactó la tabla de casos de prueba con los resultados esperados y la ficha de smells con el análisis de cada hallazgo.

Mi trabajo consistió en ejecutar los 19 casos en mi entorno desde Swagger UI, capturar las 34 evidencias, verificar que cada resultado coincidiera con lo esperado y revisar los hallazgos con el código a la vista.

Durante la ejecución del caso 2 escribí el estado en minúscula (`pend` en lugar de `PEND`) y el sistema devolvió una lista vacía. Ese resultado no estaba previsto en el análisis inicial: la búsqueda distingue mayúsculas y no avisa cuando el filtro no coincide, de modo que responde igual ante un error de tipeo que ante una búsqueda sin resultados. Se incorporó como caso 2b en la tabla y como hallazgo 11 en la ficha.

Los casos 17 y 18 no pueden reproducirse desde la interfaz, porque requieren cargar en la base una solicitud con la fecha mal formada. La IA escribió los dos scripts (`preparar_caso17.py` y `preparar_caso18.py`) y yo los ejecuté y capturé los tracebacks resultantes.

La ejecución confirmó los tres defectos principales del análisis: la inyección SQL en `buscar` (el filtro `estado=RES` devuelve 1 solicitud y `estado=' OR '1'='1` devuelve 6), el error 500 ante una comilla simple y el error 500 del reporte ante una fecha no parseable, con dos variantes distintas según el dato.

### Fase 2 — Pruebas

La IA escribió los 25 tests a partir de los casos que yo ya había ejecutado y verificado en la Fase 1, siguiendo el criterio de línea de base acordado por el grupo. Yo corrí la suite en mi entorno y renombré la carpeta a `tests`, fijando la convención que después usó todo el grupo.

La primera versión traía su propio `conftest.py`. Cristian detectó, revisando el PR, que entraba en conflicto con el del grupo y que mis tests no corrían con el suyo. La IA adaptó los cuatro archivos: el fixture `client_sin_excepciones` para los tres casos que esperan un 500, los dos fixtures que insertan las fechas defectuosas, y la reescritura del test de recuperación del reporte, que dependía del orden de ejecución. Yo hice el merge de `dev`, resolví el conflicto y verifiqué los 38 tests en verde antes de actualizar el PR.

El detalle de esta fase está en `docs/pruebas/bruno_resultados_fase2.md`.

### Fase 3 — Refactoring

Antes de refactorizar, la IA comprobó si la suite protegía lo que iba a tocar: cambió `dias_limite` para que devolviera 999 en lugar de 2 y corrió la suite completa. Los 64 tests siguieron en verde, lo que mostró que el cálculo de solicitudes vencidas no tenía ninguna cobertura. Escribió los 3 tests que lo cubren y verificó que pasaran también sobre el código sin refactorizar, antes de aplicar las extracciones.

Después aplicó las cuatro extracciones sobre `app/routers/consultas.py`, que dejaron seis funciones con nombre y redujeron el bucle de `reporte` de 25 líneas a 7.

Yo apliqué los cambios en mi entorno, corrí la suite después de cada paso, ordené los dos commits de modo que la cobertura quedara registrada antes del refactor, y abrí el PR.

El detalle de esta fase, con el antes y después de cada refactoring y las decisiones de diseño, está en `docs/refactoring/bruno_refactoring.md`.

## Registro de los pedidos

El detalle cronológico de cada pedido hecho a la IA, lo que devolvió y lo que hice con eso está en `anexo/ia/bruno_registro_ia.md`.
