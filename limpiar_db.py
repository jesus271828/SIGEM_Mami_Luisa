import sqlite3
conn = sqlite3.connect('colegio.db')
cursor = conn.cursor()
cursor.execute('DELETE FROM expedientes_viejos') # Borra todo
conn.commit()
conn.close()
print("Base de datos limpia.")