# Fase 1 — Calidad externa: resultados observados

**Integrante:** Bruno Maza
**Alcance:** `GET /solicitudes`, `GET /solicitudes/{id}`, `GET /reporte` (líneas 201–248 y 323–361 de `main.py`, tag `estado-inicial`)
**Fecha de ejecución:** 1 de noviembre de 2026
**Entorno:** base limpia (`run.bat reset`), pruebas manuales desde Swagger UI (`/docs`)

## Criterio de evaluación de códigos HTTP

| Situación | Código esperado |
|---|---|
| Consulta correcta, con o sin resultados | 200 OK |
| Parámetro con tipo inválido | 422 Unprocessable Entity |
| El recurso no existe | 404 Not Found |
| Falla interna | 500, nunca por un dato enviado por el cliente |

## Resultados

| # | Qué se probó | Parámetros | HTTP | Qué respondió | ¿Está bien? | ¿Por qué? | Evidencia |
|---|---|---|---|---|---|---|---|
| 1 | Listado sin filtros | — | 200 | 6 solicitudes, de la más nueva a la más vieja | Sí | Devuelve el conjunto completo con el orden por defecto (`ORDER BY fecha_alta DESC`) | `caso01_sin_filtros_1.png`, `caso01_sin_filtros_2.png`, `caso01_sin_filtros_3.png` |
| 2 | Filtro por estado | `estado=PEND` | 200 | 2 solicitudes (id 6 y 1) | Sí | Filtra correctamente | `caso02_estado_pend.png` |
| 2b | Estado en minúscula | `estado=pend` | 200 | `[]` | No | La comparación distingue mayúsculas y minúsculas: en la base los estados se guardan como `PEND`, así que `pend` no coincide. Devuelve lista vacía sin ningún aviso, indistinguible de una búsqueda legítima sin resultados | `caso02b_estado_minuscula.png` |
| 3 | Filtro por prioridad | `prioridad=1` | 200 | 3 solicitudes (id 6, 4 y 3) | Sí | Filtra correctamente | `caso03_prioridad_1_1.png`, `caso03_prioridad_1_2.png` |
| 4 | Estado inexistente | `estado=XXXX` | 200 | `[]` | Sí | La lista vacía es la respuesta correcta: `XXXX` no es un estado del sistema y no hay nada que devolver | `caso04_estado_inexistente.png` |
| 5 | Orden por prioridad | `orden=prioridad` | 200 | 6 solicitudes, las de prioridad 1 primero | Sí | Aplica el orden solicitado | `caso05_orden_prioridad_1.png`, `caso05_orden_prioridad_2.png`, `caso05_orden_prioridad_3.png` |
| 6 | Valor de orden inventado | `orden=zzz` | 200 | 6 solicitudes en el orden por defecto | No | No falla, pero ignora el parámetro en silencio: el usuario cree que ordenó y no lo hizo | `caso06_orden_invalido_1.png`, `caso06_orden_invalido_2.png`, `caso06_orden_invalido_3.png` |
| 7 | Prioridad no numérica | `prioridad=alta` | 422 | `"Input should be a valid integer"` | Sí | El parámetro está declarado como entero, así que FastAPI valida el tipo antes de ejecutar la función | `caso07_prioridad_texto.png` |
| 8 | Fecha con formato inválido | `desde=ayer` | 200 | `[]` | No | Acepta una fecha inválida y devuelve lista vacía, como si no hubiera resultados. Debería rechazarla con 422 | `caso08_fecha_invalida.png` |
| 9a | Control previo a la inyección | `estado=RES` | 200 | 1 solicitud (id 4) | Sí | Resultado correcto del filtro, usado como referencia para el caso 9b | `caso09a_control_res.png` |
| 9b | **Inyección SQL** | `estado=' OR '1'='1` | 200 | **6 solicitudes** (todas) | **No** | **El mismo filtro que en 9a devolvía 1 solicitud ahora devuelve 6: el parámetro alteró la consulta que ejecuta la base y el filtro quedó anulado** | `caso09b_inyeccion_sql_1.png`, `caso09b_inyeccion_sql_2.png`, `caso09b_inyeccion_sql_3.png` |
| 10 | **Comilla simple suelta** | `texto='` | **500** | `Internal Server Error` | **No** | **Un dato del cliente rompe el servidor: la comilla deja la consulta mal formada y SQLite lanza `OperationalError` en la línea 225. Nunca debe responder 500 por un dato enviado por el cliente** | `caso10_comilla_500.png`, `caso10_terminal_traceback.png` |
| 11 | Detalle de solicitud existente | `GET /solicitudes/1` | 200 | Solicitud con su historial de cambios de estado | Sí | Devuelve el detalle completo | `caso11_detalle_existente.png` |
| 12 | Solicitud inexistente | `GET /solicitudes/99999` | 404 | `{"detail":"no existe"}` | Parcial | El código 404 es correcto, pero el mensaje no dice qué no existe ni qué id se buscó | `caso12_id_inexistente.png` |
| 13 | Id cero | `GET /solicitudes/0` | 404 | `{"detail":"no existe"}` | Sí | Coherente con el caso 12 | `caso13_id_cero.png` |
| 14 | Id negativo | `GET /solicitudes/-5` | 404 | `{"detail":"no existe"}` | Parcial | Un id negativo no es un dato inexistente sino imposible: correspondería 422, no 404. El sistema no distingue los dos casos | `caso14_id_negativo.png` |
| 15 | Id no numérico | `GET /solicitudes/abc` | 422 | `"Input should be a valid integer"` | Sí | FastAPI valida el tipo antes de ejecutar la función, igual que en el caso 7 | `caso15_id_no_numerico.png` |
| 16 | Reporte completo | `GET /reporte` | 200 | `total=6`, conteos por estado, tipo y área, `porcentaje_resueltas=16.67` y la lista de vencidas | Sí | El cálculo es correcto sobre los datos de prueba | `caso16_reporte_completo_1.png`, `caso16_reporte_completo_2.png` |
| 17 | **Reporte con fecha en otro formato** | Solicitud con `fecha_alta = '2026-11-01'` (sin hora) | **500** | `Internal Server Error` | **No** | **`datetime.strptime` (línea 347) exige exactamente `%Y-%m-%d %H:%M:%S`. Una sola solicitud con otro formato lanza `ValueError` y deja sin funcionar el reporte completo** | `caso17_reporte_500.png`, `caso17_terminal_traceback.png` |
| 18 | **Reporte con `fecha_alta` nula** | Solicitud con `fecha_alta = NULL` | **500** | `Internal Server Error` | **No** | **La misma línea 347 lanza ahora `TypeError: strptime() argument 1 must be str, not None`. Dos tipos de error distintos salen de la misma instrucción sin protección** | `caso18_reporte_500.png`, `caso18_terminal_traceback.png` |

## Observaciones

### Sobre los casos 2b, 6 y 8: fallas silenciosas

Los tres responden 200 y un resultado aparentemente normal, pero el parámetro enviado no se aplicó. El sistema no distingue entre una búsqueda legítima sin resultados y un parámetro mal escrito o inválido. El contraste con el caso 4 lo deja claro: ahí la lista vacía es correcta porque el estado no existe, mientras que en el 2b es un estado válido escrito en minúscula.

La diferencia con los casos 7 y 15, donde el sistema sí responde 422, es el tipo del parámetro: `prioridad` e `id` están declarados como enteros y FastAPI los valida automáticamente, mientras que `estado`, `orden` y `desde` son texto y pasan sin control. La validación que falta es la del código, no la del framework.

### Sobre los casos 17 y 18

El sistema permite guardar solicitudes con `fecha_alta` en otro formato o nula, porque no valida ese campo al registrar. Cuando eso ocurre, `/reporte` deja de responder para **todas** las solicitudes, no solo para la que está mal cargada. Es un defecto donde el error se manifiesta lejos del lugar donde se originó.

## Detalle del caso 9 (contraste)

```
estado=RES              ->  1 solicitud
estado=' OR '1'='1      ->  6 solicitudes
```

La consulta se arma concatenando texto (línea 206):

```python
q += " AND estado = '" + estado + "'"
```

Con el valor inyectado, la condición resultante es `AND estado = '' OR '1'='1'`, que es verdadera para todas las filas.

## Detalle del caso 10 (traceback)

```
File "main.py", line 225, in buscar
    c.execute(q)
sqlite3.OperationalError: unrecognized token: "''' ORDER BY fecha_alta DESC, id DESC"
```

## Detalle de los casos 17 y 18 (tracebacks)

```
File "main.py", line 347, in reporte
    fa = datetime.strptime(s[8], "%Y-%m-%d %H:%M:%S")
ValueError: time data '2026-11-01' does not match format '%Y-%m-%d %H:%M:%S'
```

```
File "main.py", line 347, in reporte
    fa = datetime.strptime(s[8], "%Y-%m-%d %H:%M:%S")
TypeError: strptime() argument 1 must be str, not None
```

## Cómo reproducir los casos 17 y 18

Los casos 1 a 16 se ejecutan desde Swagger UI. Los casos 17 y 18 requieren cargar en la base una solicitud con la fecha mal formada, lo que no es posible desde la interfaz. Para reproducirlos se usaron los scripts `preparar_caso17.py` y `preparar_caso18.py`, incluidos en esta carpeta:

```
.venv\Scripts\python preparar_caso17.py     (luego GET /reporte)
.venv\Scripts\python preparar_caso18.py     (luego GET /reporte)
.\run.bat reset                             (para dejar la base limpia)
```
