from datetime import datetime

from fastapi import Body, FastAPI, HTTPException

from app.db import RUTA_DB_POR_DEFECTO, conectar, crear_tablas
from app.seed import base_vacia, cargar_datos_de_prueba

app = FastAPI(title="Sistema de Gestion de Solicitudes Academicas")

conn = conectar(RUTA_DB_POR_DEFECTO)
c = conn.cursor()

crear_tablas(conn)
if base_vacia(conn):
    cargar_datos_de_prueba(conn)


# ---------------- ESTUDIANTES ----------------


@app.post("/estudiantes")
def crear_estudiante(data: dict = Body(...)):
    if "nombre" not in data or data["nombre"] == "" or data["nombre"] is None:
        return {"error": "falta nombre"}
    if "apellido" not in data or data["apellido"] == "":
        return {"error": "falta apellido"}
    if "legajo" not in data or data["legajo"] == "":
        return {"error": "falta legajo"}
    if "email" in data and "@" not in data["email"]:
        return {"error": "email invalido"}
    c.execute("SELECT * FROM estudiantes WHERE legajo = ?", (data["legajo"],))
    if c.fetchone():
        return {"error": "legajo repetido"}
    c.execute(
        "INSERT INTO estudiantes (nombre, apellido, legajo, email, carrera) VALUES (?,?,?,?,?)",
        (
            data["nombre"],
            data["apellido"],
            data["legajo"],
            data.get("email", ""),
            data.get("carrera", "TUP"),
        ),
    )
    conn.commit()
    return {
        "id": c.lastrowid,
        "nombre": data["nombre"],
        "apellido": data["apellido"],
        "legajo": data["legajo"],
        "email": data.get("email", ""),
        "carrera": data.get("carrera", "TUP"),
    }


@app.get("/estudiantes")
def listar_estudiantes():
    c.execute("SELECT * FROM estudiantes")
    rows = c.fetchall()
    res = []
    for r in rows:
        res.append(
            {
                "id": r[0],
                "nombre": r[1],
                "apellido": r[2],
                "legajo": r[3],
                "email": r[4],
                "carrera": r[5],
            }
        )
    return res


# ---------------- RESPONSABLES ----------------


@app.post("/responsables")
def nuevoResponsable(data: dict = Body(...)):
    if "nombre" not in data or data["nombre"] == "":
        return {"error": "falta nombre"}
    if "area" not in data or data["area"] not in [
        "Alumnado",
        "Departamento Academico",
        "Bedelia",
        "Coordinacion",
    ]:
        return {"error": "area invalida"}
    if "email" in data and "@" not in data["email"]:
        return {"error": "email invalido"}
    c.execute(
        "INSERT INTO responsables (nombre, area, email, activo) VALUES (?,?,?,?)",
        (data["nombre"], data["area"], data.get("email", ""), 1),
    )
    conn.commit()
    return {
        "id": c.lastrowid,
        "nombre": data["nombre"],
        "area": data["area"],
        "email": data.get("email", ""),
        "activo": True,
    }


@app.get("/responsables")
def get_resp():
    c.execute("SELECT * FROM responsables")
    res = []
    for r in c.fetchall():
        res.append(
            {
                "id": r[0],
                "nombre": r[1],
                "area": r[2],
                "email": r[3],
                "activo": r[4] == 1,
            }
        )
    return res


# ---------------- SOLICITUDES ----------------


def guardar_solicitud(
    estudiante_id,
    tipo,
    descripcion,
    prioridad,
    estado,
    responsable_id,
    area,
    fecha_alta,
    fecha_mod,
    canal,
    obs,
):
    c.execute(
        """INSERT INTO solicitudes (estudiante_id, tipo, descripcion, prioridad, estado, responsable_id, area,
                 fecha_alta, fecha_mod, canal, obs) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (
            estudiante_id,
            tipo,
            descripcion,
            prioridad,
            estado,
            responsable_id,
            area,
            fecha_alta,
            fecha_mod,
            canal,
            obs,
        ),
    )
    conn.commit()
    return c.lastrowid


def calcular_prioridad(tipo):
    # TODO: usar esto en registrar
    if tipo == "MESA" or tipo == "RECLAMO":
        return 1
    if tipo == "CERT":
        return 3
    return 2


@app.post("/solicitudes")
def registrar(data: dict = Body(...)):
    # validaciones
    if "estudiante_id" not in data:
        return {"error": "falta estudiante"}
    c.execute("SELECT * FROM estudiantes WHERE id = ?", (data["estudiante_id"],))
    est = c.fetchone()
    if est is None:
        return {"error": "estudiante no existe"}
    if "tipo" not in data or data["tipo"] not in [
        "CERT",
        "EQUIV",
        "MESA",
        "RECLAMO",
        "BAJA",
    ]:
        return {"error": "tipo invalido"}
    if "descripcion" not in data or len(data["descripcion"]) < 10:
        return {"error": "descripcion muy corta"}

    # prioridad
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

    # area segun tipo
    if data["tipo"] == "CERT" or data["tipo"] == "BAJA":
        a = "Alumnado"
    elif data["tipo"] == "EQUIV":
        a = "Departamento Academico"
    elif data["tipo"] == "MESA":
        a = "Bedelia"
    else:
        a = "Coordinacion"

    canal = data.get("canal", "WEB")
    if canal not in ["WEB", "MAIL", "PRESENCIAL"]:
        canal = "WEB"

    f = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id = guardar_solicitud(
        data["estudiante_id"],
        data["tipo"],
        data["descripcion"],
        p,
        "PEND",
        None,
        a,
        f,
        f,
        canal,
        data.get("obs", ""),
    )
    c.execute(
        "INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (?,?,?,?,?)",
        (id, None, "PEND", f, "alta de solicitud"),
    )
    conn.commit()
    # c.execute("UPDATE estudiantes SET carrera = 'TUP' WHERE id = ?", (data["estudiante_id"],))
    # conn.commit()

    # notificar al estudiante
    try:
        with open("notificaciones.log", "a") as arch:
            arch.write(
                f
                + " - Se envio mail a "
                + est[4]
                + ": su solicitud "
                + str(id)
                + " fue registrada\n"
            )
    except:
        pass

    return {
        "id": id,
        "estudiante_id": data["estudiante_id"],
        "tipo": data["tipo"],
        "descripcion": data["descripcion"],
        "prioridad": p,
        "estado": "PEND",
        "responsable_id": None,
        "area": a,
        "fecha_alta": f,
        "fecha_mod": f,
        "canal": canal,
        "obs": data.get("obs", ""),
    }


@app.get("/solicitudes")
def buscar(
    estado: str = None,
    tipo: str = None,
    prioridad: int = None,
    area: str = None,
    estudiante_id: int = None,
    texto: str = None,
    desde: str = None,
    hasta: str = None,
    orden: str = "fecha",
):
    q = "SELECT * FROM solicitudes WHERE 1=1"
    if estado:
        q += " AND estado = '" + estado + "'"
    if tipo:
        q += " AND tipo = '" + tipo + "'"
    if prioridad:
        q += " AND prioridad = " + str(prioridad)
    if area:
        q += " AND area = '" + area + "'"
    if estudiante_id:
        q += " AND estudiante_id = " + str(estudiante_id)
    if texto:
        q += " AND descripcion LIKE '%" + texto + "%'"
    if desde:
        q += " AND fecha_alta >= '" + desde + "'"
    if hasta:
        q += " AND fecha_alta <= '" + hasta + " 23:59:59'"
    if orden == "prioridad":
        q += " ORDER BY prioridad ASC, fecha_alta ASC, id ASC"
    else:
        q += " ORDER BY fecha_alta DESC, id DESC"
    c.execute(q)
    rows = c.fetchall()
    res = []
    for r in rows:
        res.append(
            {
                "id": r[0],
                "estudiante_id": r[1],
                "tipo": r[2],
                "descripcion": r[3],
                "prioridad": r[4],
                "estado": r[5],
                "responsable_id": r[6],
                "area": r[7],
                "fecha_alta": r[8],
                "fecha_mod": r[9],
                "canal": r[10],
                "obs": r[11],
            }
        )
    return res


@app.get("/solicitudes/{id}")
def getSolicitud(id: int):
    c.execute("SELECT * FROM solicitudes WHERE id = ?", (id,))
    r = c.fetchone()
    if r is None:
        raise HTTPException(status_code=404, detail="no existe")
    d = {
        "id": r[0],
        "estudiante_id": r[1],
        "tipo": r[2],
        "descripcion": r[3],
        "prioridad": r[4],
        "estado": r[5],
        "responsable_id": r[6],
        "area": r[7],
        "fecha_alta": r[8],
        "fecha_mod": r[9],
        "canal": r[10],
        "obs": r[11],
    }
    c.execute("SELECT * FROM historial WHERE solicitud_id = ? ORDER BY id", (id,))
    h = []
    for x in c.fetchall():
        h.append(
            {
                "estado_anterior": x[2],
                "estado_nuevo": x[3],
                "fecha": x[4],
                "comentario": x[5],
            }
        )
    d["historial"] = h
    return d


@app.put("/solicitudes/{id}/estado")
def proc_estado(id: int, data: dict = Body(...)):
    c.execute("SELECT * FROM solicitudes WHERE id = ?", (id,))
    s = c.fetchone()
    if s is None:
        raise HTTPException(status_code=404, detail="no existe")
    nuevo = data.get("estado")
    act = s[5]
    ok = False
    if act == "PEND" and (nuevo == "ASIG" or nuevo == "CANC"):
        ok = True
    if act == "ASIG" and (nuevo == "EN_PROC" or nuevo == "CANC"):
        ok = True
    if act == "EN_PROC" and (nuevo == "RES" or nuevo == "RECH"):
        ok = True
    if not ok:
        return {"error": "transicion no permitida de " + act + " a " + str(nuevo)}
    if nuevo == "ASIG" and s[6] is None:
        return {"error": "no tiene responsable"}
    if nuevo == "RECH" and ("comentario" not in data or data["comentario"] == ""):
        return {"error": "para rechazar hay que poner motivo"}

    f = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        "UPDATE solicitudes SET estado = ?, fecha_mod = ? WHERE id = ?", (nuevo, f, id)
    )
    c.execute(
        "INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (?,?,?,?,?)",
        (id, act, nuevo, f, data.get("comentario", "")),
    )
    conn.commit()

    # notificar al estudiante
    c.execute("SELECT * FROM estudiantes WHERE id = ?", (s[1],))
    est = c.fetchone()
    try:
        with open("notificaciones.log", "a") as arch:
            arch.write(
                f
                + " - Se envio mail a "
                + est[4]
                + ": su solicitud "
                + str(id)
                + " paso a "
                + nuevo
                + "\n"
            )
    except:
        pass

    return {"id": id, "estado": nuevo, "estado_anterior": act}


@app.put("/solicitudes/{id}/responsable")
def asignar(id: int, data: dict = Body(...)):
    c.execute("SELECT * FROM solicitudes WHERE id = ?", (id,))
    s = c.fetchone()
    if s is None:
        return {"error": "solicitud no existe"}
    if s[5] in ["RES", "RECH", "CANC"]:
        return {"error": "la solicitud esta cerrada"}
    c.execute("SELECT * FROM responsables WHERE id = ?", (data.get("responsable_id"),))
    r = c.fetchone()
    if r is None:
        return {"error": "responsable no existe"}
    if r[4] == 0:
        return {"error": "responsable inactivo"}
    if r[2] != s[7]:
        return {"error": "el responsable no pertenece al area " + s[7]}

    f = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nuevo_estado = s[5]
    if s[5] == "PEND":
        nuevo_estado = "ASIG"
    c.execute(
        "UPDATE solicitudes SET responsable_id = ?, estado = ?, fecha_mod = ? WHERE id = ?",
        (r[0], nuevo_estado, f, id),
    )
    if nuevo_estado != s[5]:
        c.execute(
            "INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (?,?,?,?,?)",
            (id, s[5], nuevo_estado, f, "asignada a " + r[1]),
        )
    conn.commit()
    return {
        "id": id,
        "responsable_id": r[0],
        "responsable": r[1],
        "estado": nuevo_estado,
    }


# ---------------- REPORTE ----------------


@app.get("/reporte")
def reporte():
    c.execute("SELECT * FROM solicitudes")
    todas = c.fetchall()
    total = len(todas)
    por_estado = {}
    por_tipo = {}
    por_area = {}
    vencidas = []
    hoy = datetime.now()
    for s in todas:
        if s[5] in por_estado:
            por_estado[s[5]] = por_estado[s[5]] + 1
        else:
            por_estado[s[5]] = 1
        if s[2] in por_tipo:
            por_tipo[s[2]] = por_tipo[s[2]] + 1
        else:
            por_tipo[s[2]] = 1
        if s[7] in por_area:
            por_area[s[7]] = por_area[s[7]] + 1
        else:
            por_area[s[7]] = 1
        if s[5] not in ["RES", "RECH", "CANC"]:
            fa = datetime.strptime(s[8], "%Y-%m-%d %H:%M:%S")
            if s[4] == 1:
                dias = 2
            elif s[4] == 2:
                dias = 5
            else:
                dias = 10
            if (hoy - fa).days > dias:
                vencidas.append(
                    {
                        "id": s[0],
                        "tipo": s[2],
                        "prioridad": s[4],
                        "dias": (hoy - fa).days,
                    }
                )
    resueltas = por_estado.get("RES", 0)
    porc = 0
    if total > 0:
        porc = round(resueltas * 100 / total, 2)
    return {
        "total": total,
        "por_estado": por_estado,
        "por_tipo": por_tipo,
        "por_area": por_area,
        "porcentaje_resueltas": porc,
        "vencidas": vencidas,
    }
