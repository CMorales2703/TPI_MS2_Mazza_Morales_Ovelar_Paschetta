# Fase 1 — Calidad externa: resultados observados

**Integrante:** Cristian Morales
**Alcance:** `POST/GET /estudiantes`, `POST/GET /responsables` (líneas 1–111 de `main.py`, tag `estado-inicial`)
**Fecha de ejecución:** 19/10/2026 (headers: 20/10/2026 00:21–00:28 GMT)
**Entorno:** base limpia (`run.bat reset`), pruebas manuales desde Swagger UI (`/docs`)

## Criterio de evaluación de códigos HTTP

| Situación | Código esperado |
|---|---|
| Recurso creado | 201 Created |
| Dato inválido o faltante | 422 Unprocessable Entity |
| Choca con un dato existente (duplicado) | 409 Conflict |
| El recurso no existe | 404 Not Found |
| Falla interna | 500, nunca por un dato enviado por el cliente |

## Resultados

| # | Qué se probó | Body enviado | HTTP | Qué respondió | ¿Está bien? | ¿Por qué? | Evidencia |
|---|---|---|---|---|---|---|---|
| 1 | Alta de estudiante válido | Datos completos, legajo `TUP-2001` | 200 | Estudiante creado (`id` 5) | Parcial | Crea bien, pero debería responder 201 Created | `caso01_alta_ok.png` |
| 2 | Alta sin apellido | Sin el campo `apellido` | 200 | `{"error":"falta apellido"}` | Parcial | El error es correcto, pero debería responder 422 en vez de 200 | `caso02_falta_apellido.png` |
| 3 | Legajo repetido | Mismo body que el caso 1 | 200 | `{"error":"legajo repetido"}` | Parcial | Detecta el duplicado, pero debería responder 409 Conflict en vez de 200 | `caso03_legajo_repetido.png` |
| 4 | Email inválido | `"email":"@"` | 200 | Estudiante creado (`id` 6) con email `"@"` | No | No valida el formato del email; debería rechazarlo con 422 | `caso04_email_arroba.png` |
| 5 | Nombre nulo | `"nombre":null` | 200 | `{"error":"falta nombre"}` | Parcial | Igual que el 2 | `caso05_nombre_null.png` |
| 6 | Apellido nulo | `"apellido":null` | 200 | Estudiante creado (`id` 7) con `apellido: null` | No | Crea un estudiante sin apellido; debería rechazarlo con 422 y un mensaje de error | `caso06_apellido_null.png` |
| 7 | Área inexistente | `"area":"Sistemas"` | 200 | `{"error":"area invalida"}` | Parcial | Igual que el 2 | `caso07_area_invalida.png` |
| 8a | Alta de responsable | `Laura Gil`, `Bedelia` | 200 | Responsable creado (`id` 6) | Parcial | Igual que el 1 | `caso08a_responsable_alta.png` |
| 8b | Responsable repetido | Mismo body que el 8a | 200 | Responsable creado (`id` 7) | No | No verifica duplicados; debería responder 409 con un mensaje de error | `caso08b_responsable_duplicado.png` |
| 9a | Listado de estudiantes | — | 200 | 7 estudiantes, incluidos los de los casos 4 y 6 | Sí | El listado funciona; evidencia que se guardaron los datos inválidos de los casos 4 y 6 | `caso09a_listado_estudiantes_1.png`, `caso09a_listado_estudiantes_2.png` |
| 9b | Listado de responsables | — | 200 | 7 responsables, con el 6 y el 7 idénticos | Sí | El listado funciona; evidencia el duplicado del 8b | `caso09b_listado_responsables_1.png`, `caso09b_listado_responsables_2.png` |
| 10 | Email nulo | `"email":null` | 500 | `Internal Server Error` | No | Un dato del cliente rompe el servidor (`TypeError` en la línea 67). Debería aceptar el email nulo o rechazarlo con 422, nunca responder 500 | `caso10_email_null_500.png`, `caso10_email_null_500_repeticion.png`, `caso10_terminal_traceback_1.png`, `caso10_terminal_traceback_2.png` |
| 11a | Legajo nulo | `"legajo":null` | 200 | Estudiante creado (`id` 8) con `legajo: null` | No | Crea un estudiante sin legajo, que es obligatorio; debería rechazarlo con 422 | `caso11c_listado_legajos_null.png` (registro `id` 8) |
| 11b | Legajo nulo repetido | Mismo body que el 11a | 200 | Estudiante creado (`id` 9) con `legajo: null` | No | Igual que el 8b: no detecta el duplicado y debería responder 409 | `caso11b_legajo_null_duplicado.png`, `caso11c_listado_legajos_null.png` |
| 12 | Body que no es un objeto | `[1, 2]` | 422 | `"Input should be a valid dictionary"` | Sí | El código 422 es correcto, pero el mensaje es poco claro y el formato (`detail`) no coincide con el del resto de los errores (`error`) | `caso12_body_lista_422.png` |

## Detalle del caso 10 (traceback)

```
File "...\main.py", line 67, in crear_estudiante
    if "email" in data and "@" not in data["email"]:
TypeError: argument of type 'NoneType' is not a container or iterable
```

La validación verifica que la clave `email` exista, pero no que su valor sea un texto. Con `null` intenta buscar `@` dentro de `None`. Como no hay manejo de errores, la excepción llega sin controlar al servidor y se responde 500.

## Conclusiones de calidad externa

- **Funcionalidad básica:** las altas y los listados funcionan con datos válidos.
- **Contrato HTTP inconsistente:** los errores de validación responden 200 (casos 2, 3, 5 y 7), un dato inválido produce 500 (caso 10) y FastAPI responde 422 solo cuando el body no es un objeto (caso 12). Además hay dos formatos de error distintos (`error` y `detail`). El cliente no puede distinguir un éxito de un error por el código HTTP.
- **Validación incompleta e inconsistente:** se aceptan emails inválidos (caso 4) y valores `null` en campos obligatorios (casos 6 y 11a), y el comportamiento cambia según el campo (casos 5 y 6).
- **Integridad de datos:** se persisten registros duplicados (casos 8b y 11b) e incompletos (casos 6 y 11a). El control de legajo repetido falla con legajos nulos.
- **Defecto comprobado:** el caso 10 no es un riesgo leído en el código sino una falla reproducible del servidor.

## Vínculo con la ficha de smells

| Hallazgo de la ficha | Casos que lo evidencian |
|---|---|
| Manejo de errores inconsistente | 2, 3, 5, 7 (errores con 200), 10 (500), 12 (422 con otro formato) |
| Duplicated Code: validación de email frágil | 4, 10 |
| Falta de modelo de entrada (`data: dict`) | 4, 6, 10, 11a, 12 |
| Integridad de datos insuficiente | 8b, 9b, 11b |
