# Registro de interacciones con IA — Bruno Maza

**Herramienta:** Claude (Anthropic)
**Fases:** 1 — Diagnóstico, 2 — Pruebas y 3 — Refactoring
**Qué es este documento:** un resumen de los pedidos técnicos hechos a la IA, lo que devolvió y lo hecho con eso.

## Pedidos

| # | Fecha | Pedido (resumido) | Qué devolvió la IA | Qué hice yo |
|---|---|---|---|---|
| 1 | 31/10/2026 | Qué pide el TPI y qué me toca a mí dentro del grupo, a partir de la consigna y del plan de trabajo | Un panorama de las cinco fases, mi alcance (`buscar`, `getSolicitud` y `reporte`) y la técnica que me toca garantizar (Extract Method) | Lo usé para ordenar mi parte y confirmar el alcance con el grupo |
| 2 | 01/11/2026 | Analizar mis tres funciones y preparar el diagnóstico de la Fase 1 | La tabla de 19 casos de prueba con el resultado esperado de cada uno, la ficha con 13 hallazgos (ubicación, evidencia, impacto, riesgo, prioridad y principio) y los scripts `preparar_caso17.py` y `preparar_caso18.py` | Ejecuté los 19 casos en mi entorno desde Swagger UI, capturé las 34 evidencias y verifiqué que cada resultado coincidiera con lo previsto |
| 3 | 01/11/2026 | Revisar un resultado que no coincidía con lo esperado: el estado `pend` en minúscula devolvía lista vacía | El análisis de por qué pasa y la propuesta de incorporarlo como caso 2b y hallazgo 11 | El hallazgo salió de ejecutar el caso, no del análisis previo. Lo sumé a la tabla y a la ficha, y abrí el PR #8 |
| 4 | 01/11/2026 | Pasar mis casos de la Fase 1 a tests automáticos con el criterio de línea de base del grupo | `tests/test_buscar.py`, `tests/test_detalle.py`, `tests/test_reporte.py` (25 casos) y un `conftest.py` propio | Corrí la suite, renombré la carpeta a `tests` para fijar la convención del grupo, hice los commits y abrí el PR #9 |
| 5 | 04/11/2026 | Integrar mi suite con el `conftest.py` del grupo, después de que Cristian señalara el conflicto | Los cuatro archivos adaptados y probados: fixture `client_sin_excepciones`, los dos fixtures de fechas defectuosas y el test de recuperación del reporte reescrito para no depender del orden | Hice el merge de `dev` en mi rama, resolví el conflicto, corrí la suite completa (38 en verde) y actualicé el PR |
| 6 | 06/11/2026 | Refactorizar mis tres endpoints con Extract Method, sobre la estructura nueva de `app/routers/` | Primero una prueba de mutación que mostró que el cálculo de vencidas no estaba cubierto; después los 3 tests que lo cubren y las cuatro extracciones (6 funciones) | Apliqué los cambios, corrí la suite después de cada paso (67 en verde), hice los dos commits en orden y abrí el PR #17 |
| 7 | 07/11/2026 | Redactar los documentos de la Fase 2 y de la Fase 3 con el formato que usaron Cristian y Gastón | `docs/pruebas/bruno_resultados_fase2.md` y `docs/refactoring/bruno_refactoring.md` | Los revisé contra el código y abrí el PR |

## Observaciones

El grado de intervención de la IA fue alto en el análisis y en la redacción, y bajo en la ejecución y la verificación, que quedaron de mi lado en todas las fases.

Dos cosas no salieron de la IA. El hallazgo 11 apareció al ejecutar el caso 2 en mi entorno, escribiendo el estado en minúscula: el análisis previo no lo había contemplado. Y el conflicto entre mi `conftest.py` y el del grupo lo detectó Cristian revisando mi PR, no yo ni la IA.

La prueba de mutación del pedido 6 —cambiar a mano una regla del código y comprobar si algún test falla— la adoptó después Gastón para verificar su propia cobertura antes de refactorizar, según consta en `docs/refactoring/gaston_refactoring.md`.
