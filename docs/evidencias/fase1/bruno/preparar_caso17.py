import sqlite3

conn = sqlite3.connect("solicitudes.db")
conn.execute(
    "INSERT INTO solicitudes "
    "(estudiante_id, tipo, descripcion, prioridad, estado, responsable_id, "
    "area, fecha_alta, fecha_mod, canal, obs) "
    "VALUES (1, 'CERT', 'Caso 17 - fecha sin hora', 3, 'PEND', NULL, "
    "'Alumnado', '2026-11-01', '2026-11-01', 'WEB', '')"
)
conn.commit()
conn.close()
print("Listo: se inserto una solicitud con fecha_alta sin hora")