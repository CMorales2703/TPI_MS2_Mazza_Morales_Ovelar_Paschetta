# Fase 3 — Refactoring: alta de solicitudes

**Integrante:** Gaston Paschetta
**Alcance:** `app/routers/solicitudes.py` (`POST /solicitudes`) y las reglas por tipo en `app/dominio.py`
**Rama:** `refactor/gaston-solicitudes`
**Verificación:** la suite completa pasa después de cada commit (67 tests al empezar, 74 con los 7 nuevos), sin cambiar ningún assert de la Fase 2

## Resumen

| # | Refactoring | Técnica | Hallazgos | Principio |
|---|---|---|---|---|
| G1 | Datos del alta en un objeto | Introduce Parameter Object | 1 | Clean Code: pocos argumentos |
| T | Tests de la regla de cada tipo (antes de G2) | — | 2, 6 | — |
| G2 | Una sola regla de prioridad | Substitute Algorithm (usar la función existente) | 2 | DRY |
| G3 | Reglas por tipo en una tabla | Replace Conditional with Lookup Table | 6 | OCP |
| G4 | Historial y notificación fuera de `registrar` | Extract Method | 3 | SRP |
| G5 | Email por nombre de columna | Replace Magic Number with Named Access | 8 | Nombres claros |
| G6 | Nombres y código comentado | Rename Variable + Remove Dead Code | 9 | Nombres claros |

Los hallazgos 4, 5 y 7 no se resuelven acá: ver [Hallazgos que quedan fuera](#hallazgos-que-quedan-fuera).

## G1 — Introduce Parameter Object (hallazgo 1)

**Antes:** `guardar_solicitud` recibía once argumentos posicionales, en el mismo orden que el `INSERT`. Invertir dos del mismo tipo (`canal` y `obs`, o las dos fechas) no daba ningún error.

```python
def guardar_solicitud(conn, estudiante_id, tipo, descripcion, prioridad, estado, responsable_id, area, fecha_alta, fecha_mod, canal, obs):
    c = conn.cursor()
    c.execute("""INSERT INTO solicitudes (estudiante_id, tipo, descripcion, prioridad, estado, responsable_id, area,
                 fecha_alta, fecha_mod, canal, obs) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
              (estudiante_id, tipo, descripcion, prioridad, estado, responsable_id, area, fecha_alta, fecha_mod, canal, obs))
```

```python
id = guardar_solicitud(conn, data["estudiante_id"], data["tipo"], data["descripcion"], p, "PEND", None, a, f, f,
                       canal, data.get("obs", ""))
...
return {"id": id, "estudiante_id": data["estudiante_id"], "tipo": data["tipo"], "descripcion": data["descripcion"],
        "prioridad": p, "estado": "PEND", "responsable_id": None, "area": a, "fecha_alta": f, "fecha_mod": f,
        "canal": canal, "obs": data.get("obs", "")}
```

**Después:** la fila completa es un `dataclass`, se arma con argumentos por nombre y el `INSERT` usa parámetros con nombre. La respuesta sale del mismo objeto.

```python
@dataclass
class NuevaSolicitud:
    """Datos de una solicitud nueva, tal como se guardan en la tabla solicitudes."""

    estudiante_id: int
    tipo: str
    descripcion: str
    prioridad: int
    estado: str
    responsable_id: int | None
    area: str
    fecha_alta: str
    fecha_mod: str
    canal: str
    obs: str


def guardar_solicitud(conn, solicitud):
    c = conn.cursor()
    c.execute("""INSERT INTO solicitudes (estudiante_id, tipo, descripcion, prioridad, estado, responsable_id, area,
                 fecha_alta, fecha_mod, canal, obs)
                 VALUES (:estudiante_id, :tipo, :descripcion, :prioridad, :estado, :responsable_id, :area,
                         :fecha_alta, :fecha_mod, :canal, :obs)""",
              asdict(solicitud))
```

```python
solicitud = NuevaSolicitud(estudiante_id=data["estudiante_id"], tipo=data["tipo"], descripcion=data["descripcion"],
                           prioridad=p, estado="PEND", responsable_id=None, area=a,
                           fecha_alta=f, fecha_mod=f, canal=canal, obs=data.get("obs", ""))
id = guardar_solicitud(conn, solicitud)
...
return {"id": id, **asdict(solicitud)}
```

## T — Tests de la regla de cada tipo (hallazgos 2 y 6)

Antes de tocar la regla de prioridad comprobé qué la protegía, con la técnica de Bruno: cambiar la regla a mano y correr la suite. Cambiar la prioridad de CERT sin "urgente", de EQUIV, de RECLAMO o de BAJA, o el área de RECLAMO, dejaba los 67 tests en verde. Solo MESA y CERT con "urgente" estaban cubiertos.

**Antes:** ningún test fijaba la prioridad por defecto ni el área de cada tipo.

**Después:** 7 tests nuevos en `tests/test_solicitudes.py`, con el mismo criterio de línea de base de la Fase 2.

```python
@pytest.mark.parametrize("tipo, prioridad, area", [
    ("CERT", 3, "Alumnado"),
    ("EQUIV", 2, "Departamento Academico"),
    ("MESA", 1, "Bedelia"),
    ("RECLAMO", 1, "Coordinacion"),
    ("BAJA", 2, "Alumnado"),
])
def test_registrar_asigna_prioridad_y_area_segun_tipo(client, tipo, prioridad, area):
```

```python
def test_registrar_urgente_no_distingue_mayusculas(client):
def test_registrar_urgente_no_pisa_prioridad_enviada(client):
```

Los 7 pasan sobre el código sin refactorizar (commit aparte, antes de G2), y ahora cada uno de esos cambios hace fallar un test.

## G2 — Substitute Algorithm, una sola regla de prioridad (hallazgo 2)

**Antes:** la regla estaba dos veces. `calcular_prioridad` existía pero no se usaba (tenía un `TODO`), y `registrar` repetía los `if` con la regla de "urgente" aparte.

```python
def calcular_prioridad(tipo):
    # TODO: usar esto en registrar
    if tipo == "MESA" or tipo == "RECLAMO":
        return 1
    if tipo == "CERT":
        return 3
    return 2
```

```python
p = data.get("prioridad")
if p is None:
    if data["tipo"] == "MESA":
        p = 1
    elif data["tipo"] == "RECLAMO":
        p = 1
    elif data["tipo"] == "EQUIV":
        p = 2
    elif data["tipo"] == "CERT":
        p = 3
    else:
        p = 2
    if "urgente" in data["descripcion"].lower():
        p = 1
else:
    if p not in [1, 2, 3]:
        return {"error": "prioridad invalida"}
```

**Después:** "urgente" es parte de la prioridad por defecto y vive en la función. Si el cliente manda la prioridad, la decide `registrar`.

```python
def calcular_prioridad(tipo, descripcion):
    """Prioridad por defecto: 1 si la descripción dice "urgente"; si no, la del tipo."""
    if "urgente" in descripcion.lower():
        return 1
    if tipo == "MESA" or tipo == "RECLAMO":
        return 1
    if tipo == "CERT":
        return 3
    return 2
```

```python
p = data.get("prioridad")
if p is None:
    p = calcular_prioridad(data["tipo"], data["descripcion"])
elif p not in [1, 2, 3]:
    return {"error": "prioridad invalida"}
```

## G3 — Replace Conditional with Lookup Table (hallazgo 6)

**Antes:** cada tipo aparecía en tres lugares: la lista de validación, los `if` de la prioridad y los `if` del área.

```python
if "tipo" not in data or data["tipo"] not in ["CERT", "EQUIV", "MESA", "RECLAMO", "BAJA"]:
    return {"error": "tipo invalido"}
...
# area segun tipo
if data["tipo"] == "CERT" or data["tipo"] == "BAJA":
    a = "Alumnado"
elif data["tipo"] == "EQUIV":
    a = "Departamento Academico"
elif data["tipo"] == "MESA":
    a = "Bedelia"
else:
    a = "Coordinacion"
```

**Después:** `app/dominio.py`, junto a `AREAS`.

```python
# Regla de cada tipo de solicitud: área que la atiende y prioridad por defecto
REGLAS_POR_TIPO = {
    "CERT": {"area": "Alumnado", "prioridad": 3},
    "EQUIV": {"area": "Departamento Academico", "prioridad": 2},
    "MESA": {"area": "Bedelia", "prioridad": 1},
    "RECLAMO": {"area": "Coordinacion", "prioridad": 1},
    "BAJA": {"area": "Alumnado", "prioridad": 2},
}

TIPOS = tuple(REGLAS_POR_TIPO)
```

```python
def calcular_prioridad(tipo, descripcion):
    """Prioridad por defecto: 1 si la descripción dice "urgente"; si no, la del tipo."""
    if "urgente" in descripcion.lower():
        return 1
    return REGLAS_POR_TIPO[tipo]["prioridad"]


def determinar_area(tipo):
    """Área que atiende las solicitudes del tipo."""
    return REGLAS_POR_TIPO[tipo]["area"]
```

```python
if "tipo" not in data or data["tipo"] not in TIPOS:
    return {"error": "tipo invalido"}
...
a = determinar_area(data["tipo"])
```

Agregar un tipo se hace en una sola fila. `TIPOS` es una tupla a propósito: con un tipo no hasheable (por ejemplo `["MESA"]`) sigue respondiendo "tipo invalido".

## G4 — Extract Method, historial y notificación (hallazgo 3)

**Antes:** `registrar` validaba, calculaba, guardaba, escribía el historial y notificaba.

```python
c.execute("INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (?,?,?,?,?)",
          (id, None, "PEND", f, "alta de solicitud"))
conn.commit()
...
# notificar al estudiante
try:
    with open("notificaciones.log", "a") as arch:
        arch.write(f + " - Se envio mail a " + est[4] + ": su solicitud " + str(id) + " fue registrada\n")
except:
    pass
```

**Después:** cada paso es una función con nombre, con el mismo código (incluido el `except: pass`, ver hallazgo 7).

```python
def registrar_alta_en_historial(conn, solicitud_id, fecha):
    """Agrega al historial la fila del alta (sin estado anterior, pasa a PEND)."""
    conn.execute("INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (?,?,?,?,?)",
                 (solicitud_id, None, "PEND", fecha, "alta de solicitud"))
    conn.commit()


def notificar_alta(email, solicitud_id, fecha):
    """Deja en notificaciones.log el aviso de alta al estudiante."""
    try:
        with open("notificaciones.log", "a") as arch:
            arch.write(fecha + " - Se envio mail a " + email + ": su solicitud " + str(solicitud_id) + " fue registrada\n")
    except:
        pass
```

```python
id = guardar_solicitud(conn, solicitud)
registrar_alta_en_historial(conn, id, f)
...
notificar_alta(est[4], id, f)
```

## G5 — Email por nombre de columna (hallazgo 8)

**Antes:** el email se leía por posición. Un cambio en el orden de la tabla `estudiantes` mandaba el aviso a otro dato sin ningún error.

```python
notificar_alta(est[4], id, f)
```

**Después:**

```python
c = conn.cursor()
c.row_factory = sqlite3.Row
...
notificar_alta(est["email"], id, f)
```

Como en R2 de Cristian, `row_factory` se aplica solo al cursor de `registrar`, sin tocar `get_db`.

## G6 — Rename Variable + Remove Dead Code (hallazgo 9)

**Antes:** nombres de una letra, `id` tapando la función de Python, `est` abreviado y un `UPDATE` comentado.

```python
p = data.get("prioridad")
...
f = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
...
id = guardar_solicitud(conn, solicitud)
registrar_alta_en_historial(conn, id, f)
# c.execute("UPDATE estudiantes SET carrera = 'TUP' WHERE id = ?", (data["estudiante_id"],))
# conn.commit()

notificar_alta(est["email"], id, f)

return {"id": id, **asdict(solicitud)}
```

**Después:**

```python
prioridad = data.get("prioridad")
if prioridad is None:
    prioridad = calcular_prioridad(data["tipo"], data["descripcion"])
elif prioridad not in [1, 2, 3]:
    return {"error": "prioridad invalida"}
...
fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
solicitud = NuevaSolicitud(estudiante_id=data["estudiante_id"], tipo=data["tipo"], descripcion=data["descripcion"],
                           prioridad=prioridad, estado="PEND", responsable_id=None,
                           area=determinar_area(data["tipo"]), fecha_alta=fecha, fecha_mod=fecha,
                           canal=canal, obs=data.get("obs", ""))
solicitud_id = guardar_solicitud(conn, solicitud)
registrar_alta_en_historial(conn, solicitud_id, fecha)
notificar_alta(estudiante["email"], solicitud_id, fecha)

return {"id": solicitud_id, **asdict(solicitud)}
```

El área pasa directo al objeto y `guardar_solicitud` suma su docstring.

## Decisiones de diseño

| Pregunta | Decisión | Por qué | Alternativa descartada |
|---|---|---|---|
| ¿Qué agrupa el objeto? | La fila completa de `solicitudes` | Es lo que recibe el `INSERT`; el body es otro modelo | Agrupar el body: es el modelo de entrada del hallazgo 5 |
| ¿Dataclass o Pydantic? | `dataclass` | No convierte valores: la respuesta queda igual | Pydantic convierte `true` en `1` y cambiaría el caso 14 |
| ¿Cómo se evita invertir campos? | Argumentos por nombre y parámetros con nombre en el `INSERT` | No se pueden invertir `canal`/`obs` ni las fechas | Mantener `?` posicionales con el objeto |
| ¿De dónde sale la respuesta? | Del objeto, con `asdict` | No se desincroniza de lo guardado y conserva el `true` del caso 14 | Releer la base: devolvería `1` en el caso 14 |
| ¿Dónde queda el `commit`? | Sigue dentro de `guardar_solicitud` | Unir alta e historial en una transacción cambia qué pasa si falla el historial | Una sola transacción: queda como mejora futura |
| ¿Dónde vive cada cosa? | `NuevaSolicitud` en el router, `REGLAS_POR_TIPO` en `app/dominio.py` | La clase solo la usa el alta; `dominio.py` ya tenía `AREAS` | Un módulo nuevo para la clase |
| ¿"Urgente" es parte de la prioridad? | Sí, de la prioridad por defecto: `calcular_prioridad(tipo, descripcion)` | La prioridad enviada por el cliente la decide `registrar` | Aplicar "urgente" en `registrar` después de la función |
| ¿`TIPOS` lista, set o tupla? | Tupla | `in` sobre un dict o set falla con un tipo no hasheable como `["MESA"]` y daría 500; con la tupla sigue "tipo invalido" | Validar con `data["tipo"] not in REGLAS_POR_TIPO` |
| ¿Se extrae la validación? | No | La reemplaza el modelo Pydantic del hallazgo 5 | Extraer `validar_solicitud` ahora |

## Hallazgos que quedan fuera

| Hallazgo | Por qué no va en esta rama | Dónde va |
|---|---|---|
| 4. Errores con 200 | Pasar de 200 a 422/201 es corrección de defecto | Cambio transversal, con C3 y J1 |
| 5. Falta de modelo de entrada | Pydantic rechaza lo que hoy se acepta o da 500 | `app/schemas.py`, con C5 y J5 |
| 7. `except: pass` | Capturar solo `OSError` cambia el resultado si el email es `None`, y el caso 17 es un defecto | Servicio de notificaciones, con Javier (J7, J8) |

## Cómo se verificó

- Suite completa después de cada commit: 74 passed. Ningún assert de la Fase 2 cambió.
- Comparación contra `dev` con 51 requests a `POST /solicitudes` (los cinco tipos, tipos inválidos o no texto, descripciones nulas, numéricas, lista o en blanco, prioridades `0`, `"1"`, `true`, `false` y `2.0`, canales inválidos, `obs` nulo o numérico, estudiantes inexistentes): mismo código, misma respuesta salvo las fechas, misma fila, mismo historial y mismo log.
- Evidencia: `docs/evidencias/fase3/gaston/gaston_fase3_suite_completa.png`.
