import csv
import sqlite3
import os

def importar_datos():
    db_path = os.path.join(os.getcwd(), 'colegio.db')
    archivo_csv = 'EXPEDIENTES.csv'
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    count = 0
    with open(archivo_csv, encoding='utf-8-sig') as f:
        # Leemos cada línea manualmente para evitar problemas con muchos ';'
        for linea in f:
            partes = linea.split(';')
            # Filtramos solo las partes que contienen texto real
            datos_reales = [p.strip() for p in partes if p.strip() != ""]
            
            # Buscamos al menos 3 datos: Nombre, Año, Ficha
            if len(datos_reales) >= 3:
                nombre = datos_reales[0]
                ano = datos_reales[1]
                ficha = datos_reales[2]
                
                # Omitimos si es la fila de encabezado
                if nombre.upper() == "NOMBRE":
                    continue
                
                cursor.execute('''INSERT INTO expedientes_viejos (nombre_estudiante, ano_escolar, codigo_archivo) 
                                  VALUES (?, ?, ?)''', (nombre, ano, ficha))
                count += 1
                
    conn.commit()
    conn.close()
    print(f"¡Importación exitosa! Se añadieron {count} registros limpios.")

if __name__ == "__main__":
    importar_datos()