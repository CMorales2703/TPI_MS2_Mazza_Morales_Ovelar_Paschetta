"""Solicitudes: búsqueda, detalle y reporte."""

import sqlite3
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.db import get_db

router = APIRouter()


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
    res = []
    for r in rows:
        res.append({"id": r[0], "estudiante_id": r[1], "tipo": r[2], "descripcion": r[3], "prioridad": r[4],
                    "estado": r[5], "responsable_id": r[6], "area": r[7], "fecha_alta": r[8], "fecha_mod": r[9],
                    "canal": r[10], "obs": r[11]})
    return res


@router.get("/solicitudes/{id}")
def getSolicitud(id: int, conn: sqlite3.Connection = Depends(get_db)):
    c = conn.cursor()
    c.execute("SELECT * FROM solicitudes WHERE id = ?", (id,))
    r = c.fetchone()
    if r is None:
        raise HTTPException(status_code=404, detail="no existe")
    d = {"id": r[0], "estudiante_id": r[1], "tipo": r[2], "descripcion": r[3], "prioridad": r[4], "estado": r[5],
         "responsable_id": r[6], "area": r[7], "fecha_alta": r[8], "fecha_mod": r[9], "canal": r[10], "obs": r[11]}
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
                vencidas.append({"id": s[0], "tipo": s[2], "prioridad": s[4], "dias": (hoy - fa).days})
    resueltas = por_estado.get("RES", 0)
    porc = 0
    if total > 0:
        porc = round(resueltas * 100 / total, 2)
    return {"total": total, "por_estado": por_estado, "por_tipo": por_tipo, "por_area": por_area,
            "porcentaje_resueltas": porc, "vencidas": vencidas}
