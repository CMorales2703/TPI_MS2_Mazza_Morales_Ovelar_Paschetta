"""Validaciones de datos de entrada compartidas entre endpoints."""


def email_invalido(data):
    """Indica si el body trae un email sin '@'.

    Mantiene el comportamiento original: si no viene email, es válido; si viene
    en null, falla con TypeError (defecto documentado, caso 10 de la Fase 1).
    """
    return "email" in data and "@" not in data["email"]
