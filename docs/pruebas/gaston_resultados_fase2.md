# Fase 2 — Pruebas automatizadas: línea de base

**Integrante:** Gaston Paschetta
**Alcance:** `POST /solicitudes` (líneas 114–198 de `main.py`, tag `estado-inicial`)
**Herramientas:** pytest + `TestClient` de FastAPI
**Archivos:** `tests/test_solicitudes.py` (usa los fixtures `client` y `client_sin_excepciones` de `tests/conftest.py`)
**Cómo se ejecuta:** `.\run.bat test`
**Resultado:** 17 tests, 17 en verde (suite completa: 64 tests, 64 en verde)

## Criterio: línea de base

Se sigue el mismo criterio que en `cristian_resultados_fase2.md`: cada test verifica lo que el sistema hace **hoy**, aunque sea incorrecto, y el comportamiento esperado queda escrito en un comentario (`# Actual: ... Esperado: ...`), con el criterio de códigos HTTP de la Fase 1 (`docs/diagnostico/gaston_resultados_fase1.md`).

Los tests de casos que el sistema acepta y no debería llevan en el nombre lo que pasa hoy (`acepta_descripcion_en_blanco`, `acepta_prioridad_booleana`, `canal_invalido_se_guarda_como_web`).

Hay un test por cada uno de los 17 casos de la Fase 1, con el mismo número en el docstring.

## Qué verifica cada test

Además del código HTTP y la respuesta, cada test comprueba el efecto en la base:

- **Altas:** la solicitud guardada (`GET /solicitudes/{id}`) coincide con la respuesta. En el caso 1 también se verifica la fila del historial (`None` → `PEND`, "alta de solicitud").
- **Errores:** la cantidad de solicitudes es la misma antes y después del POST.
- **Notificación (casos 2 y 17):** la última línea de `notificaciones.log` corresponde a la solicitud creada.

Los casos 9 y 10 usan `client_sin_excepciones`, para que el `TypeError` llegue como 500 en lugar de cortar el test.

`notificaciones.log` se escribe en la carpeta actual, igual que la base. Como el fixture `client` se para en una carpeta temporal, los tests leen y escriben un log propio y no tocan el de la carpeta del proyecto.

## Tests y casos

| Caso Fase 1 | Test | Actual | Esperado | Hallazgos |
|---|---|---|---|---|
| 1 | `test_registrar_solicitud_valida` | 200, la crea con prioridad 1, área Bedelia, estado `PEND` y la fila del historial | 201 | — |
| 2 | `test_registrar_solicitud_notifica_al_estudiante` | Deja en el log el mail a sofia.aranda para la solicitud creada | Lo mismo | — |
| 3 | `test_registrar_cert_urgente_sube_prioridad` | 200, un `CERT` con "urgente" queda con prioridad 1 | 201, prioridad 1 | 2 |
| 4 | `test_registrar_respeta_prioridad_enviada` | 200, guarda la prioridad 3 enviada | 201, prioridad 3 | — |
| 5 | `test_registrar_sin_estudiante` | 200 con error, no la crea | 422 | 4 |
| 6 | `test_registrar_estudiante_inexistente` | 200 con error, no la crea | 422 | 4 |
| 7 | `test_registrar_tipo_invalido` | 200 con error, no la crea | 422 | 4 |
| 8 | `test_registrar_descripcion_corta` | 200 con error, no la crea | 422 | 4 |
| 9 | `test_registrar_descripcion_null` | 500 (`TypeError`), no la crea | 422 | 4, 5 |
| 10 | `test_registrar_descripcion_numerica` | 500 (`TypeError`), no la crea | 422 | 4, 5 |
| 11 | `test_registrar_acepta_descripcion_en_blanco` | 200, la crea con 12 espacios como descripción | 422 | 5 |
| 12 | `test_registrar_prioridad_fuera_de_rango` | 200 con error, no la crea | 422 | 4 |
| 13 | `test_registrar_prioridad_como_texto` | 200 con error, no la crea | 422 | 4, 5 |
| 14 | `test_registrar_acepta_prioridad_booleana` | 200, responde `"prioridad": true` y guarda 1 | 422 | 5 |
| 15 | `test_registrar_canal_invalido_se_guarda_como_web` | 200, cambia `FAX` por `WEB` sin avisar | 422 | 5 |
| 16 | `test_registrar_body_lista_responde_otro_formato` | 422 con formato `detail`, no la crea | 422 con formato `error` | 4 |
| 17 | `test_registrar_notifica_a_estudiante_sin_email` | Deja en el log "Se envio mail a : su solicitud N fue registrada" | Avisar que no se pudo notificar | 7 |

El caso 14 muestra un detalle que en la Fase 1 no se veía: la respuesta devuelve `true`, pero en la base queda guardado `1`, así que la respuesta y lo guardado no coinciden.

## Evidencia

`docs/evidencias/fase2/gaston/prueba_antes.png`: ejecución de la suite completa sobre la rama `test/gaston`, con `main.py` sin cambios respecto de `estado-inicial`. Resultado: 64 passed.

El warning `StarletteDeprecationWarning` sobre `httpx` viene de las versiones de las librerías, no del código del sistema. No afecta los resultados.
