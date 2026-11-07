"""Solicitudes: registro de una solicitud nueva."""

import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime

from fastapi import APIRouter, Body, Depends

from app.db import get_db
from app.dominio import REGLAS_POR_TIPO, TIPOS

router = APIRouter()


@dataclass
class NuevaSolicitud:
    """Datos de una solicitud nueva, tal como se guardan en la tabla solicitudes."""

    estudiante_id: int
    tipo: str
    descripcion: str
    prioridad: int
    estado: str
    responsable_id: int | None
    area: str
    fecha_alta: str
    fecha_mod: str
    canal: str
    obs: str


def guardar_solicitud(conn, solicitud):
    c = conn.cursor()
    c.execute("""INSERT INTO solicitudes (estudiante_id, tipo, descripcion, prioridad, estado, responsable_id, area,
                 fecha_alta, fecha_mod, canal, obs)
                 VALUES (:estudiante_id, :tipo, :descripcion, :prioridad, :estado, :responsable_id, :area,
                         :fecha_alta, :fecha_mod, :canal, :obs)""",
              asdict(solicitud))
    conn.commit()
    return c.lastrowid


def calcular_prioridad(tipo, descripcion):
    """Prioridad por defecto: 1 si la descripción dice "urgente"; si no, la del tipo."""
    if "urgente" in descripcion.lower():
        return 1
    return REGLAS_POR_TIPO[tipo]["prioridad"]


def determinar_area(tipo):
    """Área que atiende las solicitudes del tipo."""
    return REGLAS_POR_TIPO[tipo]["area"]


def registrar_alta_en_historial(conn, solicitud_id, fecha):
    """Agrega al historial la fila del alta (sin estado anterior, pasa a PEND)."""
    conn.execute("INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (?,?,?,?,?)",
                 (solicitud_id, None, "PEND", fecha, "alta de solicitud"))
    conn.commit()


def notificar_alta(email, solicitud_id, fecha):
    """Deja en notificaciones.log el aviso de alta al estudiante."""
    try:
        with open("notificaciones.log", "a") as arch:
            arch.write(fecha + " - Se envio mail a " + email + ": su solicitud " + str(solicitud_id) + " fue registrada\n")
    except:
        pass


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
    if "tipo" not in data or data["tipo"] not in TIPOS:
        return {"error": "tipo invalido"}
    if "descripcion" not in data or len(data["descripcion"]) < 10:
        return {"error": "descripcion muy corta"}

    p = data.get("prioridad")
    if p is None:
        p = calcular_prioridad(data["tipo"], data["descripcion"])
    elif p not in [1, 2, 3]:
        return {"error": "prioridad invalida"}

    a = determinar_area(data["tipo"])

    canal = data.get("canal", "WEB")
    if canal not in ["WEB", "MAIL", "PRESENCIAL"]:
        canal = "WEB"

    f = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    solicitud = NuevaSolicitud(estudiante_id=data["estudiante_id"], tipo=data["tipo"], descripcion=data["descripcion"],
                               prioridad=p, estado="PEND", responsable_id=None, area=a,
                               fecha_alta=f, fecha_mod=f, canal=canal, obs=data.get("obs", ""))
    id = guardar_solicitud(conn, solicitud)
    registrar_alta_en_historial(conn, id, f)
    # c.execute("UPDATE estudiantes SET carrera = 'TUP' WHERE id = ?", (data["estudiante_id"],))
    # conn.commit()

    notificar_alta(est[4], id, f)

    return {"id": id, **asdict(solicitud)}
