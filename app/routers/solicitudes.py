"""Solicitudes: registro de una solicitud nueva."""

import sqlite3
from datetime import datetime

from fastapi import APIRouter, Body, Depends

from app.db import get_db

router = APIRouter()


def guardar_solicitud(conn, estudiante_id, tipo, descripcion, prioridad, estado, responsable_id, area, fecha_alta, fecha_mod, canal, obs):
    c = conn.cursor()
    c.execute("""INSERT INTO solicitudes (estudiante_id, tipo, descripcion, prioridad, estado, responsable_id, area,
                 fecha_alta, fecha_mod, canal, obs) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
              (estudiante_id, tipo, descripcion, prioridad, estado, responsable_id, area, fecha_alta, fecha_mod, canal, obs))
    conn.commit()
    return c.lastrowid


def calcular_prioridad(tipo):
    # TODO: usar esto en registrar
    if tipo == "MESA" or tipo == "RECLAMO":
        return 1
    if tipo == "CERT":
        return 3
    return 2


@router.post("/solicitudes")
def registrar(data: dict = Body(...), conn: sqlite3.Connection = Depends(get_db)):
    c = conn.cursor()
    # validaciones
    if "estudiante_id" not in data:
        return {"error": "falta estudiante"}
    c.execute("SELECT * FROM estudiantes WHERE id = ?", (data["estudiante_id"],))
    est = c.fetchone()
    if est is None:
        return {"error": "estudiante no existe"}
    if "tipo" not in data or data["tipo"] not in ["CERT", "EQUIV", "MESA", "RECLAMO", "BAJA"]:
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
    id = guardar_solicitud(conn, data["estudiante_id"], data["tipo"], data["descripcion"], p, "PEND", None, a, f, f,
                           canal, data.get("obs", ""))
    c.execute("INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (?,?,?,?,?)",
              (id, None, "PEND", f, "alta de solicitud"))
    conn.commit()
    # c.execute("UPDATE estudiantes SET carrera = 'TUP' WHERE id = ?", (data["estudiante_id"],))
    # conn.commit()

    # notificar al estudiante
    try:
        with open("notificaciones.log", "a") as arch:
            arch.write(f + " - Se envio mail a " + est[4] + ": su solicitud " + str(id) + " fue registrada\n")
    except:
        pass

    return {"id": id, "estudiante_id": data["estudiante_id"], "tipo": data["tipo"], "descripcion": data["descripcion"],
            "prioridad": p, "estado": "PEND", "responsable_id": None, "area": a, "fecha_alta": f, "fecha_mod": f,
            "canal": canal, "obs": data.get("obs", "")}
