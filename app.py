from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave_secreta_super_segura")

def get_db_connection():
    conn = sqlite3.connect('colegio.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, rol TEXT, grado TEXT, ciclo TEXT)''')
        # (Se mantiene tu tabla alumnos actual con todos sus campos)
        conn.execute('''CREATE TABLE IF NOT EXISTS alumnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nombres TEXT, apellidos TEXT, fecha_nacimiento TEXT, lugar_nacimiento TEXT, 
            nacionalidad TEXT, direccion TEXT, grado TEXT, edad INTEGER, sexo TEXT, cant_hermanos INTEGER, edades_hermanos TEXT, 
            lugar_ocupa TEXT, tipo_sangre TEXT, seguro_medico TEXT, alergias TEXT, medicamentos TEXT, centro_medico TEXT, 
            pediatra TEXT, tel_emergencia TEXT, emerg_nombre TEXT, emerg_parentesco TEXT, padre_nombre TEXT, padre_sector TEXT, 
            padre_direccion TEXT, padre_cedula TEXT, padre_profesion TEXT, padre_nivel TEXT, padre_religion TEXT, padre_telefono TEXT, 
            padre_tel_trabajo TEXT, padre_email TEXT, madre_nombre TEXT, madre_sector TEXT, madre_direccion TEXT, madre_cedula TEXT, 
            madre_profesion TEXT, madre_nivel TEXT, madre_religion TEXT, madre_telefono TEXT, madre_tel_trabajo TEXT, madre_email TEXT, 
            tutor_nombre TEXT, tutor_sector TEXT, tutor_direccion TEXT, tutor_cedula TEXT, tutor_profesion TEXT, tutor_nivel TEXT, 
            tutor_religion TEXT, tutor_telefono TEXT, tutor_tel_trabajo TEXT, tutor_email TEXT, ano_escolar TEXT, fecha_inscripcion TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, alumno_id INTEGER, materia TEXT, c1 INTEGER, c2 INTEGER, c3 INTEGER, 
            FOREIGN KEY(alumno_id) REFERENCES alumnos(id))''')
        conn.commit()
init_db()

# --- RUTAS ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session: return redirect('/menu')
    if request.method == 'POST':
        user, password = request.form['username'], request.form['password']
        conn = get_db_connection()
        usuario = conn.execute('SELECT * FROM usuarios WHERE username = ? AND password = ?', (user, password)).fetchone()
        conn.close()
        if usuario:
            session.update({'username': usuario['username'], 'rol': usuario['rol'], 'ciclo': usuario['ciclo'], 'grado': usuario['grado']})
            return redirect('/menu')
        return "Usuario o contraseña incorrectos. <a href='/'>Volver</a>"
    return render_template('login.html')

@app.route('/menu')
def menu():
    if 'username' not in session: return redirect('/')
    return render_template('menu.html', username=session.get('username'), ciclo=session.get('ciclo'), rol=session.get('rol'))

@app.route('/listado', methods=['GET'])
def listado():
    if 'username' not in session: return redirect('/')
    conn = get_db_connection()
    grado_usuario = str(session.get('grado', '')).replace("-", "").strip()
    busqueda = request.args.get('busqueda', '')
    
    query = "SELECT * FROM alumnos WHERE 1=1"
    params = []
    if session.get('rol') != 'oficina':
        query += " AND grado = ?"
        params.append(grado_usuario)
    if busqueda:
        query += " AND (nombres LIKE ? OR apellidos LIKE ?)"
        params.extend(['%'+busqueda+'%', '%'+busqueda+'%'])
    
    alumnos = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('listado_general.html', alumnos=alumnos, busqueda=busqueda)

@app.route('/notas', methods=['GET'])
def notas():
    if 'username' not in session: return redirect('/')
    conn = get_db_connection()
    grado_usuario = str(session.get('grado', '')).replace("-", "").strip()
    
    if session.get('rol') == 'oficina':
        alumnos = conn.execute('SELECT id, nombres, apellidos FROM alumnos').fetchall()
    else:
        alumnos = conn.execute('SELECT id, nombres, apellidos FROM alumnos WHERE grado = ?', (grado_usuario,)).fetchall()
    
    alumno_id = request.args.get('alumno_id')
    alumno_seleccionado = conn.execute('SELECT * FROM alumnos WHERE id = ?', (alumno_id,)).fetchone() if alumno_id else None
    notas_alumno = {}
    if alumno_id:
        registros = conn.execute('SELECT materia, c1, c2, c3 FROM notas WHERE alumno_id = ?', (alumno_id,)).fetchall()
        for r in registros: notas_alumno[r['materia']] = {'c1': r['c1'], 'c2': r['c2'], 'c3': r['c3']}
    conn.close()
    
    template = 'notas_ciclo1.html' if session.get('ciclo') == 'Primer Ciclo' else 'notas_ciclo2.html'
    return render_template(template, alumnos=alumnos, alumno_seleccionado=alumno_seleccionado, notas=notas_alumno)

@app.route('/guardar_notas_ciclo1', methods=['POST'])
def guardar_notas():
    alumno_id = request.form.get('alumno_id')
    conn = get_db_connection()
    materias = ['Lengua Española', 'Matemática', 'Ciencias Sociales', 'Ciencias de la Naturaleza', 'Educación Física', 'Formación Integral, Humana y Religiosa', 'Educación Artística', 'Inglés']
    for mat in materias:
        c1, c2, c3 = request.form.get(f'{mat}_fc1'), request.form.get(f'{mat}_fc2'), request.form.get(f'{mat}_fc3')
        existe = conn.execute('SELECT id FROM notas WHERE alumno_id = ? AND materia = ?', (alumno_id, mat)).fetchone()
        if existe: conn.execute('UPDATE notas SET c1=?, c2=?, c3=? WHERE id=?', (c1, c2, c3, existe['id']))
        else: conn.execute('INSERT INTO notas (alumno_id, materia, c1, c2, c3) VALUES (?,?,?,?,?)', (alumno_id, mat, c1, c2, c3))
    conn.commit()
    conn.close()
    return redirect(url_for('notas', alumno_id=alumno_id))

@app.route('/inscripcion', methods=['GET', 'POST'])
def inscripcion():
    if 'username' not in session: return redirect('/')
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute("INSERT INTO alumnos (nombres, apellidos, grado) VALUES (?,?,?)", (request.form['nombres'], request.form['apellidos'], request.form['grado']))
        conn.commit()
        conn.close()
        return "Inscripción exitosa. <a href='/menu'>Volver al menú</a>"
    return render_template('inscripcion.html')

@app.route('/registrar_usuario', methods=['GET', 'POST'])
def registrar_usuario():
    if session.get('rol') != 'oficina': return redirect('/')
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute("INSERT INTO usuarios (username, password, rol, grado, ciclo) VALUES (?,?,?,?,?)",
                     (request.form['username'], request.form['password'], request.form['rol'], request.form.get('grado', 'N/A'), request.form.get('ciclo', 'N/A')))
        conn.commit()
        conn.close()
        return "Usuario creado. <a href='/menu'>Volver al menú</a>"
    return render_template('registrar_usuario.html')

def menu_expedientes():
    if 'username' not in session: return redirect('/')
    conn = get_db_connection()
    grado_usuario = str(session.get('grado', '')).replace("-", "").strip()
    alumnos = conn.execute('SELECT * FROM alumnos').fetchall() if session.get('rol') == 'oficina' else conn.execute('SELECT * FROM alumnos WHERE grado = ?', (grado_usuario,)).fetchall()
    conn.close()
    return render_template('expedientes_viejos.html', alumnos=alumnos)

@app.route('/pagina_busqueda')
def pagina_busqueda():
    if 'username' not in session: return redirect('/')
    # Cambiamos 'busqueda.html' por el nombre real de tu archivo
    return render_template('buscar_estudiante.html')

@app.route('/menu_expedientes')
def menu_expedientes():
    if 'username' not in session: return redirect('/')
    conn = get_db_connection()
    grado_usuario = str(session.get('grado', '')).replace("-", "").strip()
    
    if session.get('rol') == 'oficina':
        alumnos = conn.execute('SELECT * FROM alumnos').fetchall()
    else:
        alumnos = conn.execute('SELECT * FROM alumnos WHERE grado = ?', (grado_usuario,)).fetchall()
    conn.close()
    return render_template('expedientes_viejos.html', alumnos=alumnos)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

from datetime import date

@app.route('/asistencia', methods=['GET', 'POST'])
def asistencia():
    if 'username' not in session: return redirect('/')
    conn = get_db_connection()
    fecha_hoy = date.today().strftime('%Y-%m-%d')
    
    # 1. Determinamos el grado a mostrar
    # Si viene por URL (ej. ?grado=4A) lo toma, si no, usa el de la sesión
    grado_actual = request.args.get('grado', session.get('grado'))

    if request.method == 'POST':
        presentes = request.form.getlist('presente')
        # Buscamos los alumnos del grado seleccionado
        alumnos_curso = conn.execute('SELECT id FROM alumnos WHERE grado = ?', (grado_actual,)).fetchall()
        
        for a in alumnos_curso:
            estado = 'Presente' if str(a['id']) in presentes else 'Ausente'
            conn.execute('INSERT INTO asistencia (alumno_id, fecha, estado) VALUES (?,?,?)', 
                         (a['id'], fecha_hoy, estado))
        conn.commit()
        conn.close()
        return "Asistencia guardada. <a href='/menu'>Volver al menú</a>"

    # 2. Obtenemos alumnos y lista de grados (si es oficina)
    alumnos = conn.execute('SELECT * FROM alumnos WHERE grado = ?', (grado_actual,)).fetchall()
    grados = conn.execute('SELECT DISTINCT grado FROM alumnos').fetchall() if session.get('rol') == 'oficina' else None
    
    conn.close()
    return render_template('asistencia.html', alumnos=alumnos, fecha=fecha_hoy, grado=grado_actual, grados=grados)

@app.route('/reporte_asistencia')
def reporte_asistencia():
    if 'username' not in session: return redirect('/')
    conn = get_db_connection()
    fecha_hoy = date.today().strftime('%Y-%m-%d')
    
    # Traemos los alumnos y sus estados de asistencia de hoy
    query = '''
        SELECT a.nombres, a.apellidos, asis.estado 
        FROM alumnos a
        JOIN asistencia asis ON a.id = asis.alumno_id
        WHERE asis.fecha = ?
    '''
    reporte = conn.execute(query, (fecha_hoy,)).fetchall()
    conn.close()
    
    return render_template('reporte_asistencia.html', reporte=reporte, fecha=fecha_hoy)

if __name__ == '__main__':
    app.run(debug=True)