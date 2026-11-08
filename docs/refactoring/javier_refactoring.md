# Fase 3 — Refactoring: cambio de estado y asignación de responsable

**Integrante:** Javier Ovelar
**Alcance:** `app/routers/estados.py` (`PUT /solicitudes/{id}/estado` y `PUT /solicitudes/{id}/responsable`) y las transiciones de estado en `app/dominio.py`
**Rama:** `refactor/javier-estados`
**Verificación:** la suite completa (74 tests) pasa después de cada commit, sin cambiar ningún assert de la Fase 2

## Resumen

| # | Refactoring | Técnica | Hallazgos | Principio |
|---|---|---|---|---|
| J1 | Transiciones y estados cerrados a `app/dominio.py` | Move Method | 2, 10 (3 en parte) | OCP, DRY |
| J2 | Columnas por nombre | Replace Magic Number with Named Access | 9 | Nombres claros |
| J3 | Historial y notificación en funciones propias | Extract Method | 8, 11 | SRP, DRY |
| J4 | Nombres de variables | Rename Variable | 12 | Nombres claros |
| J5 | Nombres de los endpoints | Rename Method | 12 | Nombres claros |

Los hallazgos 1, 4, 5, 6 y 7, y lo que queda de 3, 8 y 12, no se resuelven acá: ver [Hallazgos que quedan fuera](#hallazgos-que-quedan-fuera).

## J1 — Move Method: transiciones y estados cerrados (hallazgos 2, 10 y 3 en parte)

**Antes:** las transiciones permitidas se calculaban con tres `if` y una bandera `ok` dentro de `proc_estado`, y la lista de estados cerrados estaba escrita a mano en `asignar`.

```python
ok = False
if act == "PEND" and (nuevo == "ASIG" or nuevo == "CANC"):
    ok = True
if act == "ASIG" and (nuevo == "EN_PROC" or nuevo == "CANC"):
    ok = True
if act == "EN_PROC" and (nuevo == "RES" or nuevo == "RECH"):
    ok = True
if not ok:
    return {"error": "transicion no permitida de " + act + " a " + str(nuevo)}
```

```python
if s[5] in ["RES", "RECH", "CANC"]:
    return {"error": "la solicitud esta cerrada"}
```

**Después:** las transiciones son una tabla en `app/dominio.py`, junto con `AREAS` y `REGLAS_POR_TIPO`. La regla se consulta con una función y los estados cerrados son una constante.

```python
TRANSICIONES = {
    "PEND": ("ASIG", "CANC"),
    "ASIG": ("EN_PROC", "CANC"),
    "EN_PROC": ("RES", "RECH"),
}

ESTADOS_CERRADOS = ("RES", "RECH", "CANC")


def transicion_permitida(actual, nuevo):
    """Indica si una solicitud puede pasar del estado actual al nuevo."""
    return nuevo in TRANSICIONES.get(actual, ())
```

```python
if not transicion_permitida(act, nuevo):
    return {"error": "transicion no permitida de " + act + " a " + str(nuevo)}
```

```python
if s[5] in ESTADOS_CERRADOS:
    return {"error": "la solicitud esta cerrada"}
```

Agregar o cambiar una transición ahora es modificar la tabla, sin tocar el endpoint.

## J2 — Columnas por nombre (hallazgo 9)

**Antes:** las columnas se leían por posición. Para saber qué era `s[5]` o `r[4]` había que mirar el `CREATE TABLE`.

```python
act = s[5]
if nuevo == "ASIG" and s[6] is None:
...
c.execute("SELECT * FROM estudiantes WHERE id = ?", (s[1],))
...
arch.write(f + " - Se envio mail a " + est[4] + ...)
```

```python
if r[4] == 0:
    return {"error": "responsable inactivo"}
if r[2] != s[7]:
    return {"error": "el responsable no pertenece al area " + s[7]}
...
return {"id": id, "responsable_id": r[0], "responsable": r[1], "estado": nuevo_estado}
```

**Después:** el cursor usa `sqlite3.Row`, igual que en `registrar` y en los routers de Cristian, y cada columna se lee por su nombre.

```python
c = conn.cursor()
c.row_factory = sqlite3.Row
...
act = s["estado"]
if nuevo == "ASIG" and s["responsable_id"] is None:
...
c.execute("SELECT * FROM estudiantes WHERE id = ?", (s["estudiante_id"],))
...
arch.write(f + " - Se envio mail a " + est["email"] + ...)
```

```python
if r["activo"] == 0:
    return {"error": "responsable inactivo"}
if r["area"] != s["area"]:
    return {"error": "el responsable no pertenece al area " + s["area"]}
...
return {"id": id, "responsable_id": r["id"], "responsable": r["nombre"], "estado": nuevo_estado}
```

## J3 — Extract Method: historial y notificación (hallazgos 8 y 11)

**Antes:** `proc_estado` actualizaba el estado, escribía el historial, buscaba al estudiante y escribía la notificación en el mismo bloque. El mismo `INSERT INTO historial` estaba repetido en `asignar`.

```python
f = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
c.execute("UPDATE solicitudes SET estado = ?, fecha_mod = ? WHERE id = ?", (nuevo, f, id))
c.execute("INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (?,?,?,?,?)",
          (id, act, nuevo, f, data.get("comentario", "")))
conn.commit()

# notificar al estudiante
c.execute("SELECT * FROM estudiantes WHERE id = ?", (s["estudiante_id"],))
est = c.fetchone()
try:
    with open("notificaciones.log", "a") as arch:
        arch.write(f + " - Se envio mail a " + est["email"] + ": su solicitud " + str(id) + " paso a " + nuevo + "\n")
except:
    pass
```

```python
if nuevo_estado != s["estado"]:
    c.execute("INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (?,?,?,?,?)",
              (id, s["estado"], nuevo_estado, f, "asignada a " + r["nombre"]))
```

**Después:** cada responsabilidad está en una función propia, con el mismo criterio que `registrar_alta_en_historial` y `notificar_alta` de Gastón. Los dos endpoints usan la misma función de historial.

```python
def registrar_en_historial(conn, solicitud_id, estado_ant, estado_nuevo, fecha, comentario):
    """Agrega al historial el paso de la solicitud de un estado a otro."""
    conn.execute("INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (?,?,?,?,?)",
                 (solicitud_id, estado_ant, estado_nuevo, fecha, comentario))


def notificar_cambio_estado(estudiante, solicitud_id, estado, fecha):
    """Deja en notificaciones.log el aviso al estudiante del cambio de estado."""
    try:
        with open("notificaciones.log", "a") as arch:
            arch.write(fecha + " - Se envio mail a " + estudiante["email"] + ": su solicitud " + str(solicitud_id) + " paso a " + estado + "\n")
    except:
        pass
```

```python
f = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
c.execute("UPDATE solicitudes SET estado = ?, fecha_mod = ? WHERE id = ?", (nuevo, f, id))
registrar_en_historial(conn, id, act, nuevo, f, data.get("comentario", ""))
conn.commit()

c.execute("SELECT * FROM estudiantes WHERE id = ?", (s["estudiante_id"],))
est = c.fetchone()
notificar_cambio_estado(est, id, nuevo, f)
```

```python
if nuevo_estado != s["estado"]:
    registrar_en_historial(conn, id, s["estado"], nuevo_estado, f, "asignada a " + r["nombre"])
```

Dos decisiones para que el comportamiento no cambie:

- `registrar_en_historial` no hace `commit`: el `conn.commit()` sigue en cada endpoint, en el mismo lugar que antes.
- `notificar_cambio_estado` recibe el estudiante, no el email. Si el estudiante no existe, `estudiante["email"]` sigue fallando dentro del `try` y el error se ignora como antes. Leer el email afuera habría convertido ese caso en un 500.

## J4 — Rename Variable (hallazgo 12)

**Antes:** variables de una o pocas letras.

```python
s = c.fetchone()
act = s["estado"]
f = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
est = c.fetchone()
r = c.fetchone()
```

**Después:**

```python
solicitud = c.fetchone()
estado_actual = solicitud["estado"]
fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
estudiante = c.fetchone()
responsable = c.fetchone()
```

| Antes | Después |
|---|---|
| `s` | `solicitud` |
| `r` | `responsable` |
| `act` | `estado_actual` |
| `f` | `fecha` |
| `est` | `estudiante` |

`c`, `data` y `nuevo` quedan igual.

## J5 — Rename Method (hallazgo 12)

**Antes:**

```python
def proc_estado(id: int, data: dict = Body(...), conn: sqlite3.Connection = Depends(get_db)):
def asignar(id: int, data: dict = Body(...), conn: sqlite3.Connection = Depends(get_db)):
```

**Después:**

```python
def cambiar_estado(id: int, data: dict = Body(...), conn: sqlite3.Connection = Depends(get_db)):
def asignar_responsable(id: int, data: dict = Body(...), conn: sqlite3.Connection = Depends(get_db)):
```

Mismo criterio que Cristian en `responsables.py` (`crear_responsable`, `listar_responsables`). Las URL no cambian; solo cambia el título de cada endpoint en `/docs`.

## Hallazgos que quedan fuera

| Hallazgo | Por qué no va en esta rama | Dónde va |
|---|---|---|
| 1. Errores con 200 | Pasar a 404/422 cambia lo que responde el sistema: es corrección de defecto | Cambio transversal, con C3 y G4 |
| 3. Lógica de estados repartida (en parte) | `asignar_responsable` sigue pasando PEND → ASIG por su cuenta, sin usar `transicion_permitida` | Mejora futura |
| 4. Validación débil del motivo de rechazo | Rechazar `null` o texto en blanco cambia lo que hoy se acepta | Corrección de defecto |
| 5. Falta de modelo de entrada | Pydantic rechaza lo que hoy se acepta | `app/schemas.py`, con C5 y G5 |
| 6. Historial en reasignaciones | Escribir historial al reasignar cambia el resultado del caso 12c | Corrección de defecto |
| 7. `except:` sin tipo | Capturar solo `OSError` cambia el resultado si el estudiante no existe o no tiene email | Servicio de notificaciones, con Gastón (G7) |
| 8. Duplicated Code (en parte) | El historial y la notificación de `registrar` siguen en `solicitudes.py` | Servicio de notificaciones, con Gastón |
| 10. Estados como strings (en parte) | Los estados siguen siendo strings sueltos en los endpoints, y `consultas.py` tiene su propia tupla de estados cerrados | Avisar a Bruno: puede usar `ESTADOS_CERRADOS` |
| 12. Parámetro `id` (en parte) | Cambiarlo obliga a cambiar la ruta `{id}`, y `consultas.py` usa el mismo criterio | Mejora futura, junto con `consultas.py` |

## Cómo se verificó

- Suite completa después de cada commit: 74 passed. Ningún assert de la Fase 2 cambió.
- Evidencia: `docs/evidencias/fase3/javier/javier_fase3_suite_completa.png`.
