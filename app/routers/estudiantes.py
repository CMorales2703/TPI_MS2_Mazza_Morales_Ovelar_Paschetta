"""Estudiantes: alta y listado."""

import sqlite3

from fastapi import APIRouter, Body, Depends

from app.db import get_db
from app.dominio import CARRERA_POR_DEFECTO
from app.validaciones import email_invalido

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


def validar_estudiante(data):
    """Devuelve el mensaje de error del primer dato inválido, o None si están bien."""
    if "nombre" not in data or data["nombre"] == "" or data["nombre"] is None:
        return "falta nombre"
    if "apellido" not in data or data["apellido"] == "":
        return "falta apellido"
    if "legajo" not in data or data["legajo"] == "":
        return "falta legajo"
    if email_invalido(data):
        return "email invalido"
    return None


def legajo_existe(conn, legajo):
    """Indica si ya hay un estudiante con ese legajo."""
    c = conn.cursor()
    c.execute("SELECT * FROM estudiantes WHERE legajo = ?", (legajo,))
    return c.fetchone() is not None


def insertar_estudiante(conn, data):
    """Guarda el estudiante y devuelve el registro creado."""
    estudiante = {
        "nombre": data["nombre"],
        "apellido": data["apellido"],
        "legajo": data["legajo"],
        "email": data.get("email", ""),
        "carrera": data.get("carrera", CARRERA_POR_DEFECTO),
    }
    c = conn.cursor()
    c.execute(
        "INSERT INTO estudiantes (nombre, apellido, legajo, email, carrera) VALUES (?,?,?,?,?)",
        (
            estudiante["nombre"],
            estudiante["apellido"],
            estudiante["legajo"],
            estudiante["email"],
            estudiante["carrera"],
        ),
    )
    conn.commit()
    return {"id": c.lastrowid, **estudiante}


@router.post("/estudiantes")
def crear_estudiante(
    data: dict = Body(...), conn: sqlite3.Connection = Depends(get_db)
):
    error = validar_estudiante(data)
    if error:
        return {"error": error}
    if legajo_existe(conn, data["legajo"]):
        return {"error": "legajo repetido"}
    return insertar_estudiante(conn, data)


@router.get("/estudiantes")
def listar_estudiantes(conn: sqlite3.Connection = Depends(get_db)):
    c = conn.cursor()
    c.row_factory = sqlite3.Row
    c.execute("SELECT * FROM estudiantes")
    return [fila_a_estudiante(fila) for fila in c.fetchall()]
