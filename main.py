"""Punto de entrada: crea la aplicación y registra los routers."""

from contextlib import asynccontextmanager

from app.routers import consultas, estados, estudiantes, responsables, solicitudes
from fastapi import FastAPI

from app.db import RUTA_DB_POR_DEFECTO, conectar, crear_tablas
from app.seed import base_vacia, cargar_datos_de_prueba


def preparar_base(ruta_db):
    """Crea las tablas y, si la base está vacía, carga los datos de prueba."""
    conn = conectar(ruta_db)
    try:
        crear_tablas(conn)
        if base_vacia(conn):
            cargar_datos_de_prueba(conn)
    finally:
        conn.close()


def crear_app(ruta_db=RUTA_DB_POR_DEFECTO):
    """Crea la aplicación sobre la base indicada.

    La base se prepara al arrancar la aplicación, no al importar el módulo.
    """

    @asynccontextmanager
    async def lifespan(app):
        preparar_base(app.state.ruta_db)
        yield

    app = FastAPI(
        title="Sistema de Gestion de Solicitudes Academicas", lifespan=lifespan
    )
    app.state.ruta_db = ruta_db
    app.include_router(estudiantes.router)
    app.include_router(responsables.router)
    app.include_router(solicitudes.router)
    app.include_router(estados.router)
    app.include_router(consultas.router)
    return app


app = crear_app()
