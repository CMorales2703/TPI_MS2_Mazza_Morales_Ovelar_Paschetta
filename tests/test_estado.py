def test_cambiar_estado_asig_a_en_proc(client):
    """Caso 13: transición válida ASIG -> EN_PROC (solicitud 2)."""
    respuesta = client.put("/solicitudes/2/estado", json={"estado": "EN_PROC"})

    # Actual: 200. Esperado: 200.
    assert respuesta.status_code == 200
    assert respuesta.json() == {"id": 2, "estado": "EN_PROC", "estado_anterior": "ASIG"}
    solicitud = client.get("/solicitudes/2").json()                                     
    assert solicitud["estado"] == "EN_PROC"                                             
    assert solicitud["historial"][-1]["estado_nuevo"] == "EN_PROC"                      


def test_cambiar_estado_solicitud_inexistente(client):
    """Caso 1: solicitud inexistente responde 404 con formato detail (hallazgo 1)."""
    respuesta = client.put("/solicitudes/999/estado", json={"estado": "ASIG"})

    # Actual: 404 {"detail": "no existe"}. Esperado: 404 con formato "error".
    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "no existe"}


def test_cambiar_estado_transicion_no_permitida(client):
    """Caso 5: PEND -> RES no permitida, pero responde 200 (hallazgos 1 y 2)."""
    antes = client.get("/solicitudes/1").json()                                         
    respuesta = client.put("/solicitudes/1/estado", json={"estado": "RES"})

    # Actual: 200 con error. Esperado: 409.
    assert respuesta.status_code == 200
    assert respuesta.json() == {"error":"transicion no permitida de PEND a RES"}
    assert client.get("/solicitudes/1").json() == antes                                 


def test_rechazar_acepta_motivo_nulo(client):
    """Caso 15: rechaza con comentario null (hallazgo 4)."""
    respuesta = client.put("/solicitudes/3/estado",
                           json={"estado": "RECH", "comentario": None})

    # Actual: 200 y rechaza. Esperado: 422 sin cambiar el estado.
    assert respuesta.status_code == 200
    assert respuesta.json() =={"id":3,"estado":"RECH","estado_anterior":"EN_PROC"}
    solicitud = client.get("/solicitudes/3").json()                                     
    assert solicitud["estado"] == "RECH"                                                
    assert solicitud["historial"][-1]["comentario"] is None                             


def test_cambiar_estado_a_asig_sin_responsable(client):
    """Caso 4: PEND -> ASIG sin responsable (hallazgos 1 y 3)."""
    antes = client.get("/solicitudes/1").json()

    respuesta = client.put("/solicitudes/1/estado", json={"estado": "ASIG"})

    # Actual: 200 con error. Esperado: 409.
    assert respuesta.status_code == 200
    assert respuesta.json() == {"error": "no tiene responsable"}
    assert client.get("/solicitudes/1").json() == antes