# Fase 2 — Pruebas automatizadas: línea de base

**Integrante:** Cristian Morales
**Alcance:** `POST/GET /estudiantes`, `POST/GET /responsables` (líneas 1–111 de `main.py`, tag `estado-inicial`)
**Herramientas:** pytest + `TestClient` de FastAPI
**Archivos:** `tests/conftest.py`, `tests/test_estudiantes.py`, `tests/test_responsables.py`, `pytest.ini`
**Cómo se ejecuta:** `.\run.bat test`
**Resultado:** 11 tests, 11 en verde

## Objetivo

Antes de refactorizar, los tests fijan el comportamiento actual del sistema. En la Fase 3 sirven para comprobar que un refactoring no cambió ese comportamiento.

## Criterio: línea de base

Cada test verifica lo que el sistema hace **hoy**, aunque sea incorrecto. El comportamiento esperado queda escrito en un comentario (`# Actual: ... Esperado: ...`), con el mismo criterio de códigos HTTP que la Fase 1.

Esto separa dos tipos de cambio en la Fase 3:

- **Refactoring:** no cambia el comportamiento, así que todos los tests siguen en verde sin tocarlos.
- **Corrección de defecto:** cambia el comportamiento a propósito (por ejemplo, de 200 o 500 a 422), así que el test correspondiente falla y se actualiza su expectativa. Cada actualización tiene que estar justificada por un hallazgo de la ficha.

Los tests de casos que el sistema acepta y no debería llevan en el nombre lo que pasa hoy (`acepta_email_invalido`, `acepta_duplicado`), para que no se lean como el comportamiento deseado.

## Base de datos aislada

`import main` crea `solicitudes.db` en la carpeta actual y carga los datos de prueba (hallazgo 2). Para que cada test arranque igual sin modificar `main.py`, el fixture `client` de `conftest.py`:

1. se para en una carpeta temporal nueva (`tmp_path` + `monkeypatch.chdir`);
2. quita `main` de `sys.modules` para que se vuelva a importar;
3. importa `main`, que crea una base nueva con los datos de prueba en esa carpeta;
4. entrega un `TestClient` y, al terminar, cierra la conexión.

Verificación: la fecha de modificación de la `solicitudes.db` real es la misma antes y después de correr los tests (`docs/evidencias/fase2/cristian/base_aislada.png`).

## Qué verifica cada test

Además del código HTTP y la respuesta, cada test comprueba el efecto en la base:

- **Altas:** el registro guardado (buscado por el `id` de la respuesta) coincide con la respuesta y con el dato enviado.
- **Errores:** la cantidad de registros es la misma antes y después del POST.
- **Duplicados:** los dos POST devuelven ids distintos y los dos registros existen.

## Tests y casos

| Caso Fase 1 | Test | Actual | Esperado | Hallazgos |
|---|---|---|---|---|
| 1 | `test_crear_estudiante_valido` | 200, lo crea | 201 | — |
| 1 (variante) | `test_crear_estudiante_sin_carrera_usa_default` | 200, lo crea con `TUP` | 201 | — |
| 2 | `test_crear_estudiante_sin_apellido` | 200 con error, no lo crea | 422 | 3 |
| 3 | `test_crear_estudiante_con_legajo_repetido_devuelve_error` | 200 con error, no lo crea | 409 | 3 |
| 4 | `test_crear_estudiante_acepta_email_invalido` | 200, lo crea con `"@"` | 422 | 4, 5 |
| 6 | `test_crear_estudiante_acepta_apellido_nulo` | 200, lo crea con `null` | 422 | 5, 11 |
| 7 | `test_crear_responsable_area_invalida` | 200 con error, no lo crea | 422 | 3, 6 |
| 8a | `test_crear_responsable_valido` | 200, lo crea activo | 201 | — |
| 8b | `test_crear_responsable_acepta_duplicado` | 200, crea un duplicado | 409 | 11 |
| 10 | `test_crear_estudiante_email_null` | 500 (`TypeError`), no lo crea | 422 | 3, 4, 5 |
| 11a/11b | `test_crear_estudiante_acepta_legajo_nulo_repetido` | 200, crea dos registros con legajo `null` | 422 | 5, 11 |

Los casos 9a y 9b (listados) no tienen un test propio: los usan todos los tests para verificar lo guardado, con las funciones `buscar_estudiante`, `cantidad_estudiantes`, `buscar_responsable` y `cantidad_responsables`.

### Casos sin test todavía

| Caso | Qué falta |
|---|---|
| 5 | Nombre nulo: 200 con error, no lo crea. Esperado: 422 |
| 12 | Body que no es un objeto: 422 con formato `detail`. Esperado: 422 con el mismo formato que el resto de los errores |

## Detalles técnicos

- **Caso 10:** por defecto, `TestClient` relanza al test la excepción no controlada de la app, en lugar de devolver el 500. Para observar el 500 se crea un cliente con `raise_server_exceptions=False` a partir de `client.app`, solo en ese test, para no ocultar errores inesperados en el resto.
- **Caso 11:** el control de legajo repetido no detecta legajos nulos, porque `WHERE legajo = NULL` nunca da verdadero en SQL y la tabla no tiene `UNIQUE` ni `NOT NULL`. El caso 3 muestra que el control sí funciona con un legajo normal.
- **Casos 4 y 6 separados:** no se agrupan con `parametrize` porque son defectos distintos. Si en la Fase 3 se corrige uno y no el otro, cada test tiene que poder cambiar por separado.
- **Warning de dependencias:** `StarletteDeprecationWarning` sobre `httpx` viene de las versiones de las librerías, no del código del sistema. No afecta los resultados.