# Fase 1 — Calidad externa: resultados observados

**Integrante:** Gaston Paschetta
**Alcance:** `POST /solicitudes` (líneas 114–198 de `main.py`, tag `estado-inicial`)
**Fecha de ejecución:** 31/10/2026
**Entorno:** base limpia (`run.bat reset`), pruebas manuales desde Swagger UI (`/docs`), casos ejecutados en orden

## Criterio de evaluación de códigos HTTP

| Situación | Código esperado |
|---|---|
| Solicitud creada | 201 Created |
| Dato inválido o faltante | 422 Unprocessable Entity |
| El estudiante indicado no existe | 422 Unprocessable Entity (el recurso que se crea es la solicitud; el estudiante es un dato del body) |
| Falla interna | 500, nunca por un dato enviado por el cliente |

## Datos iniciales relevantes

| Dato | Valor en la base limpia |
|---|---|
| Estudiantes | 1 a 4 (Lucia Ferreyra, Mateo Quiroga, Sofia Aranda, Tomas Villalba) |
| Solicitudes | 1 a 6, así que la primera solicitud nueva es la 7 |

> Las solicitudes 7 y 11 no forman parte de los casos: la 7 es una primera ejecución del caso 1 que se repitió (quedó como 8) y la 11 una ejecución de prueba con `"prioridad": 1` numérico. Por eso el caso 1 es la solicitud 8, y el caso 11, que se repitió al final, es la 15.
| Tipos válidos | `CERT`, `EQUIV`, `MESA`, `RECLAMO`, `BAJA` |

## Resultados

| # | Qué se probó | Body enviado | HTTP | Qué respondió | ¿Está bien? | ¿Por qué? | Evidencia |
|---|---|---|---|---|---|---|---|
| 1 | Alta válida de tipo MESA | Estudiante 3, `MESA`, descripción válida | 200 | Solicitud 8, prioridad 1, área Bedelia, estado PEND | Parcial | Crea bien y asigna prioridad y área según el tipo, pero debería responder 201 Created | `caso1_alta_mesa.png` |
| 2 | Historial y notificación del alta | `GET /solicitudes/8` y `notificaciones.log` | 200 | Historial con `PEND` "alta de solicitud" y una línea de mail a sofia.aranda para la solicitud 8 en el log | Sí | El alta deja registro y notifica | `caso2_historial.png`, `caso2_notificaciones_log.png` |
| 3 | Prioridad automática por "urgente" | Estudiante 1, `CERT`, descripción con "urgente" | 200 | Solicitud 9 con prioridad 1 (un CERT normal es 3) | Sí | La regla se aplica. Ojo: `calcular_prioridad` no tiene esta regla (ver ficha, hallazgo 2) | `caso3_cert_urgente.png` |
| 4 | Prioridad indicada por el cliente | Estudiante 2, `MESA`, `"prioridad": 3` | 200 | Solicitud 10 con prioridad 3 | Sí | Respeta la prioridad enviada | `caso4_prioridad_explicita.png` |
| 5 | Falta el estudiante | Sin `estudiante_id` | 200 | `{"error":"falta estudiante"}` | Parcial | El error es correcto, pero debería responder 422 en vez de 200 | `caso5_falta_estudiante.png` |
| 6 | Estudiante inexistente | `"estudiante_id": 999` | 200 | `{"error":"estudiante no existe"}` | Parcial | Igual que el 5 | `caso6_estudiante_inexistente.png` |
| 7 | Tipo inválido | `"tipo": "BECA"` | 200 | `{"error":"tipo invalido"}` | Parcial | Igual que el 5 | `caso7_tipo_invalido.png` |
| 8 | Descripción corta | `"descripcion": "mesa"` | 200 | `{"error":"descripcion muy corta"}` | Parcial | Igual que el 5 | `caso8_descripcion_corta.png` |
| 9 | Descripción nula | `"descripcion": null` | 500 | `Internal Server Error` | No | Un dato del cliente rompe el servidor (`TypeError` en la línea 144). Debería responder 422 | `caso9_descripcion_null_500.png`, `caso9_terminal_traceback.png` |
| 10 | Descripción numérica | `"descripcion": 12345678901` | 500 | `Internal Server Error` | No | Igual que el 9: `len()` de un número | `caso10_descripcion_numero_500.png` |
| 11 | Descripción con solo espacios | `"descripcion"` de 12 espacios | 200 | Solicitud 15 creada con la descripción en blanco | No | Cuenta los espacios como texto; debería rechazarla con 422 | `caso11_descripcion_espacios.png` |
| 12 | Prioridad fuera de rango | `"prioridad": 7` | 200 | `{"error":"prioridad invalida"}` | Parcial | Igual que el 5 | `caso12_prioridad_7.png` |
| 13 | Prioridad como texto | `"prioridad": "1"` | 200 | `{"error":"prioridad invalida"}` | Parcial | Igual que el 5 | `caso13_prioridad_texto.png` |
| 14 | Prioridad booleana | `"prioridad": true` | 200 | Solicitud 12 creada con `"prioridad": true` | No | `True in [1, 2, 3]` da verdadero en Python, así que acepta un booleano como prioridad. Debería rechazarlo con 422 | `caso14_prioridad_true.png` |
| 15 | Canal inválido | Estudiante 4, `EQUIV`, `"canal": "FAX"` | 200 | Solicitud 13 creada con canal `WEB` | No | Cambia el dato sin avisar. La prioridad inválida se rechaza (caso 12) pero el canal inválido se corrige: el criterio es inconsistente | `caso15_canal_invalido.png` |
| 16 | Body que no es un objeto | `[1, 2]` | 422 | `"Input should be a valid dictionary"` | Sí | El código 422 es correcto, pero el formato (`detail`) no coincide con el del resto de los errores (`error`) | `caso16_body_lista_422.png` |
| 17 | Notificación a un estudiante sin email | Primero `POST /estudiantes` sin `email` (queda el estudiante 5), después alta de solicitud para el estudiante 5 | 200 | Solicitud 14 creada; en `notificaciones.log` queda "Se envio mail a : su solicitud 14 fue registrada" | No | Registra como enviado un mail sin destinatario. Debería avisar que no se pudo notificar | `caso17a_estudiante_sin_email.png`, `caso17b_alta_solicitud.png`, `caso17c_notificaciones_log.png` |

## Detalle de los casos 9 y 10 (traceback)

```
File "...\main.py", line 144, in registrar
    if "descripcion" not in data or len(data["descripcion"]) < 10:
TypeError: object of type 'NoneType' has no len()
```

La validación revisa que la clave `descripcion` exista, pero no que su valor sea un texto. Con `null` o con un número, `len()` falla y la excepción llega sin controlar al servidor.

## Conclusiones de calidad externa

- **Funcionalidad básica:** con datos válidos el alta funciona: asigna prioridad y área según el tipo, registra el historial y deja la notificación (casos 1 a 4).
- **Contrato HTTP inconsistente:** todos los errores de validación responden 200 (casos 5 a 8, 12 y 13), dos datos inválidos producen 500 (casos 9 y 10) y solo el body que no es objeto responde 422, con otro formato (caso 16).
- **Validación incompleta e inconsistente:** acepta una descripción en blanco (caso 11) y una prioridad booleana (caso 14), y frente a un dato inválido a veces rechaza (prioridad) y a veces corrige en silencio (canal, caso 15).
- **Notificación poco confiable:** se da por enviado un mail sin destinatario (caso 17).

## Vínculo con la ficha de smells

| Hallazgo de la ficha | Casos que lo evidencian |
|---|---|
| 2. Duplicated Code / Dead Code en la prioridad | 3 |
| 4. Manejo de errores inconsistente | 5, 6, 7, 8, 12, 13 (errores con 200), 9 y 10 (500), 16 (422 con otro formato) |
| 5. Falta de modelo de entrada y validación inconsistente | 9, 10, 11, 13, 14, 15 |
| 7. Excepción silenciada en la notificación | 17 |
