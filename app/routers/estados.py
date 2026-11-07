"""Solicitudes: cambio de estado y asignación de responsable."""

import sqlite3
from datetime import datetime

from fastapi import APIRouter, Body, Depends, HTTPException

from app.db import get_db

from app.dominio import ESTADOS_CERRADOS, transicion_permitida

router = APIRouter()


@router.put("/solicitudes/{id}/estado")
def proc_estado(id: int, data: dict = Body(...), conn: sqlite3.Connection = Depends(get_db)):
    c = conn.cursor()
    c.execute("SELECT * FROM solicitudes WHERE id = ?", (id,))
    s = c.fetchone()
    if s is None:
        raise HTTPException(status_code=404, detail="no existe")
    nuevo = data.get("estado")
    act = s[5]

    if not transicion_permitida(act, nuevo):
        return {"error": "transicion no permitida de " + act + " a " + str(nuevo)}
    if nuevo == "ASIG" and s[6] is None:
        return {"error": "no tiene responsable"}
    if nuevo == "RECH" and ("comentario" not in data or data["comentario"] == ""):
        return {"error": "para rechazar hay que poner motivo"}

    f = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("UPDATE solicitudes SET estado = ?, fecha_mod = ? WHERE id = ?", (nuevo, f, id))
    c.execute("INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (?,?,?,?,?)",
              (id, act, nuevo, f, data.get("comentario", "")))
    conn.commit()

    # notificar al estudiante
    c.execute("SELECT * FROM estudiantes WHERE id = ?", (s[1],))
    est = c.fetchone()
    try:
        with open("notificaciones.log", "a") as arch:
            arch.write(f + " - Se envio mail a " + est[4] + ": su solicitud " + str(id) + " paso a " + nuevo + "\n")
    except:
        pass

    return {"id": id, "estado": nuevo, "estado_anterior": act}


@router.put("/solicitudes/{id}/responsable")
def asignar(id: int, data: dict = Body(...), conn: sqlite3.Connection = Depends(get_db)):
    c = conn.cursor()
    c.execute("SELECT * FROM solicitudes WHERE id = ?", (id,))
    s = c.fetchone()
    if s is None:
        return {"error": "solicitud no existe"}
    if s[5] in ESTADOS_CERRADOS:
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
    c.execute("UPDATE solicitudes SET responsable_id = ?, estado = ?, fecha_mod = ? WHERE id = ?",
              (r[0], nuevo_estado, f, id))
    if nuevo_estado != s[5]:
        c.execute("INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (?,?,?,?,?)",
                  (id, s[5], nuevo_estado, f, "asignada a " + r[1]))
    conn.commit()
    return {"id": id, "responsable_id": r[0], "responsable": r[1], "estado": nuevo_estado}
