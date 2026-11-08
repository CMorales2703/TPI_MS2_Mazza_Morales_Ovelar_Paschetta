"""Solicitudes: cambio de estado y asignación de responsable."""

import sqlite3
from datetime import datetime

from fastapi import APIRouter, Body, Depends, HTTPException

from app.db import get_db

from app.dominio import ESTADOS_CERRADOS, transicion_permitida

router = APIRouter()

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

@router.put("/solicitudes/{id}/estado")
def proc_estado(id: int, data: dict = Body(...), conn: sqlite3.Connection = Depends(get_db)):
    c = conn.cursor()
    c.row_factory = sqlite3.Row
    c.execute("SELECT * FROM solicitudes WHERE id = ?", (id,))
    s = c.fetchone()
    if s is None:
        raise HTTPException(status_code=404, detail="no existe")
    nuevo = data.get("estado")
    act = s["estado"]

    if not transicion_permitida(act, nuevo):
        return {"error": "transicion no permitida de " + act + " a " + str(nuevo)}
    if nuevo == "ASIG" and s["responsable_id"] is None:
        return {"error": "no tiene responsable"}
    if nuevo == "RECH" and ("comentario" not in data or data["comentario"] == ""):
        return {"error": "para rechazar hay que poner motivo"}

    f = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("UPDATE solicitudes SET estado = ?, fecha_mod = ? WHERE id = ?", (nuevo, f, id))
    registrar_en_historial(conn, id, act, nuevo, f, data.get("comentario", ""))
    conn.commit()

    c.execute("SELECT * FROM estudiantes WHERE id = ?", (s["estudiante_id"],))
    est = c.fetchone()
    notificar_cambio_estado(est, id, nuevo, f)

    return {"id": id, "estado": nuevo, "estado_anterior": act}


@router.put("/solicitudes/{id}/responsable")
def asignar(id: int, data: dict = Body(...), conn: sqlite3.Connection = Depends(get_db)):
    c = conn.cursor()
    c.row_factory = sqlite3.Row
    c.execute("SELECT * FROM solicitudes WHERE id = ?", (id,))
    s = c.fetchone()
    if s is None:
        return {"error": "solicitud no existe"}
    if s["estado"] in ESTADOS_CERRADOS:
        return {"error": "la solicitud esta cerrada"}
    c.execute("SELECT * FROM responsables WHERE id = ?", (data.get("responsable_id"),))
    r = c.fetchone()
    if r is None:
        return {"error": "responsable no existe"}
    if r["activo"] == 0:
        return {"error": "responsable inactivo"}
    if r["area"] != s["area"]:
        return {"error": "el responsable no pertenece al area " + s["area"]}

    f = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nuevo_estado = s["estado"]
    if s["estado"] == "PEND":
        nuevo_estado = "ASIG"
    c.execute("UPDATE solicitudes SET responsable_id = ?, estado = ?, fecha_mod = ? WHERE id = ?",
              (r["id"], nuevo_estado, f, id))

    if nuevo_estado != s["estado"]:
        registrar_en_historial(conn, id, s["estado"], nuevo_estado, f, "asignada a " + r["nombre"])
    conn.commit()
    return {"id": id, "responsable_id": r["id"], "responsable": r["nombre"], "estado": nuevo_estado}
