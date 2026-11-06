"""Acceso a la base de datos: conexión y creación de las tablas."""

import sqlite3

from fastapi import Request

RUTA_DB_POR_DEFECTO = "solicitudes.db"


def conectar(ruta_db):
    """Abre una conexión a la base indicada."""
    return sqlite3.connect(ruta_db, check_same_thread=False)


def crear_tablas(conn):
    """Crea las tablas del sistema si todavía no existen."""
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS estudiantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, apellido TEXT, legajo TEXT, email TEXT, carrera TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS responsables (
        id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, area TEXT, email TEXT, activo INTEGER)""")
    c.execute("""CREATE TABLE IF NOT EXISTS solicitudes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, estudiante_id INTEGER, tipo TEXT, descripcion TEXT, prioridad INTEGER,
        estado TEXT, responsable_id INTEGER, area TEXT, fecha_alta TEXT, fecha_mod TEXT, canal TEXT, obs TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS historial (
        id INTEGER PRIMARY KEY AUTOINCREMENT, solicitud_id INTEGER, estado_ant TEXT, estado_nuevo TEXT, fecha TEXT, comentario TEXT)""")
    conn.commit()


def get_db(request: Request):
    """Dependencia de FastAPI: abre una conexión por request y la cierra al terminar."""
    conn = conectar(request.app.state.ruta_db)
    try:
        yield conn
    finally:
        conn.close()
