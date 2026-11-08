# Fase 2 — Pruebas automatizadas: línea de base

**Integrante:** Bruno Maza
**Alcance:** `GET /solicitudes`, `GET /solicitudes/{id}`, `GET /reporte` (líneas 201–248 y 323–361 de `main.py`, tag `estado-inicial`)
**Herramientas:** pytest + `TestClient` de FastAPI
**Archivos:** `tests/test_buscar.py`, `tests/test_detalle.py`, `tests/test_reporte.py` (usan los fixtures `client` y `client_sin_excepciones` de `tests/conftest.py`)
**Cómo se ejecuta:** `.\run.bat test`
**Resultado:** 25 tests, 25 en verde (suite completa al momento del merge: 38 tests, 38 en verde)

## Criterio: línea de base

Se sigue el mismo criterio que en `cristian_resultados_fase2.md`: cada test verifica lo que el sistema hace **hoy**, aunque sea incorrecto.

Un test que esperara el comportamiento correcto estaría en rojo desde el primer día y no serviría como red de seguridad para el refactor. Lo que se busca es detectar un cambio no intencional, no señalar lo que falta corregir.

La diferencia de forma con los demás integrantes está en cómo se marcan esos casos. Acá los tests que documentan un defecto llevan el prefijo `DEFECTO` en el nombre, con el caso de la Fase 1 y el hallazgo citados en el docstring; Cristian, Javier y Gastón lo indican en el nombre del test (`acepta_...`, `no_registra_...`) más un comentario `# Actual: ... Esperado: ...`. Las dos formas cumplen la misma función y conviven en la suite; se deja constancia del criterio porque no se unificó.

Cuando un defecto se corrija, el test que lo documenta va a fallar. Eso es lo esperado, y corresponde actualizarlo en el mismo PR de la corrección para que el cambio de comportamiento quede visible en la revisión.

## Qué verifica cada test

Además del código HTTP y del cuerpo de la respuesta:

- **Listado:** la cantidad de solicitudes devueltas y que todas cumplan el filtro aplicado, no solo que la respuesta tenga el campo.
- **Orden:** que la lista resultante esté efectivamente ordenada, comparándola con la misma lista ordenada.
- **Detalle:** que traiga el campo `historial`, que es lo único que lo distingue del listado.
- **Reporte:** que los tres agrupamientos sumen el total y que el porcentaje se corresponda con el conteo de `RES`. Son invariantes: si un refactor pierde o duplica una solicitud en alguno de los agrupamientos, dejan de cumplirse.

Los tres casos que esperan un 500 usan `client_sin_excepciones`, para que la excepción llegue como respuesta en lugar de cortar el test. El resto usa `client`, de modo que un error inesperado muestre el traceback.

Los casos 17 y 18 necesitan una solicitud con la fecha mal formada, que no puede cargarse desde la interfaz. La insertan los fixtures `solicitud_con_fecha_invalida` y `solicitud_con_fecha_nula`, agregados al `conftest.py` del grupo.

## Tests y casos

### `GET /solicitudes` (`test_buscar.py`)

| Caso Fase 1 | Test | Actual | Esperado | Hallazgos |
|---|---|---|---|---|
| 1 | `test_sin_filtros_devuelve_todas` | 200, las 6 solicitudes de prueba | 200 | — |
| 1 | `test_orden_por_defecto_es_por_fecha` | 200, de la más nueva a la más vieja | 200 | — |
| 2 | `test_filtro_por_estado` | 200, solo las 2 pendientes | 200 | — |
| 3 | `test_filtro_por_prioridad` | 200, solo las 3 de prioridad 1 | 200 | — |
| 4 | `test_estado_inexistente_devuelve_lista_vacia` | 200, lista vacía | 200 | — |
| 5 | `test_orden_por_prioridad` | 200, ordenadas de 1 a 3 | 200 | — |
| 7 | `test_prioridad_no_numerica_es_rechazada` | 422, lo valida FastAPI antes de ejecutar | 422 | — |
| 2b | `test_DEFECTO_busqueda_distingue_mayusculas` | 200, `pend` devuelve lista vacía sin ningún aviso | Encontrar las `PEND`, o avisar que el valor no es válido | 11 |
| 6 | `test_DEFECTO_orden_invalido_se_ignora_en_silencio` | 200, usa el orden por defecto sin avisar | 422 | 9 |
| 8 | `test_DEFECTO_fecha_invalida_se_ignora_en_silencio` | 200, acepta `ayer` como fecha y devuelve lista vacía | 422 | 10 |
| 9a, 9b | `test_DEFECTO_inyeccion_sql_evade_el_filtro` | 200, `estado=RES` devuelve 1 y `estado=' OR '1'='1` devuelve las 6 | Lista vacía | 1 |
| 10 | `test_DEFECTO_comilla_simple_rompe_el_servidor` | 500, `OperationalError` de SQLite | 422 | 1 |

### `GET /solicitudes/{id}` (`test_detalle.py`)

| Caso Fase 1 | Test | Actual | Esperado | Hallazgos |
|---|---|---|---|---|
| 11 | `test_devuelve_la_solicitud_con_su_historial` | 200, incluye el campo `historial` | 200 | — |
| 12 | `test_id_inexistente_devuelve_404` | 404, `detail: "no existe"` | 404 | — |
| 13 | `test_id_cero_devuelve_404` | 404 | 404 | — |
| 15 | `test_id_no_numerico_es_rechazado` | 422, lo valida FastAPI | 422 | — |
| 14 | `test_DEFECTO_id_negativo_devuelve_404_en_lugar_de_422` | 404 | 422: un id negativo no es un dato inexistente sino imposible | — |
| — | `test_el_detalle_no_es_vulnerable_a_inyeccion` | 422 | 422 | 1 |

El último no corresponde a ningún caso de la Fase 1: se agregó como contraste del hallazgo 1. `getSolicitud` usa una consulta parametrizada (`WHERE id = ?`, línea 237) y por eso no es vulnerable, mientras que `buscar` concatena texto. Documentar las dos conductas en la misma suite deja a la vista que la diferencia está en cómo se arma la consulta y no en el endpoint.

### `GET /reporte` (`test_reporte.py`)

| Caso Fase 1 | Test | Actual | Esperado | Hallazgos |
|---|---|---|---|---|
| 16 | `test_devuelve_todos_los_agrupamientos` | 200, trae los conteos, el porcentaje y las vencidas | 200 | — |
| — | `test_el_total_coincide_con_el_listado` | El total es igual a la cantidad que devuelve `GET /solicitudes` | Lo mismo | — |
| — | `test_los_conteos_suman_el_total` | Los tres agrupamientos suman el total | Lo mismo | — |
| — | `test_el_porcentaje_de_resueltas_es_coherente` | El porcentaje corresponde al conteo de `RES` | Lo mismo | — |
| 17 | `test_DEFECTO_fecha_con_otro_formato_rompe_el_reporte` | 500, `ValueError` en la línea 347 | 200, ignorando o reportando el dato inválido | 2 |
| 18 | `test_DEFECTO_fecha_nula_rompe_el_reporte` | 500, `TypeError` en la misma línea | 200 | 2 |
| — | `test_DEFECTO_el_reporte_se_recupera_al_quitar_el_dato_malo` | 500 con el dato defectuoso, 200 al borrarlo | 200 en los dos casos | 2 |

Los tres últimos tests muestran algo que en la Fase 1 quedaba disperso: una sola instrucción sin protección produce dos errores distintos según el dato, y el endpoint completo deja de funcionar aunque las otras seis solicitudes estén bien. El tercero agrega que el fallo viene del dato y no deja el sistema en un estado inconsistente: al quitar la solicitud defectuosa el reporte vuelve a responder, sin reiniciar nada.

## Integración con el `conftest.py` del grupo

La primera versión de esta suite traía su propio `conftest.py`, con una sola base para toda la corrida. Al integrarla con `dev` quedó descartado en favor del del grupo, que crea una base nueva por test.

El criterio del grupo es el correcto y conviene dejar escrito por qué: con una base compartida los tests quedan encadenados, y lo que hace uno lo ve el siguiente. Esta suite tenía un caso que dependía de eso — el de recuperación del reporte funcionaba porque corría después de los otros dos y heredaba la base ya limpiada. Con una base por test había que reescribirlo para que se valiera por sí mismo, que es lo que se hizo: inserta el dato defectuoso, verifica el 500, lo borra y verifica el 200, todo dentro del mismo test.

Al `conftest.py` del grupo se le agregaron tres cosas: el fixture `client_sin_excepciones`, que devuelve el 500 como respuesta en lugar de cortar el test, y los dos fixtures que insertan las fechas defectuosas de los casos 17 y 18.

## Evidencia

`docs/evidencias/fase2/bruno/bruno_fase2_01_suite_completa.png`: ejecución de la suite completa ya integrada con la de Cristian. Resultado: 38 passed.

El warning `StarletteDeprecationWarning` sobre `httpx` viene de las versiones de las librerías, no del código del sistema. No afecta los resultados.
