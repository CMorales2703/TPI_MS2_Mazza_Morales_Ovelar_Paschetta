import sqlite3

conn = sqlite3.connect("solicitudes.db")
conn.execute("DELETE FROM solicitudes WHERE descripcion LIKE 'Caso 1%'")
conn.execute(
    "INSERT INTO solicitudes "
    "(estudiante_id, tipo, descripcion, prioridad, estado, responsable_id, "
    "area, fecha_alta, fecha_mod, canal, obs) "
    "VALUES (1, 'CERT', 'Caso 18 - fecha nula', 3, 'PEND', NULL, "
    "'Alumnado', NULL, NULL, 'WEB', '')"
)
conn.commit()
conn.close()
print("Listo: se borro el registro del caso 17 y se inserto uno con fecha_alta nula")