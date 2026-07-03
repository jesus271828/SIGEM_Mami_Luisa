import sqlite3

def arreglar_db():
    conn = sqlite3.connect('colegio.db')
    cursor = conn.cursor()
    # Este comando añade la tabla solo si no existe, sin borrar nada de lo anterior
    cursor.execute('''CREATE TABLE IF NOT EXISTS asistencia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alumno_id INTEGER,
        fecha TEXT,
        estado TEXT,
        FOREIGN KEY(alumno_id) REFERENCES alumnos(id)
    )''')
    conn.commit()
    conn.close()
    print("Tabla de asistencia creada correctamente sin borrar tus datos.")

if __name__ == '__main__':
    arreglar_db()