"""Solicitudes: búsqueda, detalle y reporte."""

import sqlite3
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.db import get_db

router = APIRouter()


def fila_a_solicitud(fila):
    """Convierte una fila de la tabla solicitudes en un diccionario."""
    return {
        "id": fila[0],
        "estudiante_id": fila[1],
        "tipo": fila[2],
        "descripcion": fila[3],
        "prioridad": fila[4],
        "estado": fila[5],
        "responsable_id": fila[6],
        "area": fila[7],
        "fecha_alta": fila[8],
        "fecha_mod": fila[9],
        "canal": fila[10],
        "obs": fila[11],
    }


def contar(conteos, clave):
    """Suma uno al contador de esa clave."""
    conteos[clave] = conteos.get(clave, 0) + 1


def esta_cerrada(estado):
    """Una solicitud cerrada ya no puede vencer."""
    return estado in ("RES", "RECH", "CANC")


def dias_limite(prioridad):
    """Dias que una solicitud puede permanecer abierta segun su prioridad."""
    if prioridad == 1:
        return 2
    if prioridad == 2:
        return 5
    return 10


def dias_abierta(fecha_alta, hoy):
    """Dias transcurridos desde el alta de la solicitud."""
    return (hoy - datetime.strptime(fecha_alta, "%Y-%m-%d %H:%M:%S")).days


def porcentaje_resueltas(por_estado, total):
    """Porcentaje de solicitudes en estado RES sobre el total."""
    if total == 0:
        return 0
    return round(por_estado.get("RES", 0) * 100 / total, 2)


@router.get("/solicitudes")
def buscar(estado: str = None, tipo: str = None, prioridad: int = None, area: str = None, estudiante_id: int = None,
           texto: str = None, desde: str = None, hasta: str = None, orden: str = "fecha",
           conn: sqlite3.Connection = Depends(get_db)):
    c = conn.cursor()
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
    return [fila_a_solicitud(r) for r in rows]


@router.get("/solicitudes/{id}")
def getSolicitud(id: int, conn: sqlite3.Connection = Depends(get_db)):
    c = conn.cursor()
    c.execute("SELECT * FROM solicitudes WHERE id = ?", (id,))
    r = c.fetchone()
    if r is None:
        raise HTTPException(status_code=404, detail="no existe")
    d = fila_a_solicitud(r)
    c.execute("SELECT * FROM historial WHERE solicitud_id = ? ORDER BY id", (id,))
    h = []
    for x in c.fetchall():
        h.append({"estado_anterior": x[2], "estado_nuevo": x[3], "fecha": x[4], "comentario": x[5]})
    d["historial"] = h
    return d


@router.get("/reporte")
def reporte(conn: sqlite3.Connection = Depends(get_db)):
    c = conn.cursor()
    c.execute("SELECT * FROM solicitudes")
    todas = c.fetchall()
    por_estado = {}
    por_tipo = {}
    por_area = {}
    vencidas = []
    hoy = datetime.now()
    for s in todas:
        contar(por_estado, s[5])
        contar(por_tipo, s[2])
        contar(por_area, s[7])
        if not esta_cerrada(s[5]):
            dias = dias_abierta(s[8], hoy)
            if dias > dias_limite(s[4]):
                vencidas.append({"id": s[0], "tipo": s[2], "prioridad": s[4], "dias": dias})
    total = len(todas)
    return {
        "total": total,
        "por_estado": por_estado,
        "por_tipo": por_tipo,
        "por_area": por_area,
        "porcentaje_resueltas": porcentaje_resueltas(por_estado, total),
        "vencidas": vencidas,
    }