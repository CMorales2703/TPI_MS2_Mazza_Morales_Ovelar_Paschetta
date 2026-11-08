# Fase 3 — Refactoring: estudiantes, responsables y cambios transversales

**Integrante:** Cristian Morales
**Alcance:** conexión y arranque (transversal), `app/routers/estudiantes.py`, `app/routers/responsables.py`
**Ramas:** `refactor/conexion` (PR #13) y `refactor/personas`
**Verificación:** los 64 tests de la Fase 2 pasan después de cada commit, sin cambiar ningún assert

## Resumen

| # | Refactoring | Técnica | Hallazgos | Principio | Rama |
|---|---|---|---|---|---|
| T1 | Tablas y datos de prueba a módulos propios | Extract Method + Move | 2, 10 | SRP | `refactor/conexion` |
| T2 | Conexión por request en lugar de global | Dependency Injection | 1, 2 | DIP | `refactor/conexion` |
| T3 | Un router por área | Move | — | SRP | `refactor/conexion` |
| R1 | Nombres de los endpoints de responsables | Rename Method | 12 | Nombres claros | `refactor/personas` |
| R2 | Conversión de filas con columnas por nombre | Extract Method | 8, 9 | Nombres claros | `refactor/personas` |
| R3 | Validación de email en un solo lugar | Extract Function | 4 | DRY | `refactor/personas` |
| R4 | Áreas y carrera por defecto como constantes | Replace Magic Literal with Constant | 6, 13 | OCP | `refactor/personas` |
| R5 | `crear_estudiante` dividido | Extract Method | 7 | SRP | `refactor/personas` |

Los cambios transversales (T1 a T3) están explicados en `docs/decisiones/01_estructura_y_conexion.md`.

## R1 — Rename Method (hallazgo 12)

**Antes:** cada endpoint seguía una convención distinta.

```python
def crear_estudiante(...)     # snake_case, verbo "crear"
def listar_estudiantes(...)
def nuevoResponsable(...)     # camelCase, sin verbo
def get_resp(...)             # inglés, abreviado
```

**Después:**

```python
def crear_responsable(...)
def listar_responsables(...)
```

Las rutas y las respuestas no cambian. En `/docs` cambia el nombre interno de la operación.

## R2 — Extract Method, columnas por nombre (hallazgos 8 y 9)

**Antes:** el listado accedía a las columnas por posición. Un cambio en el orden de la tabla rompía la respuesta sin ningún error.

```python
for r in rows:
    res.append({"id": r[0], "nombre": r[1], "apellido": r[2], "legajo": r[3], "email": r[4], "carrera": r[5]})
```

**Después:** el cursor usa `sqlite3.Row` y la conversión está en una función.

```python
def fila_a_estudiante(fila):
    return {"id": fila["id"], "nombre": fila["nombre"], "apellido": fila["apellido"],
            "legajo": fila["legajo"], "email": fila["email"], "carrera": fila["carrera"]}

c.row_factory = sqlite3.Row
return [fila_a_estudiante(fila) for fila in c.fetchall()]
```

Lo mismo con `fila_a_responsable`. `row_factory` se aplica solo al cursor de estos endpoints, para no afectar las partes de los demás.

## R3 — Extract Function, validación de email (hallazgo 4)

**Antes:** la misma condición en los dos endpoints.

```python
if "email" in data and "@" not in data["email"]:
    return {"error": "email invalido"}
```

**Después:** `app/validaciones.py`.

```python
def email_invalido(data):
    return "email" in data and "@" not in data["email"]
```

La condición se mantiene exactamente igual, incluido el `TypeError` con `email: null` (caso 10). Corregirlo cambia la respuesta de 500 a 422: es corrección de defecto, no refactoring.

## R4 — Replace Magic Literal with Constant (hallazgos 6 y 13)

**Antes:** la lista de áreas escrita en el endpoint, y repetida en `registrar` con otra forma.

```python
if "area" not in data or data["area"] not in ["Alumnado", "Departamento Academico", "Bedelia", "Coordinacion"]:
```

**Después:** `app/dominio.py`.

```python
AREAS = ("Alumnado", "Departamento Academico", "Bedelia", "Coordinacion")
CARRERA_POR_DEFECTO = "TUP"
```

```python
if "area" not in data or data["area"] not in AREAS:
```

Agregar un área se hace en un solo lugar. `registrar` (Gaston) puede usar la misma constante en su refactor.

## R5 — Extract Method en `crear_estudiante` (hallazgo 7)

**Antes:** una función con cuatro responsabilidades: validar, buscar duplicados, insertar y armar la respuesta.

**Después:** la función coordina y delega.

```python
@router.post("/estudiantes")
def crear_estudiante(data: dict = Body(...), conn: sqlite3.Connection = Depends(get_db)):
    error = validar_estudiante(data)
    if error:
        return {"error": error}
    if legajo_existe(conn, data["legajo"]):
        return {"error": "legajo repetido"}
    return insertar_estudiante(conn, data)
```

Las validaciones, su orden, los mensajes y la respuesta son los mismos.

## Hallazgos que no se resuelven con refactoring

Cambian lo que ve el cliente, así que son **corrección de defecto**: van en commits aparte, con el criterio de códigos HTTP unificado por el grupo y actualizando las expectativas de los tests.

| Hallazgo | Por qué no es refactoring |
|---|---|
| 3. Manejo de errores inconsistente | pasar de 200 con `error` a 422/409 cambia las respuestas |
| 5. Falta de modelo de entrada | un modelo Pydantic rechaza con 422 lo que hoy se acepta o devuelve 200 |
| 11. Integridad de datos | `NOT NULL` / `UNIQUE` hacen que se rechacen altas que hoy se aceptan |