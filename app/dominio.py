"""Valores del dominio compartidos por todo el sistema."""

AREAS = ("Alumnado", "Departamento Academico", "Bedelia", "Coordinacion")

CARRERA_POR_DEFECTO = "TUP"


# Regla de cada tipo de solicitud: área que la atiende y prioridad por defecto
REGLAS_POR_TIPO = {
    "CERT": {"area": "Alumnado", "prioridad": 3},
    "EQUIV": {"area": "Departamento Academico", "prioridad": 2},
    "MESA": {"area": "Bedelia", "prioridad": 1},
    "RECLAMO": {"area": "Coordinacion", "prioridad": 1},
    "BAJA": {"area": "Alumnado", "prioridad": 2},
}

TIPOS = tuple(REGLAS_POR_TIPO)

TRANSICIONES = {
    "PEND": ("ASIG", "CANC"),
    "ASIG": ("EN_PROC", "CANC"),
    "EN_PROC": ("RES", "RECH"),
}

ESTADOS_CERRADOS = ("RES", "RECH", "CANC")


def transicion_permitida(actual, nuevo):
    """Indica si una solicitud puede pasar del estado actual al nuevo."""
    return nuevo in TRANSICIONES.get(actual, ())

