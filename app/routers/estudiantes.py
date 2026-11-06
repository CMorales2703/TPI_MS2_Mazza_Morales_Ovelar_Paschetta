"""Estudiantes: alta y listado."""

import sqlite3

from fastapi import APIRouter, Body, Depends

from app.db import get_db

router = APIRouter()


def fila_a_estudiante(fila):
    """Convierte una fila de la tabla estudiantes en el diccionario de respuesta."""
    return {
        "id": fila["id"],
        "nombre": fila["nombre"],
        "apellido": fila["apellido"],
        "legajo": fila["legajo"],
        "email": fila["email"],
        "carrera": fila["carrera"],
    }


@router.post("/estudiantes")
def crear_estudiante(
    data: dict = Body(...), conn: sqlite3.Connection = Depends(get_db)
):
    c = conn.cursor()
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


@router.get("/estudiantes")
def listar_estudiantes(conn: sqlite3.Connection = Depends(get_db)):
    c = conn.cursor()
    c.row_factory = sqlite3.Row
    c.execute("SELECT * FROM estudiantes")
    return [fila_a_estudiante(fila) for fila in c.fetchall()]
