import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config_email import EMAIL_HOST, EMAIL_HOST_PASSWORD, EMAIL_PORT, EMAIL_HOST_USER
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from Config.database_connection import create_connection
from Controllers.admin_controller import AdminController
from Controllers.profesor_controller import ProfesorController
from Controllers.estudiante_controller import EstudianteController
from Controllers.horario_controller import HorarioController
from Controllers.autenticacion import AutenticacionController
import sqlite3  # O el conector que uses

app = Flask(__name__, template_folder='Views', static_folder='Static')
app.secret_key = 'clave_secreta_gestion_estudiantil_2023'

def get_db_connection():
    conn = sqlite3.connect('tu_base_de_datos.db')
    conn.row_factory = sqlite3.Row
    return conn

# --------------------------
# Manejadores de errores
# --------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error/500.html'), 500

# --------------------------
# Rutas de Autenticación
# --------------------------
@app.route('/')
def home():
    if 'usuario' in session:
        return redirect(url_for('dashboard'))
    return render_template('auth/Home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo')
        contraseña = request.form.get('contraseña')
        rol = request.form.get('rol')

        if not correo or not contraseña or not rol:
            flash("Por favor, completa todos los campos.", "error")
            return redirect(url_for('login'))

        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                tabla = {
                    'admin': 'administradores',
                    'profesor': 'profesores',
                    'estudiante': 'estudiantes',
                    'padre': 'padres'
                }.get(rol)
                if not tabla:
                    flash("Rol no válido.", "error")
                    return redirect(url_for('login'))

                query = f"SELECT * FROM {tabla} WHERE correo = %s"
                cursor.execute(query, (correo,))
                usuario = cursor.fetchone()

                if usuario and check_password_hash(usuario['contraseña'], contraseña):
                    session['usuario'] = {
                        'id': usuario['id'],
                        'nombre': usuario['nombre'],
                        'correo': usuario['correo'],
                        'tipo': rol
                    }
                    flash("Inicio de sesión exitoso.", "success")
                    return redirect(url_for('dashboard'))
                else:
                    flash("Correo o contraseña incorrectos.", "error")
            except Exception as e:
                flash(f"Error al iniciar sesión: {e}", "error")
            finally:
                cursor.close()
                conexion.close()
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        contraseña = request.form.get('contraseña')
        rol = request.form.get('rol')

        if not nombre or not correo or not contraseña or not rol:
            flash("Por favor, completa todos los campos.", "error")
            return redirect(url_for('register'))

        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                contraseña_cifrada = generate_password_hash(contraseña)
                cursor.execute(
                    "INSERT INTO usuarios (nombre, correo, contraseña, rol) VALUES (%s, %s, %s, %s)",
                    (nombre, correo, contraseña_cifrada, rol)
                )
                tabla = {
                    'admin': 'administradores',
                    'profesor': 'profesores',
                    'estudiante': 'estudiantes',
                    'padre': 'padres'
                }.get(rol)
                if not tabla:
                    flash("Rol no válido.", "error")
                    return redirect(url_for('register'))
                cursor.execute(
                    f"INSERT INTO {tabla} (nombre, correo, contraseña) VALUES (%s, %s, %s)",
                    (nombre, correo, contraseña_cifrada)
                )
                conexion.commit()
                flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
                return redirect(url_for('login'))
            except Exception as e:
                flash(f"Error al registrar usuario: {e}", "error")
            finally:
                cursor.close()
                conexion.close()
    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# --------------------------
# Dashboard y rutas por rol
# --------------------------
@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('home'))
    if 'tipo' not in session['usuario']:
        flash("Error en la sesión. Por favor, inicia sesión nuevamente.", "error")
        return redirect(url_for('logout'))
    tipo_usuario = session['usuario']['tipo']
    dashboards = {
        'admin': 'admin_dashboard',
        'profesor': 'profesor_dashboard',
        'estudiante': 'estudiante_dashboard',
        'padre': 'padre_dashboard'
    }
    if tipo_usuario not in dashboards:
        flash("Rol desconocido. Contacta al administrador.", "error")
        return redirect(url_for('home'))
    return redirect(url_for(dashboards[tipo_usuario]))

# --------------------------
# Rutas ADMINISTRADOR
# --------------------------
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'usuario' not in session or session['usuario']['tipo'] != 'admin':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('admin_login'))
    conexion = create_connection()
    try:
        with conexion.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM usuarios")
            total_usuarios = cursor.fetchone()['total']
            cursor.execute("SELECT COUNT(*) AS total FROM materias")
            total_materias = cursor.fetchone()['total']
            cursor.execute("SELECT COUNT(*) AS total FROM horarios")
            total_horarios = cursor.fetchone()['total']
            cursor.execute("SELECT COUNT(*) AS total FROM inscripciones")
            total_inscripciones = cursor.fetchone()['total']
        stats = {
            'total_usuarios': total_usuarios,
            'total_materias': total_materias,
            'total_horarios': total_horarios,
            'total_inscripciones': total_inscripciones
        }
        return render_template('admin/dashboard.html', usuario=session['usuario'], stats=stats)
    except Exception as e:
        app.logger.error(f"Error al cargar el dashboard del administrador: {str(e)}")
        flash("Ocurrió un error al cargar el dashboard.", "error")
        return redirect(url_for('home'))
    finally:
        if conexion:
            conexion.close()

@app.route('/admin/usuarios', methods=['GET'])
def gestionar_usuarios():
    if 'usuario' not in session or session['usuario']['tipo'] != 'admin':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))
    usuarios = AdminController.obtener_usuarios()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@app.route('/admin/agregar_usuario', methods=['GET', 'POST'])
def agregar_usuario():
    if 'usuario' not in session or session['usuario']['tipo'] != 'admin':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        contraseña = request.form.get('contraseña')
        rol = request.form.get('rol')
        if nombre and correo and contraseña and rol:
            success = AdminController.agregar_usuario(nombre, correo, contraseña, rol)
            if success:
                flash("Usuario agregado correctamente.", "success")
                return redirect(url_for('gestionar_usuarios'))
            else:
                flash("Error al agregar el usuario. Verifica los datos.", "error")
        else:
            flash("Por favor, completa todos los campos.", "error")
    return render_template('admin/agregarUsuario.html')

@app.route('/admin/eliminar_usuario/<int:id>', methods=['POST'])
def eliminar_usuario(id):
    if 'usuario' not in session or session['usuario']['tipo'] != 'admin':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))
    exito = AdminController.eliminar_usuario(id)
    if exito:
        flash("Usuario eliminado correctamente.", "success")
    else:
        flash("Error al eliminar el usuario.", "error")
    return redirect(url_for('gestionar_usuarios'))

@app.route('/admin/editar_usuario/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    if 'usuario' not in session or session['usuario']['tipo'] != 'admin':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))
    usuario = AdminController.obtener_usuario_por_id(id)
    if not usuario:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for('gestionar_usuarios'))
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        rol = request.form.get('rol')
        if nombre and correo and rol:
            exito = AdminController.modificar_usuario(id, nombre, correo, rol)
            if exito:
                flash("Usuario actualizado correctamente.", "success")
                return redirect(url_for('gestionar_usuarios'))
            else:
                flash("Error al actualizar el usuario. Verifica los datos.", "error")
        else:
            flash("Por favor, completa todos los campos.", "error")
    return render_template('admin/editarUsuario.html', usuario=usuario)

# Materias
@app.route('/admin/materias', methods=['GET', 'POST'])
def gestionar_materias():
    if 'usuario' not in session or session['usuario']['tipo'] != 'admin':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))
    conexion = create_connection()
    materias = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            if request.method == 'POST':
                nombre_materia = request.form.get('nombre_materia')
                descripcion = request.form.get('descripcion')
                if nombre_materia and descripcion:
                    cursor.execute("INSERT INTO materias (nombre, descripcion) VALUES (%s, %s)", (nombre_materia, descripcion))
                    conexion.commit()
                    flash("Materia agregada correctamente.", "success")
                else:
                    flash("Por favor, completa todos los campos.", "error")
            cursor.execute("SELECT * FROM materias")
            materias = cursor.fetchall()
        except Exception as e:
            flash(f"Error al gestionar materias: {e}", "error")
        finally:
            cursor.close()
            conexion.close()
    return render_template('admin/materias.html', materias=materias)

# Ruta de Horarios para el dashboard del administrador
@app.route('/admin/horarios', methods=['GET', 'POST'])
def gestionar_horarios_admin():
    conexion = create_connection()
    if not conexion:
        return "Error de conexión a la base de datos", 500

    cursor = conexion.cursor(dictionary=True)
    # Obtener datos para los selects
    cursor.execute("SELECT id, nombre FROM estudiantes")
    estudiantes = cursor.fetchall()
    cursor.execute("SELECT id, nombre FROM profesores")
    profesores = cursor.fetchall()
    cursor.execute("SELECT id, nombre FROM materias")
    materias = cursor.fetchall()

    if request.method == 'POST':
        id_estudiante = request.form['id_estudiante']
        id_profesor = request.form['id_profesor']
        id_materia = request.form['id_materia']
        dia_semana = request.form['dia_semana']
        hora_inicio = request.form['hora_inicio']
        hora_fin = request.form['hora_fin']
        try:
            cursor.execute("""
                INSERT INTO horarios (id_estudiante, id_profesor, dia_semana, hora_inicio, hora_fin, id_materia)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_estudiante, id_profesor, dia_semana, hora_inicio, hora_fin, id_materia))
            conexion.commit()
        except Exception as e:
            conexion.rollback()
            return f"Error al guardar el horario: {e}", 500

    # Obtener todos los horarios para mostrar en la tabla
    cursor.execute("""
        SELECT h.id, h.id_estudiante, m.nombre AS materia, h.dia_semana, h.hora_inicio, h.hora_fin
        FROM horarios h
        JOIN materias m ON h.id_materia = m.id
        ORDER BY h.id DESC
    """)
    horarios = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template('admin/horarios.html', estudiantes=estudiantes, profesores=profesores, materias=materias, horarios=horarios)
#Ruta para editar horarios al dasboard del administrador
@app.route('/admin/horarios/editar/<int:id>', methods=['GET', 'POST'])
def editar_horario(id):
    if 'usuario' not in session or session['usuario']['tipo'] != 'admin':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))
    conexion = create_connection()
    horario = None
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            if request.method == 'POST':
                id_estudiante = request.form.get('id_estudiante')
                dia_semana = request.form.get('dia_semana')
                hora_inicio = request.form.get('hora_inicio')
                hora_fin = request.form.get('hora_fin')
                id_materia = request.form.get('id_materia') 
                print("DEBUG FORM:", id_estudiante, dia_semana, hora_inicio, hora_fin, id_materia) 
                if id_estudiante and dia_semana and hora_inicio and hora_fin and id_materia:
                    cursor.execute("""
                        UPDATE horarios
                        SET id_estudiante=%s, dia_semana=%s, hora_inicio=%s, hora_fin=%s, id_materia=%s
                        WHERE id=%s
                    """, (id_estudiante, dia_semana, hora_inicio, hora_fin, id_materia, id))
                    conexion.commit()
                    flash("Horario actualizado correctamente.", "success")
                    return redirect(url_for('gestionar_horarios_admin'))
                else:
                    flash("Por favor, completa todos los campos.", "error")
            else:
                cursor.execute("SELECT * FROM horarios WHERE id=%s", (id,))
                horario = cursor.fetchone()
        except Exception as e:
            flash(f"Error al editar horario: {e}", "error")
        finally:
            cursor.close()
            conexion.close()
    return render_template('admin/editar_horario.html', horario=horario)

@app.route('/admin/horarios/eliminar/<int:id>', methods=['POST'])
def eliminar_horario(id):
    if 'usuario' not in session or session['usuario']['tipo'] != 'admin':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))
    conexion = create_connection()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM horarios WHERE id=%s", (id,))
            conexion.commit()
            flash("Horario eliminado correctamente.", "success")
        except Exception as e:
            flash(f"Error al eliminar horario: {e}", "error")
        finally:
            cursor.close()
            conexion.close()
    return redirect(url_for('gestionar_horarios_admin'))

# Inscripciones
@app.route('/admin/inscripciones', methods=['GET', 'POST'])
def gestionar_inscripciones():
    if 'usuario' not in session or session['usuario']['tipo'] != 'admin':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))
    conexion = create_connection()
    inscripciones = []
    estudiantes = []
    materias = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre, puede_inscribirse FROM estudiantes")
            estudiantes = cursor.fetchall()
            cursor.execute("SELECT id, nombre FROM materias")
            materias = cursor.fetchall()
            cursor.execute("""
                SELECT i.id_estudiante, i.id_materia, e.nombre AS estudiante, m.nombre AS materia
                FROM inscripciones i
                JOIN estudiantes e ON i.id_estudiante = e.id
                JOIN materias m ON i.id_materia = m.id
            """)
            inscripciones = cursor.fetchall()
            if request.method == 'POST':
                id_estudiante = request.form.get('id_estudiante')
                id_materia = request.form.get('id_materia')
                if id_estudiante and id_materia:
                    cursor.execute("INSERT IGNORE INTO inscripciones (id_estudiante, id_materia) VALUES (%s, %s)", (id_estudiante, id_materia))
                    conexion.commit()
                    flash("Inscripción agregada correctamente.", "success")
                    return redirect(url_for('gestionar_inscripciones'))
                else:
                    flash("Selecciona estudiante y materia.", "error")
        except Exception as e:
            flash(f"Error al gestionar inscripciones: {e}", "error")
        finally:
            cursor.close()
            conexion.close()
    # CREA LOS DICCIONARIOS Y PASALOS AL TEMPLATE
    estudiantes_dict = {e['id']: e for e in estudiantes}
    materias_dict = {m['id']: m for m in materias}
    return render_template(
        'admin/inscripciones.html',
        inscripciones=inscripciones,
        estudiantes=estudiantes,
        materias=materias,
        estudiantes_dict=estudiantes_dict,
        materias_dict=materias_dict
    )

@app.route('/admin/inscripciones/eliminar', methods=['POST'])
def eliminar_inscripcion():
    if 'usuario' not in session or session['usuario']['tipo'] != 'admin':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))
    id_estudiante = request.form.get('id_estudiante')
    id_materia = request.form.get('id_materia')
    conexion = create_connection()
    if conexion and id_estudiante and id_materia:
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM inscripciones WHERE id_estudiante=%s AND id_materia=%s", (id_estudiante, id_materia))
            conexion.commit()
            flash("Inscripción eliminada correctamente.", "success")
        except Exception as e:
            flash(f"Error al eliminar inscripción: {e}", "error")
        finally:
            cursor.close()
            conexion.close()
    return redirect(url_for('gestionar_inscripciones'))

@app.route('/admin/inscripciones/habilitar_estudiante', methods=['POST'])
def habilitar_estudiante_inscripcion():
    if 'usuario' not in session or session['usuario']['tipo'] != 'admin':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))
    id_estudiante = request.form.get('id_estudiante')
    puede = request.form.get('puede_inscribirse') == '1'
    conexion = create_connection()
    if conexion and id_estudiante:
        try:
            cursor = conexion.cursor()
            cursor.execute("UPDATE estudiantes SET puede_inscribirse=%s WHERE id=%s", (puede, id_estudiante))
            conexion.commit()
            flash("Permiso de inscripción actualizado.", "success")
        except Exception as e:
            flash(f"Error al actualizar permiso: {e}", "error")
        finally:
            cursor.close()
            conexion.close()
    return redirect(url_for('gestionar_inscripciones'))

@app.route('/admin/inscripciones/modificar', methods=['POST'])
def modificar_inscripcion():
    if 'usuario' not in session or session['usuario']['tipo'] != 'admin':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))

    id_estudiante = request.form.get('id_estudiante')
    id_materia = request.form.get('id_materia')
    nuevo_id_estudiante = request.form.get('nuevo_id_estudiante')
    nuevo_id_materia = request.form.get('nuevo_id_materia')

    conexion = create_connection()
    if conexion and id_estudiante and id_materia and nuevo_id_estudiante and nuevo_id_materia:
        try:
            cursor = conexion.cursor()
            # Eliminar la inscripción anterior
            cursor.execute("DELETE FROM inscripciones WHERE id_estudiante=%s AND id_materia=%s", (id_estudiante, id_materia))
            # Insertar la nueva inscripción
            cursor.execute("INSERT INTO inscripciones (id_estudiante, id_materia) VALUES (%s, %s)", (nuevo_id_estudiante, nuevo_id_materia))
            conexion.commit()
            flash("Inscripción modificada correctamente.", "success")
        except Exception as e:
            flash(f"Error al modificar inscripción: {e}", "error")
        finally:
            cursor.close()
            conexion.close()
    else:
        flash("Datos incompletos para modificar inscripción.", "error")
    return redirect(url_for('gestionar_inscripciones'))

# Asignación de padres a estudiantes
@app.route('/admin/asignar_padre', methods=['GET', 'POST'])
def asignar_padre():
    conexion = create_connection()
    estudiantes = []
    padres = []
    mensaje_exito = None
    mensaje_error = None

    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute('SELECT id, nombre FROM estudiantes')
        estudiantes = cursor.fetchall()
        cursor.execute('SELECT id, nombre FROM padres')
        padres = cursor.fetchall()

        if request.method == 'POST':
            id_estudiante = request.form['id_estudiante']
            id_padre = request.form['id_padre']
            cursor.execute(
                'SELECT 1 FROM padres_estudiantes WHERE id_estudiante = %s AND id_padre = %s',
                (id_estudiante, id_padre)
            )
            existe = cursor.fetchone()
            if existe:
                mensaje_error = '¡Ya existe esta asignación!'
            else:
                cursor.execute(
                    'INSERT INTO padres_estudiantes (id_padre, id_estudiante) VALUES (%s, %s)',
                    (id_padre, id_estudiante)
                )
                conexion.commit()
                mensaje_exito = '¡Padre asignado correctamente!'
        cursor.close()
        conexion.close()
    return render_template(
        'admin/asignar_padre.html',
        estudiantes=estudiantes,
        padres=padres,
        mensaje_exito=mensaje_exito,
        mensaje_error=mensaje_error
    )

# --------------------------
# Rutas PROFESOR
# --------------------------
@app.route('/profesor/dashboard')
def profesor_dashboard():
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))

    id_profesor = session['usuario']['id']

    conexion = create_connection()
    estudiantes_por_materia = []
    promedios_por_materia = []
    if conexion:
        cursor = conexion.cursor()
        # Cantidad de estudiantes por materia (corrigiendo el WHERE)
        cursor.execute("""
            SELECT m.nombre, COUNT(DISTINCT n.id_estudiante)
            FROM materias m
            JOIN notas n ON n.id_materia = m.id
            WHERE n.id_profesor = %s
            GROUP BY m.nombre
        """, (id_profesor,))
        estudiantes_por_materia = cursor.fetchall()

        # Promedio de notas por materia (corrigiendo el WHERE)
        cursor.execute("""
            SELECT m.nombre, AVG(n.nota)
            FROM materias m
            JOIN notas n ON n.id_materia = m.id
            WHERE n.id_profesor = %s
            GROUP BY m.nombre
        """, (id_profesor,))
        promedios_por_materia = cursor.fetchall()
        cursor.close()
        conexion.close()

    # Prepara los datos para las gráficas
    labels = [row[0] for row in estudiantes_por_materia]
    data_estudiantes = [row[1] for row in estudiantes_por_materia]
    data_promedios = [float(row[1]) if row[1] is not None else 0 for row in promedios_por_materia]

    return render_template(
        'profesor/dashboard.html',
        labels=labels,
        data_estudiantes=data_estudiantes,
        data_promedios=data_promedios,
        usuario=session['usuario']
    )

@app.route('/profesor/obtener_estudiantes', methods=['GET', 'POST'])
def obtener_estudiantes():
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))

    materias = ProfesorController.obtener_materias()
    estudiantes = []
    id_materia = None

    if request.method == 'POST':
        id_materia = request.form.get('id_materia')
        if id_materia:
            estudiantes = ProfesorController.obtener_estudiantes_por_materia(id_materia)
        else:
            flash("Por favor, selecciona una materia.", "error")

    return render_template(
        'profesor/obtener_estudiantes.html',
        materias=materias,
        estudiantes=estudiantes,
        id_materia=id_materia,
        usuario=session['usuario']
    )

@app.route('/profesor/asignar_nota', methods=['GET', 'POST'])
def asignar_nota():
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))

    materias = ProfesorController.obtener_materias()
    estudiantes = []
    id_materia = None

    if request.method == 'POST':
        id_materia = request.form.get('id_materia')
        notas = request.form.getlist('nota[]')
        comentarios = request.form.getlist('comentario[]')
        ids_estudiantes = request.form.getlist('id_estudiante[]')
        id_profesor = session['usuario']['id']

        # Si se seleccionó materia pero no hay notas, mostrar estudiantes
        if id_materia and not notas:
            estudiantes = ProfesorController.obtener_estudiantes_por_materia(id_materia)
        # Si hay notas, procesar asignación
        elif notas and comentarios and ids_estudiantes and id_materia:
            for i in range(len(ids_estudiantes)):
                ProfesorController.asignar_nota(
                    ids_estudiantes[i],
                    id_profesor,
                    id_materia,
                    notas[i],
                    comentarios[i]
                )
            flash("Notas asignadas correctamente.", "success")
            return redirect(url_for('asignar_nota'))
        else:
            flash("Por favor, selecciona una materia.", "error")

    return render_template('profesor/asignarNota.html', usuario=session['usuario'], materias=materias, estudiantes=estudiantes, id_materia=id_materia)

@app.route('/profesor/cambiar_nota', methods=['GET', 'POST'])
def cambiar_nota():
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))
    materias = ProfesorController.obtener_materias()
    estudiantes = []
    if request.method == 'POST':
        id_materia = request.form.get('id_materia')
        ids_estudiantes = request.form.getlist('id_estudiante[]')
        nuevas_notas = request.form.getlist('nueva_nota[]')
        comentarios = request.form.getlist('comentario[]')
        id_profesor = session['usuario']['id']

        if ids_estudiantes and nuevas_notas and comentarios:
            for i in range(len(ids_estudiantes)):
                ProfesorController.cambiar_nota(
                    ids_estudiantes[i],
                    id_materia,
                    nuevas_notas[i],
                    comentarios[i],
                    id_profesor
                )
            flash("Notas y comentarios actualizados correctamente.", "success")
            return redirect(url_for('cambiar_nota'))
        elif id_materia:
            estudiantes = ProfesorController.obtener_estudiantes_por_materia(id_materia)
        else:
            flash("Por favor, selecciona una materia.", "error")

    return render_template('profesor/cambiarNota.html', materias=materias, estudiantes=estudiantes)


@app.route('/profesor/enviar_notificacion', methods=['GET', 'POST'])
def enviar_notificacion():
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))

    if request.method == 'POST':
        nombre_estudiante = request.form.get('nombre_estudiante')
        nombre_padre = request.form.get('nombre_padre')
        correo_padre = request.form.get('correo_padre')
        comentario = request.form.get('comentario')

        if nombre_estudiante and nombre_padre and correo_padre and comentario:
            asunto = f"Notificación sobre {nombre_estudiante}"
            mensaje = f"Estimado/a {nombre_padre},\n\n{comentario}\n\nAtentamente,\nEl profesor"
            try:
                msg = MIMEMultipart()
                msg['From'] = EMAIL_HOST_USER
                msg['To'] = correo_padre
                msg['Subject'] = asunto
                msg.attach(MIMEText(mensaje, 'plain'))

                server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
                server.starttls()
                server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
                server.sendmail(EMAIL_HOST_USER, correo_padre, msg.as_string())
                server.quit()
                flash("Correo enviado correctamente.", "success")
            except Exception as e:
                flash(f"Error al enviar correo: {e}", "error")
        else:
            flash("Completa todos los campos.", "error")
        return redirect(url_for('enviar_notificacion'))

    return render_template('profesor/enviarNotificacion.html')

# --------------------------
# Rutas ESTUDIANTE
# --------------------------
@app.route('/estudiante/dashboard')
def estudiante_dashboard():
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        return redirect(url_for('home'))
    try:
        conexion = create_connection()
        if not conexion:
            flash("Error de conexión con la base de datos", "error")
            return render_template('estudiante/dashboard.html', usuario=session['usuario'])
        with conexion.cursor(dictionary=True) as cursor:
            notificaciones = []
            cursor.execute("SHOW TABLES LIKE 'notificaciones'")
            if cursor.fetchone():
                cursor.execute("SHOW COLUMNS FROM notificaciones LIKE 'mensaje'")
                if cursor.fetchone():
                    cursor.execute("""
                        SELECT mensaje, fecha 
                        FROM notificaciones 
                        WHERE id_estudiante = %s
                        ORDER BY fecha DESC
                        LIMIT 5
                    """, (session['usuario']['id'],))
                    notificaciones = cursor.fetchall()
            materias = []
            cursor.execute("SHOW TABLES LIKE 'inscripciones'")
            if cursor.fetchone():
                cursor.execute("""
                    SELECT m.id, m.nombre 
                    FROM inscripciones i
                    JOIN materias m ON i.id_materia = m.id
                    WHERE i.id_estudiante = %s
                """, (session['usuario']['id'],))
                materias = cursor.fetchall()
            # OBTENER ÚLTIMO COMENTARIO
            cursor.execute("""
                SELECT n.comentario, m.nombre AS materia, p.nombre AS profesor
                FROM notas n
                JOIN materias m ON n.id_materia = m.id
                JOIN profesores p ON n.id_profesor = p.id
                WHERE n.id_estudiante = %s AND n.comentario IS NOT NULL AND n.comentario != ''
                ORDER BY n.id DESC
                LIMIT 1
            """, (session['usuario']['id'],))
            comentarios = cursor.fetchall()
            estadisticas = []
            try:
                cursor.execute("""
                    SELECT m.nombre AS materia, 
                           ROUND(AVG(n.nota), 2) AS promedio
                    FROM inscripciones i
                    JOIN materias m ON i.id_materia = m.id
                    LEFT JOIN notas n ON n.id_materia = m.id AND n.id_estudiante = i.id_estudiante
                    WHERE i.id_estudiante = %s
                    GROUP BY m.id
                """, (session['usuario']['id'],))
                estadisticas = cursor.fetchall()
            except Exception as e:
                estadisticas = []
            return render_template(
                'estudiante/dashboard.html',
                usuario=session['usuario'],
                notificaciones=notificaciones,
                materias=materias,
                comentarios=comentarios,
                estadisticas=estadisticas
            )
    except Exception as e:
        app.logger.error(f"Error en estudiante dashboard: {str(e)}")
        flash("Ocurrió un error al cargar el dashboard", "error")
        return render_template('estudiante/dashboard.html', usuario=session['usuario'])
    finally:
        if 'conexion' in locals() and conexion:
            conexion.close()

@app.route('/estudiante/ver_notas')
def ver_notas():
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))
    usuario = session['usuario']
    conexion = create_connection()
    notas = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            query = """
                SELECT m.nombre AS materia, 
                       p.nombre AS profesor, 
                       n.nota
                FROM notas n
                JOIN materias m ON n.id_materia = m.id
                LEFT JOIN profesores p ON n.id_profesor = p.id
                WHERE n.id_estudiante = %s
            """
            cursor.execute(query, (usuario['id'],))
            notas = cursor.fetchall()
        except Exception as e:
            flash(f"Error al obtener las notas: {e}", "error")
        finally:
            cursor.close()
            conexion.close()
    return render_template('estudiante/ver_notas.html', usuario=usuario, notas=notas)

@app.route('/estudiante/ver_clases')
def ver_clases():
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))
    usuario = session['usuario']
    conexion = create_connection()
    horario = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            query = """
                SELECT h.dia_semana, h.hora_inicio, h.hora_fin, m.nombre AS materia, p.nombre AS profesor
                FROM horarios h
                JOIN materias m ON h.id_materia = m.id
                LEFT JOIN profesores p ON h.id_profesor = p.id
                WHERE h.id_estudiante = %s
                ORDER BY FIELD(h.dia_semana, 'Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'), h.hora_inicio
            """
            cursor.execute(query, (usuario['id'],))
            horario = cursor.fetchall()
        except Exception as e:
            flash(f"Error al obtener el horario: {e}", "error")
        finally:
            cursor.close()
            conexion.close()
    return render_template('estudiante/ver_clases.html', usuario=usuario, horario=horario)

@app.route('/estudiante/horario')
def horario_estudiante():
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))
    usuario = session['usuario']
    conexion = create_connection()
    horario = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            query = """
                SELECT h.dia_semana, h.hora_inicio, h.hora_fin, m.nombre AS materia, p.nombre AS profesor
                FROM horarios h
                JOIN materias m ON h.id_materia = m.id
                LEFT JOIN profesores p ON h.id_profesor = p.id
                WHERE h.id_estudiante = %s
                ORDER BY FIELD(h.dia_semana, 'Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'), h.hora_inicio
            """
            cursor.execute(query, (usuario['id'],))
            horario = cursor.fetchall()
        except Exception as e:
            flash(f"Error al obtener el horario: {e}", "error")
        finally:
            cursor.close()
            conexion.close()
    return render_template('estudiante/horario.html', usuario=usuario, horario=horario)
# --------------------------
# Rutas PADRE
# --------------------------
@app.route('/padre/dashboard')
def padre_dashboard():
    if 'usuario' not in session or session['usuario']['tipo'] != 'padre':
        return redirect(url_for('home'))
    try:
        conexion = create_connection()
        if not conexion:
            flash("Error de conexión con la base de datos", "error")
            return render_template('padre/dashboard.html', usuario=session['usuario'])
        with conexion.cursor(dictionary=True) as cursor:
            estudiantes = []
            cursor.execute("SHOW TABLES LIKE 'padres_estudiantes'")
            if cursor.fetchone():
                cursor.execute("""
                    SELECT e.id, e.nombre 
                    FROM padres_estudiantes pe
                    JOIN estudiantes e ON pe.id_estudiante = e.id
                    WHERE pe.id_padre = %s
                """, (session['usuario']['id'],))
                estudiantes = cursor.fetchall()
            return render_template('padre/dashboard.html', usuario=session['usuario'], estudiantes=estudiantes)
    except Exception as e:
        app.logger.error(f"Error en padre dashboard: {str(e)}")
        flash("Ocurrió un error al cargar el dashboard", "error")
        return render_template('padre/dashboard.html', usuario=session['usuario'])
    finally:
        if 'conexion' in locals() and conexion:
            conexion.close()

@app.route('/padre/hijos')
def ver_hijos():
    if 'usuario' not in session or session['usuario']['tipo'] != 'padre':
        return redirect(url_for('home'))
    padre_id = session['usuario']['id']
    conexion = create_connection()
    hijos = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT e.nombre
                FROM padres_estudiantes pe
                JOIN estudiantes e ON pe.id_estudiante = e.id
                WHERE pe.id_padre = %s
            """, (padre_id,))
            hijos = cursor.fetchall()
        except Exception as e:
            hijos = []
        finally:
            cursor.close()
            conexion.close()
    return render_template('padre/ver_hijos.html', hijos=hijos)

@app.route('/ver_horarios')
def ver_horarios():
    if 'usuario' not in session or session['usuario']['tipo'] != 'padre':
        return redirect(url_for('home'))
    padre_id = session['usuario']['id']
    conexion = create_connection()
    materias_por_estudiante = {}
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            # 1. Obtener los hijos del padre
            cursor.execute("""
                SELECT e.id, e.nombre
                FROM padres_estudiantes pe
                JOIN estudiantes e ON pe.id_estudiante = e.id
                WHERE pe.id_padre = %s
            """, (padre_id,))
            estudiantes = cursor.fetchall()
            if estudiantes:
                for estudiante in estudiantes:
                    # 2. Obtener materias inscritas de cada hijo
                    cursor.execute("""
                        SELECT m.id, m.nombre, m.descripcion
                        FROM inscripciones i
                        JOIN materias m ON i.id_materia = m.id
                        WHERE i.id_estudiante = %s
                    """, (estudiante['id'],))
                    materias = cursor.fetchall()
                    materias_por_estudiante[estudiante['nombre']] = materias
        except Exception as e:
            materias_por_estudiante = {}
        finally:
            cursor.close()
            conexion.close()
    return render_template('padre/ver_horarios.html', materias_por_estudiante=materias_por_estudiante)


@app.route('/padre/ver_descripcion')
def ver_descripcion():
    if 'usuario' not in session or session['usuario']['tipo'] != 'padre':
        return redirect(url_for('home'))
    padre_id = session['usuario']['id']
    conexion = create_connection()
    notas = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            # Obtener los hijos del padre
            cursor.execute("""
                SELECT e.id, e.nombre
                FROM padres_estudiantes pe
                JOIN estudiantes e ON pe.id_estudiante = e.id
                WHERE pe.id_padre = %s
            """, (padre_id,))
            estudiantes = cursor.fetchall()
            if estudiantes:
                for estudiante in estudiantes:
                    # Obtener notas y comentarios de cada hijo
                    cursor.execute("""
                        SELECT m.nombre AS nombre_materia, n.nota, n.comentario, %s AS nombre_estudiante
                        FROM notas n
                        JOIN materias m ON n.id_materia = m.id
                        WHERE n.id_estudiante = %s
                    """, (estudiante['nombre'], estudiante['id']))
                    notas += cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()
    return render_template('padre/ver_descripcion.html', notas=notas)
# --------------------------
# Main
# --------------------------
if __name__ == '__main__':
    app.run(debug=True)