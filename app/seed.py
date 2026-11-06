"""Datos de prueba sintéticos del sistema."""


def base_vacia(conn):
    """Indica si la base todavía no tiene estudiantes cargados."""
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM estudiantes")
    return c.fetchone()[0] == 0


def cargar_datos_de_prueba(conn):
    """Carga los estudiantes, responsables, solicitudes e historial de prueba."""
    c = conn.cursor()
    c.execute(
        "INSERT INTO estudiantes (nombre, apellido, legajo, email, carrera) VALUES ('Lucia','Ferreyra','TUP-1001','lucia.ferreyra@ejemplo.com','TUP')"
    )
    c.execute(
        "INSERT INTO estudiantes (nombre, apellido, legajo, email, carrera) VALUES ('Mateo','Quiroga','TUP-1002','mateo.quiroga@ejemplo.com','TUP')"
    )
    c.execute(
        "INSERT INTO estudiantes (nombre, apellido, legajo, email, carrera) VALUES ('Sofia','Aranda','TUP-1003','sofia.aranda@ejemplo.com','TUP')"
    )
    c.execute(
        "INSERT INTO estudiantes (nombre, apellido, legajo, email, carrera) VALUES ('Tomas','Villalba','TUP-1004','tomas.villalba@ejemplo.com','TUP')"
    )
    c.execute(
        "INSERT INTO responsables (nombre, area, email, activo) VALUES ('Graciela Molina','Alumnado','gmolina@ejemplo.com',1)"
    )
    c.execute(
        "INSERT INTO responsables (nombre, area, email, activo) VALUES ('Ruben Castro','Alumnado','rcastro@ejemplo.com',0)"
    )
    c.execute(
        "INSERT INTO responsables (nombre, area, email, activo) VALUES ('Paula Diaz','Departamento Academico','pdiaz@ejemplo.com',1)"
    )
    c.execute(
        "INSERT INTO responsables (nombre, area, email, activo) VALUES ('Hector Ruiz','Bedelia','hruiz@ejemplo.com',1)"
    )
    c.execute(
        "INSERT INTO responsables (nombre, area, email, activo) VALUES ('Marina Sosa','Coordinacion','msosa@ejemplo.com',1)"
    )
    c.execute(
        "INSERT INTO solicitudes (estudiante_id, tipo, descripcion, prioridad, estado, responsable_id, area, fecha_alta, fecha_mod, canal, obs) VALUES (1,'CERT','Necesito certificado de alumna regular para la obra social',3,'PEND',NULL,'Alumnado','2026-09-01 10:15:00','2026-09-01 10:15:00','WEB','')"
    )
    c.execute(
        "INSERT INTO solicitudes (estudiante_id, tipo, descripcion, prioridad, estado, responsable_id, area, fecha_alta, fecha_mod, canal, obs) VALUES (2,'EQUIV','Pido equivalencia de Programacion I aprobada en otra universidad',2,'ASIG',3,'Departamento Academico','2026-09-03 09:00:00','2026-09-04 11:20:00','MAIL','adjunta programa')"
    )
    c.execute(
        "INSERT INTO solicitudes (estudiante_id, tipo, descripcion, prioridad, estado, responsable_id, area, fecha_alta, fecha_mod, canal, obs) VALUES (3,'MESA','Solicito mesa especial de Matematica por superposicion de fechas',1,'EN_PROC',4,'Bedelia','2026-09-10 14:30:00','2026-09-12 08:45:00','WEB','')"
    )
    c.execute(
        "INSERT INTO solicitudes (estudiante_id, tipo, descripcion, prioridad, estado, responsable_id, area, fecha_alta, fecha_mod, canal, obs) VALUES (4,'RECLAMO','La nota del parcial 1 no figura cargada en el sistema',1,'RES',5,'Coordinacion','2026-09-15 16:00:00','2026-09-16 10:00:00','PRESENCIAL','')"
    )
    c.execute(
        "INSERT INTO solicitudes (estudiante_id, tipo, descripcion, prioridad, estado, responsable_id, area, fecha_alta, fecha_mod, canal, obs) VALUES (1,'BAJA','Quiero dar de baja la materia Ingles II este cuatrimestre',2,'RECH',1,'Alumnado','2026-09-20 12:00:00','2026-09-22 09:30:00','WEB','')"
    )
    c.execute(
        "INSERT INTO solicitudes (estudiante_id, tipo, descripcion, prioridad, estado, responsable_id, area, fecha_alta, fecha_mod, canal, obs) VALUES (2,'CERT','Certificado analitico parcial urgente para presentar en trabajo',1,'PEND',NULL,'Alumnado','2026-10-01 08:10:00','2026-10-01 08:10:00','WEB','')"
    )
    c.execute(
        "INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (1,NULL,'PEND','2026-09-01 10:15:00','alta de solicitud')"
    )
    c.execute(
        "INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (2,NULL,'PEND','2026-09-03 09:00:00','alta de solicitud')"
    )
    c.execute(
        "INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (2,'PEND','ASIG','2026-09-04 11:20:00','asignada a Paula Diaz')"
    )
    c.execute(
        "INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (3,NULL,'PEND','2026-09-10 14:30:00','alta de solicitud')"
    )
    c.execute(
        "INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (3,'PEND','ASIG','2026-09-11 09:00:00','asignada a Hector Ruiz')"
    )
    c.execute(
        "INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (3,'ASIG','EN_PROC','2026-09-12 08:45:00','')"
    )
    c.execute(
        "INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (4,NULL,'PEND','2026-09-15 16:00:00','alta de solicitud')"
    )
    c.execute(
        "INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (4,'PEND','ASIG','2026-09-15 17:00:00','asignada a Marina Sosa')"
    )
    c.execute(
        "INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (4,'ASIG','EN_PROC','2026-09-16 08:00:00','')"
    )
    c.execute(
        "INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (4,'EN_PROC','RES','2026-09-16 10:00:00','nota cargada')"
    )
    c.execute(
        "INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (5,NULL,'PEND','2026-09-20 12:00:00','alta de solicitud')"
    )
    c.execute(
        "INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (5,'PEND','ASIG','2026-09-21 10:00:00','asignada a Graciela Molina')"
    )
    c.execute(
        "INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (5,'ASIG','EN_PROC','2026-09-21 15:00:00','')"
    )
    c.execute(
        "INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (5,'EN_PROC','RECH','2026-09-22 09:30:00','fuera de termino')"
    )
    c.execute(
        "INSERT INTO historial (solicitud_id, estado_ant, estado_nuevo, fecha, comentario) VALUES (6,NULL,'PEND','2026-10-01 08:10:00','alta de solicitud')"
    )
    conn.commit()
