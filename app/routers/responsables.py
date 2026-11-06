"""Responsables: alta y listado."""

import sqlite3

from fastapi import APIRouter, Body, Depends

from app.db import get_db

router = APIRouter()


def fila_a_responsable(fila):
    """Convierte una fila de la tabla responsables en el diccionario de respuesta."""
    return {
        "id": fila["id"],
        "nombre": fila["nombre"],
        "area": fila["area"],
        "email": fila["email"],
        "activo": fila["activo"] == 1,
    }


@router.post("/responsables")
def crear_responsable(
    data: dict = Body(...), conn: sqlite3.Connection = Depends(get_db)
):
    c = conn.cursor()
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


@router.get("/responsables")
def listar_responsables(conn: sqlite3.Connection = Depends(get_db)):
    c = conn.cursor()
    c.row_factory = sqlite3.Row
    c.execute("SELECT * FROM responsables")
    return [fila_a_responsable(fila) for fila in c.fetchall()]
