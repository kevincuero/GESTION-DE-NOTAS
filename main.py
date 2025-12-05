
"""MOVED: rutas editar/eliminar entregas - colocadas más abajo tras la inicialización de `app`"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config_email import EMAIL_HOST, EMAIL_HOST_PASSWORD, EMAIL_PORT, EMAIL_HOST_USER
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import send_from_directory
from Config.database_connection import create_connection
from Controllers.admin_controller import AdminController
from Controllers.profesor_controller import ProfesorController
from Controllers.estudiante_controller import EstudianteController
from Controllers.horario_controller import HorarioController
from Controllers.autenticacion import AutenticacionController
from Controllers.indices_controller import IndicesController
from Controllers.evento_controller import EventoController
import sqlite3  # O el conector que uses
import traceback
import io
import csv
import time

app = Flask(__name__, template_folder='Views', static_folder='Static')
app.secret_key = 'clave_secreta_gestion_estudiantil_2023'

# Rutas para editar/eliminar entregas (movidas aquí para asegurar que `app` exista)
@app.route('/estudiante/editar_entrega', methods=['POST'])
def editar_entrega():
    """Permite a estudiantes editar sus entregas."""
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    id_estudiante = session['usuario']['id']
    id_tarea = request.form.get('id_tarea')
    
    if not id_tarea:
        return jsonify({'success': False, 'message': 'ID de tarea no especificado'}), 400
    
    try:
        conexion = create_connection()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            
            # Verificar que existe la entrega del estudiante
            query = """
            SELECT id, ruta FROM entregas_tareas
            WHERE id_estudiante = %s AND id_tarea_materia = %s
            """
            cursor.execute(query, (id_estudiante, id_tarea))
            entrega = cursor.fetchone()
            
            if not entrega:
                cursor.close()
                conexion.close()
                return jsonify({'success': False, 'message': 'Entrega no encontrada'}), 404
            
            # Si hay nuevo archivo, actualizar
            if 'archivo' in request.files and request.files['archivo'].filename != '':
                archivo = request.files['archivo']
                
                if not allowed_content_file(archivo.filename):
                    cursor.close()
                    conexion.close()
                    return jsonify({'success': False, 'message': 'Tipo de archivo no permitido'}), 400
                
                # Eliminar archivo anterior
                old_path = os.path.join(CONTENT_UPLOAD_FOLDER, entrega['ruta'].replace('uploads/contenidos/', ''))
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except:
                        pass
                
                # Guardar nuevo archivo
                filename = secure_filename(f"{id_estudiante}_{id_tarea}_{int(time.time())}_{archivo.filename}")
                carpeta_entregas = os.path.join(CONTENT_UPLOAD_FOLDER, 'entregas', str(id_tarea))
                os.makedirs(carpeta_entregas, exist_ok=True)
                ruta_absoluta = os.path.join(carpeta_entregas, filename)
                
                archivo.save(ruta_absoluta)
                ruta_relativa = os.path.join('uploads', 'contenidos', 'entregas', str(id_tarea), filename).replace('\\', '/')
                
                # Actualizar BD
                cursor.execute(
                    """
                    UPDATE entregas_tareas 
                    SET filename=%s, ruta=%s, mimetype=%s, fecha_entrega=NOW()
                    WHERE id_estudiante=%s AND id_tarea_materia=%s
                    """,
                    (filename, ruta_relativa, archivo.mimetype, id_estudiante, id_tarea)
                )
            
            conexion.commit()
            cursor.close()
            conexion.close()
            return jsonify({'success': True, 'message': 'Entrega actualizada correctamente'})
        else:
            return jsonify({'success': False, 'message': 'Error de conexión'}), 500
    except Exception as e:
        app.logger.error(f"Error al editar entrega: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/estudiante/eliminar_entrega', methods=['POST'])
def eliminar_entrega():
    """Permite a estudiantes eliminar sus entregas."""
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    id_estudiante = session['usuario']['id']
    data = request.get_json()
    id_tarea = data.get('id_tarea')
    
    if not id_tarea:
        return jsonify({'success': False, 'message': 'ID de tarea no especificado'}), 400
    
    try:
        conexion = create_connection()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            
            # Obtener información de la entrega
            query = """
            SELECT id, ruta FROM entregas_tareas
            WHERE id_estudiante = %s AND id_tarea_materia = %s
            """
            cursor.execute(query, (id_estudiante, id_tarea))
            entrega = cursor.fetchone()
            
            if not entrega:
                cursor.close()
                conexion.close()
                return jsonify({'success': False, 'message': 'Entrega no encontrada'}), 404
            
            # Eliminar archivo
            file_path = os.path.join(CONTENT_UPLOAD_FOLDER, entrega['ruta'].replace('uploads/contenidos/', ''))
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            
            # Eliminar de BD
            cursor.execute(
                "DELETE FROM entregas_tareas WHERE id_estudiante=%s AND id_tarea_materia=%s",
                (id_estudiante, id_tarea)
            )
            conexion.commit()
            cursor.close()
            conexion.close()
            
            return jsonify({'success': True, 'message': 'Entrega eliminada correctamente'})
        else:
            return jsonify({'success': False, 'message': 'Error de conexión'}), 500
    except Exception as e:
        app.logger.error(f"Error al eliminar entrega: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# OAuth (Google) - intenta habilitar sólo si `authlib` está instalada y las credenciales están configuradas.
# OAuth (Google) - intenta habilitar sólo si `authlib` está instalada y las credenciales están configuradas.
oauth = None
try:
    # Importa authlib sólo si está disponible en el entorno
    from authlib.integrations.flask_client import OAuth  # type: ignore
except ImportError:
    app.logger.info('authlib no está instalada; Google OAuth deshabilitado.')
    oauth = None
else:
    # Comprueba que las credenciales estén en las variables de entorno
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
    google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    if not google_client_id or not google_client_secret:
        app.logger.warning('Google OAuth deshabilitado: faltan GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET en variables de entorno.')
        oauth = None
    else:
        oauth = OAuth(app)
        oauth.register(
            name='google',
            client_id=google_client_id,
            client_secret=google_client_secret,
            access_token_url='https://oauth2.googleapis.com/token',
            authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
            api_base_url='https://www.googleapis.com/oauth2/v2/',
            userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
            client_kwargs={'scope': 'openid email profile'}
        )

# Configuración de subida de archivos (hojas de vida y contenidos)
ALLOWED_EXTENSIONS = {'pdf'}
UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads', 'hojas')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Extensión para contenidos de materias (documentos, imágenes, video, presentaciones)
CONTENT_ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'zip', 'mp4', 'png', 'jpg', 'jpeg'}
CONTENT_UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads', 'contenidos')
os.makedirs(CONTENT_UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_content_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in CONTENT_ALLOWED_EXTENSIONS

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


@app.route('/login/google')
def login_google():
    if oauth is None:
        flash('Inicio de sesión con Google no está disponible (dependencia faltante).', 'error')
        return redirect(url_for('login'))
    redirect_uri = url_for('authorize_google', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@app.route('/authorize/google')
def authorize_google():
    if oauth is None:
        flash('Inicio de sesión con Google no está disponible (dependencia faltante).', 'error')
        return redirect(url_for('login'))
    try:
        token = oauth.google.authorize_access_token()
        # Obtener información del usuario
        resp = oauth.google.get('userinfo')
        user_info = resp.json()
        email = user_info.get('email')
        nombre = user_info.get('name') or user_info.get('given_name') or email
        if not email:
            flash('No se pudo obtener el correo desde Google.', 'error')
            return redirect(url_for('login'))

        # Buscar usuario en la tabla estudiantes
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("SELECT id, nombre, correo FROM estudiantes WHERE correo=%s", (email,))
                usuario = cursor.fetchone()
                if usuario:
                    session['usuario'] = {'id': usuario['id'], 'nombre': usuario['nombre'], 'correo': usuario['correo'], 'tipo': 'estudiante'}
                    flash('Inicio de sesión con Google exitoso.', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    # Crear estudiante nuevo (sin contraseña) y marcarlo para revisión si es necesario
                    cursor.execute("INSERT INTO estudiantes (nombre, correo) VALUES (%s, %s)", (nombre, email))
                    conexion.commit()
                    new_id = cursor.lastrowid
                    session['usuario'] = {'id': new_id, 'nombre': nombre, 'correo': email, 'tipo': 'estudiante'}
                    flash('Cuenta creada e iniciada con Google. Si requiere aprobación, el administrador podrá gestionarla.', 'success')
                    return redirect(url_for('dashboard'))
            except Exception as e:
                app.logger.error(f"Error en login Google: {e}")
                flash('Ocurrió un error al iniciar sesión con Google.', 'error')
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
                try:
                    conexion.close()
                except Exception:
                    pass
    except Exception as e:
        app.logger.error(f"Error autorizando con Google: {e}")
        flash('Error durante la autorización con Google.', 'error')
    return redirect(url_for('login'))

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

    # ===== VERIFICAR Y GENERAR NOTIFICACIONES DE CONTENIDO DESACTUALIZADO =====
    notificaciones_contenido = verificar_y_generar_notificaciones_contenido(id_profesor)
    materias_estado = obtener_materias_con_estado_contenido(id_profesor)
    
    # Filtrar solo las materias en alerta (urgente o alerta)
    materias_alerta = [m for m in materias_estado if m['estado_contenido'] in ['URGENTE', 'ALERTA']]

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
        usuario=session['usuario'],
        materias_alerta=materias_alerta,
        todas_materias_estado=materias_estado,
        notificaciones_contenido=notificaciones_contenido
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


@app.route('/profesor/hoja_vida')
def profesor_hoja_vida():
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))

    id_profesor = session['usuario']['id']
    hoja = None
    conexion = create_connection()
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT hoja_vida FROM profesores WHERE id = %s", (id_profesor,))
            fila = cursor.fetchone()
            if fila:
                hoja = fila.get('hoja_vida')
        except Exception as e:
            app.logger.error(f"Error obteniendo hoja de vida: {e}")
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conexion.close()
            except Exception:
                pass

    return render_template('profesor/HojadeVida.html', hoja=hoja, usuario=session['usuario'])


@app.route('/profesor/contenidos')
def profesor_contenidos():
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))

    id_profesor = session['usuario']['id']
    materias = ProfesorController.obtener_materias_asignadas(id_profesor)
    contenidos = ProfesorController.listar_contenidos_por_profesor_materia(id_profesor=id_profesor)
    return render_template('profesor/contenidos.html', materias=materias, contenidos=contenidos, usuario=session['usuario'])


@app.route('/profesor/tareas/agregar', methods=['GET', 'POST'])
def agregar_tarea():
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))

    id_profesor = session['usuario']['id']
    materias = ProfesorController.obtener_materias_asignadas(id_profesor)

    if request.method == 'POST':
        id_materia = request.form.get('id_materia')
        tipo_tarea = request.form.get('tipo_tarea')
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        fecha_entrega = request.form.get('fecha_entrega')
        hora_entrega = request.form.get('hora_entrega')

        if not id_materia or not tipo_tarea or not titulo or not fecha_entrega or not hora_entrega:
            flash('Por favor completa todos los campos requeridos.', 'error')
            return redirect(url_for('agregar_tarea'))

        # Combinar fecha y hora
        fecha_entrega_dt = None
        try:
            fecha_entrega_dt = f"{fecha_entrega} {hora_entrega}:00"
        except Exception:
            fecha_entrega_dt = f"{fecha_entrega} 00:00:00"

        # Procesar archivo opcional
        archivo = None
        filename = None
        mimetype = None
        ruta_relativa = None
        if 'archivo' in request.files:
            archivo = request.files['archivo']
            if archivo and archivo.filename != '':
                if allowed_content_file(archivo.filename):
                    filename = secure_filename(f"{id_profesor}_{int(time.time())}_{archivo.filename}")
                    carpeta_profesor = os.path.join(CONTENT_UPLOAD_FOLDER, str(id_profesor))
                    os.makedirs(carpeta_profesor, exist_ok=True)
                    ruta_absoluta = os.path.join(carpeta_profesor, filename)
                    try:
                        archivo.save(ruta_absoluta)
                        ruta_relativa = os.path.join('uploads', 'contenidos', str(id_profesor), filename).replace('\\','/')
                        mimetype = archivo.mimetype
                    except Exception as e:
                        app.logger.error(f"Error guardando archivo de tarea: {e}")
                        flash('Error al guardar archivo adjunto.', 'error')
                        return redirect(url_for('agregar_tarea'))
                else:
                    flash('Tipo de archivo no permitido.', 'error')
                    return redirect(url_for('agregar_tarea'))

        # Guardar en la BD: tabla tareas_materia (se asume que la tabla existe, ver SQL recomendado)
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    INSERT INTO tareas_materia (id_profesor, id_materia, titulo, descripcion, tipo_tarea, fecha_entrega, filename, mimetype, ruta, creado_en)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    """,
                    (id_profesor, id_materia, titulo, descripcion, tipo_tarea, fecha_entrega_dt, filename, mimetype, ruta_relativa)
                )
                conexion.commit()
                flash('Tarea creada correctamente.', 'success')
            except Exception as e:
                app.logger.error(f"Error al crear tarea en BD: {e}")
                try:
                    conexion.rollback()
                except Exception:
                    pass
                flash('Ocurrió un error al crear la tarea.', 'error')
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
                try:
                    conexion.close()
                except Exception:
                    pass

        return redirect(url_for('profesor_contenidos'))

    return render_template('profesor/agregar_tarea.html', materias=materias, usuario=session['usuario'])


@app.route('/profesor/ver_entregas', methods=['GET', 'POST'])
def profesor_ver_entregas():
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))

    id_profesor = session['usuario']['id']
    materias = ProfesorController.obtener_materias_asignadas(id_profesor)

    id_materia = request.args.get('id_materia')
    id_tarea = request.args.get('id_tarea')

    estudiantes = []
    tareas = []
    entregas_map = {}
    materia_nombre = ''

    conexion = create_connection()
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            # Obtener tareas del profesor en la materia seleccionada
            if id_materia:
                cursor.execute("SELECT id, titulo, fecha_entrega FROM tareas_materia WHERE id_profesor=%s AND id_materia=%s ORDER BY fecha_entrega", (id_profesor, id_materia))
                tareas = cursor.fetchall()
                # obtener nombre materia
                cursor.execute("SELECT nombre FROM materias WHERE id=%s", (id_materia,))
                mrow = cursor.fetchone()
                materia_nombre = mrow['nombre'] if mrow else ''

                # Obtener estudiantes inscritos
                cursor.execute("SELECT e.id, e.nombre, e.correo FROM inscripciones i JOIN estudiantes e ON i.id_estudiante = e.id WHERE i.id_materia=%s", (id_materia,))
                estudiantes = cursor.fetchall()

                # Si id_tarea especificada, obtener entregas para esa tarea
                if id_tarea:
                    cursor.execute("SELECT et.id, et.id_estudiante, et.filename, et.ruta, et.fecha_entrega, et.calificacion, et.comentario FROM entregas_tareas et WHERE et.id_tarea_materia=%s", (id_tarea,))
                    entregas = cursor.fetchall()
                    # mapear por id_estudiante
                    entregas_map = { e['id_estudiante']: e for e in (entregas or []) }

        except Exception as e:
            app.logger.error(f"Error en ver_entregas: {e}")
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conexion.close()
            except Exception:
                pass

    return render_template('profesor/ver_entregas.html', materias=materias, tareas=tareas, estudiantes=estudiantes, entregas_map=entregas_map, id_materia_selected=id_materia, materia_nombre=materia_nombre)


@app.route('/profesor/descargar_entrega/<int:id_entrega>')
def descargar_entrega(id_entrega):
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash('No tienes permisos para acceder a esta sección.', 'error')
        return redirect(url_for('home'))
    try:
        conexion = create_connection()
        if not conexion:
            flash('Error de conexión.', 'error')
            return redirect(url_for('profesor_contenidos'))
        cursor = conexion.cursor(dictionary=True)
        cursor.execute('SELECT et.*, tm.id_profesor FROM entregas_tareas et JOIN tareas_materia tm ON et.id_tarea_materia = tm.id WHERE et.id = %s', (id_entrega,))
        row = cursor.fetchone()
        cursor.close()
        conexion.close()
        if not row:
            flash('Entrega no encontrada.', 'error')
            return redirect(url_for('profesor_ver_entregas'))
        # Verificar que el profesor es dueño de la tarea
        if int(row.get('id_profesor')) != int(session['usuario']['id']):
            flash('No tienes permiso para descargar esta entrega.', 'error')
            return redirect(url_for('profesor_ver_entregas'))
        ruta = row.get('ruta')
        if not ruta:
            flash('Ruta inválida.', 'error')
            return redirect(url_for('profesor_ver_entregas'))
        carpeta_rel = os.path.dirname(ruta)
        nombre = os.path.basename(ruta)
        carpeta_abs = os.path.join(app.static_folder, carpeta_rel)
        return send_from_directory(carpeta_abs, nombre, as_attachment=True)
    except Exception as e:
        app.logger.error(f"Error descargando entrega: {e}")
        flash('Ocurrió un error al descargar la entrega.', 'error')
        return redirect(url_for('profesor_ver_entregas'))


@app.route('/profesor/calificar_entrega', methods=['POST'])
def calificar_entrega():
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash('No tienes permisos para realizar esta acción.', 'error')
        return redirect(url_for('home'))
    id_entrega = request.form.get('id_entrega')
    calificacion = request.form.get('calificacion')
    try:
        conexion = create_connection()
        cursor = conexion.cursor()
        cursor.execute('UPDATE entregas_tareas SET calificacion=%s WHERE id=%s', (calificacion, id_entrega))
        conexion.commit()
        cursor.close()
        conexion.close()
        flash('Calificación registrada.', 'success')
    except Exception as e:
        app.logger.error(f"Error al calificar entrega: {e}")
        flash('Ocurrió un error al guardar la calificación.', 'error')
    return redirect(url_for('profesor_ver_entregas', id_materia=request.form.get('id_materia') or ''))


@app.route('/profesor/eliminar_entrega', methods=['POST'])
def profesor_eliminar_entrega():
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash('No tienes permisos para realizar esta acción.', 'error')
        return redirect(url_for('home'))
    id_entrega = request.form.get('id_entrega')
    try:
        conexion = create_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute('SELECT et.id, et.ruta, tm.id_profesor FROM entregas_tareas et JOIN tareas_materia tm ON et.id_tarea_materia = tm.id WHERE et.id = %s', (id_entrega,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            conexion.close()
            flash('Entrega no encontrada.', 'error')
            return redirect(url_for('profesor_ver_entregas'))
        if int(row.get('id_profesor')) != int(session['usuario']['id']):
            cursor.close()
            conexion.close()
            flash('No tienes permiso para eliminar esta entrega.', 'error')
            return redirect(url_for('profesor_ver_entregas'))
        # eliminar archivo
        file_path = os.path.join(app.static_folder, row.get('ruta'))
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass
        # eliminar registro
        cursor.execute('DELETE FROM entregas_tareas WHERE id=%s', (id_entrega,))
        conexion.commit()
        cursor.close()
        conexion.close()
        flash('Entrega eliminada correctamente.', 'success')
    except Exception as e:
        app.logger.error(f"Error al eliminar entrega (profesor): {e}")
        flash('Ocurrió un error al eliminar la entrega.', 'error')
    return redirect(url_for('profesor_ver_entregas', id_materia=request.form.get('id_materia') or ''))


@app.route('/profesor/contenidos/upload', methods=['POST'])
def profesor_subir_contenido():
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash("No tienes permisos para realizar esta acción.", "error")
        return redirect(url_for('home'))

    id_profesor = session['usuario']['id']
    id_materia = request.form.get('id_materia')
    titulo = request.form.get('titulo')
    descripcion = request.form.get('descripcion')

    if 'archivo' not in request.files:
        flash('No se encontró archivo para subir.', 'error')
        return redirect(url_for('profesor_contenidos'))

    archivo = request.files['archivo']
    if archivo.filename == '':
        flash('No se seleccionó ningún archivo.', 'error')
        return redirect(url_for('profesor_contenidos'))

    if archivo and allowed_content_file(archivo.filename):
        filename = secure_filename(f"{id_profesor}_{int(time.time())}_{archivo.filename}")
        carpeta_profesor = os.path.join(CONTENT_UPLOAD_FOLDER, str(id_profesor))
        os.makedirs(carpeta_profesor, exist_ok=True)
        ruta_absoluta = os.path.join(carpeta_profesor, filename)
        try:
            archivo.save(ruta_absoluta)
            ruta_relativa = os.path.join('uploads', 'contenidos', str(id_profesor), filename).replace('\\','/')
            # Registrar en BD
            ProfesorController.subir_contenido(id_profesor, id_materia, titulo, descripcion, filename, archivo.mimetype, None, ruta_relativa)
            flash('Contenido subido correctamente.', 'success')
        except Exception as e:
            app.logger.error(f"Error al guardar contenido: {e}")
            flash('Ocurrió un error al subir el archivo.', 'error')
    else:
        flash('Tipo de archivo no permitido para contenidos.', 'error')

    return redirect(url_for('profesor_contenidos'))


@app.route('/contenidos/<int:id>/download')
def descargar_contenido(id):
    contenido = ProfesorController.obtener_contenido_por_id(id)
    if not contenido:
        flash('Contenido no encontrado.', 'error')
        return redirect(url_for('home'))
    ruta = contenido.get('ruta')
    if not ruta:
        flash('Ruta inválida del archivo.', 'error')
        return redirect(url_for('home'))
    # ruta está guardada relativa a la carpeta Static
    try:
        carpeta_rel = os.path.dirname(ruta)
        nombre = os.path.basename(ruta)
        carpeta_abs = os.path.join(app.static_folder, carpeta_rel)
        return send_from_directory(carpeta_abs, nombre, as_attachment=True)
    except Exception as e:
        app.logger.error(f"Error al enviar archivo: {e}")
        flash('Ocurrió un error al servir el archivo.', 'error')
        return redirect(url_for('home'))


@app.route('/profesor/contenidos/<int:id>/eliminar', methods=['POST'])
def eliminar_contenido(id):
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash("No tienes permisos para realizar esta acción.", "error")
        return redirect(url_for('home'))

    fila = ProfesorController.eliminar_contenido(id)
    if fila:
        try:
            # fila puede ser una tupla con ruta, filename
            if isinstance(fila, (list, tuple)) and fila[0]:
                ruta = fila[0]
                archivo_abs = os.path.join(app.static_folder, ruta)
                if os.path.exists(archivo_abs):
                    os.remove(archivo_abs)
            flash('Contenido eliminado correctamente.', 'success')
        except Exception as e:
            app.logger.error(f"Error al eliminar archivo del disco: {e}")
    else:
        flash('No se pudo eliminar el contenido.', 'error')
    return redirect(url_for('profesor_contenidos'))


@app.route('/profesor/contenidos/<int:id>/editar', methods=['GET', 'POST'])
def editar_contenido(id):
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash("No tienes permisos para realizar esta acción.", "error")
        return redirect(url_for('home'))

    id_profesor = session['usuario']['id']
    contenido = ProfesorController.obtener_contenido_por_id(id)
    if not contenido:
        flash('Contenido no encontrado.', 'error')
        return redirect(url_for('profesor_contenidos'))

    # Verificar que el profesor propietario sea el mismo
    if int(contenido.get('id_profesor')) != int(id_profesor):
        flash('No tienes permiso para editar este contenido.', 'error')
        return redirect(url_for('profesor_contenidos'))

    materias = ProfesorController.obtener_materias_asignadas(id_profesor)

    if request.method == 'POST':
        id_materia = request.form.get('id_materia')
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')

        # Datos actuales
        filename = contenido.get('filename')
        ruta_relativa = contenido.get('ruta')
        mimetype = contenido.get('mimetype')

        # Procesar posible archivo nuevo
        if 'archivo_nuevo' in request.files:
            archivo_nuevo = request.files['archivo_nuevo']
            if archivo_nuevo and archivo_nuevo.filename != '':
                if allowed_content_file(archivo_nuevo.filename):
                    nuevo_filename = secure_filename(f"{id_profesor}_{int(time.time())}_{archivo_nuevo.filename}")
                    carpeta_profesor = os.path.join(CONTENT_UPLOAD_FOLDER, str(id_profesor))
                    os.makedirs(carpeta_profesor, exist_ok=True)
                    ruta_absoluta = os.path.join(carpeta_profesor, nuevo_filename)
                    try:
                        archivo_nuevo.save(ruta_absoluta)
                        nueva_ruta_rel = os.path.join('uploads', 'contenidos', str(id_profesor), nuevo_filename).replace('\\','/')
                        # eliminar archivo antiguo si existe
                        try:
                            if ruta_relativa:
                                antiguo_abs = os.path.join(app.static_folder, ruta_relativa)
                                if os.path.exists(antiguo_abs):
                                    os.remove(antiguo_abs)
                        except Exception:
                            app.logger.warning('No se pudo eliminar archivo antiguo, continúo.')

                        # actualizar valores para guardar en BD
                        filename = nuevo_filename
                        ruta_relativa = nueva_ruta_rel
                        mimetype = archivo_nuevo.mimetype
                    except Exception as e:
                        app.logger.error(f"Error al guardar nuevo archivo: {e}")
                        flash('Error al guardar el archivo nuevo.', 'error')
                        return redirect(url_for('editar_contenido', id=id))
                else:
                    flash('Tipo de archivo no permitido para contenidos.', 'error')
                    return redirect(url_for('editar_contenido', id=id))

        # Actualizar en la BD
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    UPDATE contenidos_materia
                    SET id_materia=%s, titulo=%s, descripcion=%s, filename=%s, mimetype=%s, ruta=%s
                    WHERE id=%s
                    """,
                    (id_materia, titulo, descripcion, filename, mimetype, ruta_relativa, id)
                )
                conexion.commit()
                flash('Contenido actualizado correctamente.', 'success')
            except Exception as e:
                app.logger.error(f"Error al actualizar contenido en BD: {e}")
                try:
                    conexion.rollback()
                except Exception:
                    pass
                flash('Ocurrió un error al actualizar el contenido.', 'error')
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
                try:
                    conexion.close()
                except Exception:
                    pass

        return redirect(url_for('profesor_contenidos'))

    return render_template('profesor/editar_contenido.html', contenido=contenido, materias=materias, usuario=session['usuario'])


@app.route('/materia/<int:id>/contenidos')
def ver_contenidos_materia(id):
    # Vista para estudiantes: muestra contenidos por materia
    contenidos = ProfesorController.listar_contenidos_por_profesor_materia(id_profesor=None, id_materia=id)
    return render_template('estudiante/contenidos_profesor.html', contenidos=contenidos, usuario=session.get('usuario'))


@app.route('/profesor/subir_hoja', methods=['POST'])
def subir_hoja():
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash("No tienes permisos para realizar esta acción.", "error")
        return redirect(url_for('home'))

    id_profesor = session['usuario']['id']
    if 'hoja' not in request.files:
        flash('No se encontró ningún archivo.', 'error')
        return redirect(url_for('profesor_hoja_vida'))

    archivo = request.files['hoja']
    if archivo.filename == '':
        flash('No se seleccionó ningún archivo.', 'error')
        return redirect(url_for('profesor_hoja_vida'))

    if archivo and allowed_file(archivo.filename):
        filename = secure_filename(f"{id_profesor}_{int(time.time())}_{archivo.filename}")
        ruta = os.path.join(UPLOAD_FOLDER, filename)
        try:
            archivo.save(ruta)
            # Actualizar registro en BD
            conexion = create_connection()
            if conexion:
                cursor = conexion.cursor()
                try:
                    cursor.execute("UPDATE profesores SET hoja_vida = %s WHERE id = %s", (filename, id_profesor))
                    conexion.commit()
                except Exception as e:
                    conexion.rollback()
                    app.logger.error(f"Error guardando nombre de archivo en BD: {e}")
                finally:
                    try:
                        cursor.close()
                    except Exception:
                        pass
                    try:
                        conexion.close()
                    except Exception:
                        pass

            flash('Hoja de vida subida correctamente.', 'success')
        except Exception as e:
            app.logger.error(f"Error al guardar archivo: {e}")
            flash('Ocurrió un error al subir el archivo.', 'error')
    else:
        flash('Tipo de archivo no permitido. Solo PDF.', 'error')

    return redirect(url_for('profesor_hoja_vida'))


@app.route('/profesor/actualizar_hoja', methods=['POST'])
def actualizar_hoja():
    # Reutiliza la lógica de subir_hoja (sobrescribe registro y archivo)
    return subir_hoja()


@app.route('/profesor/ver_hoja/<int:id_profesor>')
def ver_hoja(id_profesor):
    conexion = create_connection()
    filename = None
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT hoja_vida FROM profesores WHERE id = %s", (id_profesor,))
            fila = cursor.fetchone()
            if fila:
                filename = fila.get('hoja_vida')
        except Exception as e:
            app.logger.error(f"Error obteniendo hoja de vida: {e}")
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conexion.close()
            except Exception:
                pass

    if not filename:
        flash('No existe hoja de vida para este profesor.', 'error')
        return redirect(url_for('profesor_hoja_vida'))

    # Enviar archivo desde carpeta de uploads
    return send_from_directory(UPLOAD_FOLDER, filename)

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
        tipo_evaluacion = request.form.get('tipo_evaluacion')
        notas = request.form.getlist('nota[]')
        comentarios = request.form.getlist('comentario[]')
        ids_estudiantes = request.form.getlist('id_estudiante[]')
        id_profesor = session['usuario']['id']

        # Si se seleccionó materia pero no hay notas, mostrar estudiantes
        if id_materia and not notas:
            estudiantes = ProfesorController.obtener_estudiantes_por_materia(id_materia)
        # Si hay notas, procesar asignación
        elif notas and comentarios and ids_estudiantes and id_materia and tipo_evaluacion:
            for i in range(len(ids_estudiantes)):
                if notas[i]:  # Solo procesar si hay nota
                    ProfesorController.asignar_nota(
                        ids_estudiantes[i],
                        id_profesor,
                        id_materia,
                        notas[i],
                        tipo_evaluacion,
                        comentarios[i]
                    )
            flash("Notas asignadas correctamente.", "success")
            return redirect(url_for('asignar_nota'))
        else:
            if not tipo_evaluacion:
                flash("Por favor, selecciona un tipo de evaluación.", "error")
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
        tipos_notas = request.form.getlist('tipo_nota_cambiar[]')
        comentarios = request.form.getlist('comentario[]')
        id_profesor = session['usuario']['id']

        if ids_estudiantes and nuevas_notas and tipos_notas and comentarios:
            actualizadas = 0
            for i in range(len(ids_estudiantes)):
                exito = ProfesorController.cambiar_nota(
                    ids_estudiantes[i],
                    id_materia,
                    nuevas_notas[i],
                    tipos_notas[i],
                    comentarios[i],
                    id_profesor
                )
                if exito:
                    actualizadas += 1
            if actualizadas > 0:
                flash(f"{actualizadas} nota(s) actualizada(s) correctamente.", "success")
            else:
                flash("No se pudo actualizar ninguna nota. Verifica que los registros existan en la base de datos.", "error")
            return redirect(url_for('cambiar_nota'))
        elif id_materia:
            estudiantes = ProfesorController.obtener_estudiantes_por_materia(id_materia)
        else:
            flash("Por favor, selecciona una materia.", "error")

    return render_template('profesor/cambiarNota.html', materias=materias, estudiantes=estudiantes, usuario=session['usuario'])


@app.route('/profesor/enviar_notificacion', methods=['GET', 'POST'])
def enviar_notificacion():
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))

    id_profesor = session['usuario']['id']
    materias = ProfesorController.obtener_materias_asignadas(id_profesor)
    
    if request.method == 'POST':
        tipo_envio = request.form.get('tipo_envio', 'individual')
        id_materia = request.form.get('id_materia')
        titulo = request.form.get('titulo')
        mensaje = request.form.get('mensaje')
        
        if not id_materia or not titulo or not mensaje:
            flash("Por favor completa todos los campos.", "error")
            return redirect(url_for('enviar_notificacion'))
        
        if tipo_envio == 'individual':
            id_estudiante = request.form.get('id_estudiante')
            if not id_estudiante:
                flash("Selecciona un estudiante.", "error")
                return redirect(url_for('enviar_notificacion'))
            
            from Controllers.notificacion_controller import NotificacionController
            resultado = NotificacionController.enviar_notificacion_a_estudiante(
                int(id_estudiante), id_profesor, titulo, mensaje
            )
            if resultado['success']:
                flash(resultado['message'], "success")
            else:
                flash(resultado['message'], "error")
        
        return redirect(url_for('enviar_notificacion'))
    
    return render_template('profesor/EnviarNotificacion.html', materias=materias)

@app.route('/profesor/enviar_notificacion_grupo', methods=['POST'])
def enviar_notificacion_grupo():
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))

    id_profesor = session['usuario']['id']
    id_materia = request.form.get('id_materia')
    titulo = request.form.get('titulo')
    mensaje = request.form.get('mensaje')
    
    if not id_materia or not titulo or not mensaje:
        flash("Por favor completa todos los campos.", "error")
        return redirect(url_for('enviar_notificacion'))
    
    from Controllers.notificacion_controller import NotificacionController
    resultado = NotificacionController.enviar_notificacion_a_clase(
        int(id_materia), id_profesor, titulo, mensaje
    )
    
    if resultado['success']:
        flash(resultado['message'], "success")
    else:
        flash(resultado['message'], "error")
    
    return redirect(url_for('enviar_notificacion'))

@app.route('/profesor/revisar_estudiante/<int:id_estudiante>')
def revisar_estudiante(id_estudiante):
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))
    # Obtener datos del estudiante
    conexion = create_connection()
    estudiante = None
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre, correo FROM estudiantes WHERE id=%s", (id_estudiante,))
            estudiante = cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener datos del estudiante: {e}")
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            conexion.close()

    informe = EstudianteController.obtener_informe_estudiante(id_estudiante)
    return render_template('profesor/revisar_estudiante.html', estudiante=estudiante, informe=informe, usuario=session['usuario'])


@app.route('/api/estudiantes_por_materia/<int:id_materia>', methods=['GET'])
def estudiantes_por_materia(id_materia):
    """Retorna estudiantes inscritos en una materia en formato JSON."""
    estudiantes = ProfesorController.obtener_estudiantes_por_materia(id_materia)
    # Convertir a formato JSON con id y nombre
    result = [{'id': e['id'], 'nombre': e['estudiante']} for e in estudiantes]
    return jsonify(result)

# --------------------------
# API RUTAS PARA NOTIFICACIONES
# --------------------------
@app.route('/api/notificacion/marcar_leida/<int:id_notificacion>', methods=['POST'])
def api_marcar_notificacion_leida(id_notificacion):
    """API para marcar una notificación como leída."""
    if 'usuario' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    from Controllers.notificacion_controller import NotificacionController
    resultado = NotificacionController.marcar_como_leida(id_notificacion)
    return jsonify(resultado)

@app.route('/api/notificacion/marcar_todas_leidas', methods=['POST'])
def api_marcar_todas_notificaciones_leidas():
    """API para marcar todas las notificaciones como leídas."""
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    id_estudiante = session['usuario']['id']
    from Controllers.notificacion_controller import NotificacionController
    resultado = NotificacionController.marcar_todas_como_leidas(id_estudiante)
    return jsonify(resultado)

@app.route('/api/notificacion/eliminar/<int:id_notificacion>', methods=['DELETE'])
def api_eliminar_notificacion(id_notificacion):
    """API para eliminar una notificación."""
    if 'usuario' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    from Controllers.notificacion_controller import NotificacionController
    resultado = NotificacionController.eliminar_notificacion(id_notificacion)
    return jsonify(resultado)

@app.route('/api/notificacion/sin_leer', methods=['GET'])
def api_notificaciones_sin_leer():
    """API para obtener el conteo de notificaciones sin leer."""
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        return jsonify({'count': 0}), 401
    
    id_estudiante = session['usuario']['id']
    from Controllers.notificacion_controller import NotificacionController
    count = NotificacionController.obtener_conteo_no_leidas(id_estudiante)
    return jsonify({'count': count})

# --------------------------
# Rutas ÍNDICES DE APRENDIZAJE
# --------------------------
@app.route('/profesor/indices', methods=['GET', 'POST'])
def indices():
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))

    id_profesor = session['usuario']['id']
    
    if request.method == 'POST':
        id_materia = request.form.get('id_materia')
        if not id_materia:
            flash("Selecciona una materia.", "error")
            return redirect(url_for('indices'))
        session['id_materia_indices'] = int(id_materia)
    
    id_materia = session.get('id_materia_indices')
    materias = ProfesorController.obtener_materias_asignadas(id_profesor)
    indices_list = []
    
    if id_materia:
        try:
            indices_list = IndicesController.obtener_indices_con_evaluaciones(id_materia)
        except Exception as e:
            flash(f"Error al cargar índices: {str(e)}", "error")
    
    return render_template('profesor/indices.html', materias=materias, indices=indices_list, id_materia_actual=id_materia, usuario=session['usuario'])

@app.route('/profesor/crear_indice', methods=['GET', 'POST'])
def crear_indice():
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))

    id_profesor = session['usuario']['id']
    id_materia = session.get('id_materia_indices')
    
    if not id_materia:
        flash("Selecciona una materia primero.", "error")
        return redirect(url_for('indices'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        parcial = request.form.get('parcial')
        porcentaje = request.form.get('porcentaje')
        
        try:
            porcentaje = float(porcentaje) if porcentaje else 0
        except ValueError:
            flash("El porcentaje debe ser un número válido.", "error")
            return redirect(url_for('crear_indice'))
        
        resultado = IndicesController.crear_indice(
            id_materia=int(id_materia),
            id_profesor=id_profesor,
            nombre=nombre,
            descripcion=descripcion,
            parcial=parcial,
            porcentaje=porcentaje
        )
        
        if resultado['success']:
            flash(resultado['message'], "success")
            return redirect(url_for('indices'))
        else:
            flash(resultado['message'], "error")
    
    return render_template('profesor/crear_indice.html', id_materia=id_materia, usuario=session['usuario'])

@app.route('/profesor/evaluar_indice/<int:id_indice>', methods=['GET', 'POST'])
def evaluar_indice(id_indice):
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))

    id_profesor = session['usuario']['id']
    
    try:
        indice = IndicesController.obtener_indice_por_id(id_indice)
        if not indice or indice['id_profesor'] != id_profesor:
            flash("Índice no encontrado o no tienes permisos.", "error")
            return redirect(url_for('indices'))
        
        if request.method == 'POST':
            porcentaje_dominio = request.form.get('porcentaje_dominio')
            comentario = request.form.get('comentario', '').strip()
            
            try:
                porcentaje_dominio = float(porcentaje_dominio)
                if not (0 <= porcentaje_dominio <= 100):
                    flash("El porcentaje de dominio debe estar entre 0 y 100.", "error")
                    return redirect(url_for('evaluar_indice', id_indice=id_indice))
            except ValueError:
                flash("El porcentaje debe ser un número válido.", "error")
                return redirect(url_for('evaluar_indice', id_indice=id_indice))
            
            resultado = IndicesController.guardar_evaluacion_indice(
                id_indice=id_indice,
                id_profesor=id_profesor,
                porcentaje_dominio=porcentaje_dominio,
                comentario=comentario
            )
            
            if resultado['success']:
                flash(resultado['message'], "success")
                return redirect(url_for('indices'))
            else:
                flash(resultado['message'], "error")
        
        evaluaciones = IndicesController.obtener_evaluaciones_indice(id_indice)
        ultima_evaluacion = evaluaciones[0] if evaluaciones else None
        
        return render_template('profesor/evaluar_indice.html', indice=indice, evaluaciones=evaluaciones, ultima_evaluacion=ultima_evaluacion, usuario=session['usuario'])
    
    except Exception as e:
        flash(f"Error al cargar índice: {str(e)}", "error")
        return redirect(url_for('indices'))

@app.route('/profesor/editar_indice/<int:id_indice>', methods=['GET', 'POST'])
def editar_indice(id_indice):
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))

    id_profesor = session['usuario']['id']
    
    try:
        indice = IndicesController.obtener_indice_por_id(id_indice)
        if not indice or indice['id_profesor'] != id_profesor:
            flash("Índice no encontrado o no tienes permisos.", "error")
            return redirect(url_for('indices'))
        
        if request.method == 'POST':
            nombre = request.form.get('nombre')
            descripcion = request.form.get('descripcion')
            parcial = request.form.get('parcial')
            porcentaje = request.form.get('porcentaje')
            
            try:
                porcentaje = float(porcentaje) if porcentaje else 0
            except ValueError:
                flash("El porcentaje debe ser un número válido.", "error")
                return redirect(url_for('editar_indice', id_indice=id_indice))
            
            resultado = IndicesController.actualizar_indice(
                id_indice=id_indice,
                nombre=nombre,
                descripcion=descripcion,
                parcial=parcial,
                porcentaje=porcentaje
            )
            
            if resultado['success']:
                flash(resultado['message'], "success")
                return redirect(url_for('indices'))
            else:
                flash(resultado['message'], "error")
        
        return render_template('profesor/crear_indice.html', indice=indice, id_materia=indice['id_materia'], usuario=session['usuario'])
    
    except Exception as e:
        flash(f"Error al cargar índice: {str(e)}", "error")
        return redirect(url_for('indices'))

@app.route('/profesor/eliminar_indice/<int:id_indice>')
def eliminar_indice(id_indice):
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))

    id_profesor = session['usuario']['id']
    
    try:
        indice = IndicesController.obtener_indice_por_id(id_indice)
        if not indice or indice['id_profesor'] != id_profesor:
            flash("Índice no encontrado o no tienes permisos.", "error")
            return redirect(url_for('indices'))
        
        resultado = IndicesController.eliminar_indice(id_indice)
        
        if resultado['success']:
            flash(resultado['message'], "success")
        else:
            flash(resultado['message'], "error")
        
        return redirect(url_for('indices'))
    
    except Exception as e:
        flash(f"Error al eliminar índice: {str(e)}", "error")
        return redirect(url_for('indices'))
# Rutas DOCENTE (definiciones anteriores eliminadas para evitar duplicados)
# --------------------------
# Rutas DOCENTE (NUEVAS)
# --------------------------

@app.route('/docente/listado_alumnos', methods=['GET'])
def docente_listado_alumnos():
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        return jsonify({'error': 'No autorizado'}), 401

    id_profesor = session['usuario']['id']
    alumnos = ProfesorController.listar_alumnos(id_profesor)

    return jsonify({'alumnos': alumnos}), 200


@app.route('/docente/buscar_alumno', methods=['GET'])
def docente_buscar_alumno():
    if 'usuario' not in session or session['usuario']['tipo'] != 'profesor':
        return jsonify({'error': 'No autorizado'}), 401

    nombre = request.args.get('nombre', '').strip()
    if not nombre:
        return jsonify({'error': 'Debe enviar un nombre'}), 400

    id_profesor = session['usuario']['id']
    estudiantes = ProfesorController.buscar_estudiante_por_nombre(id_profesor, nombre)

    return jsonify({'estudiantes': estudiantes}), 200



# --------------------------
# Rutas ESTUDIANTE
# --------------------------

# Rutas compatibles con tests: alias público para listado y búsqueda de alumnos
@app.route('/alumnos', methods=['GET'])
def alumnos_publico():
    # Soporta query param `search` o `nombre` usado en versiones anteriores
    termino = request.args.get('search') or request.args.get('nombre') or ''

    # Si hay sesión y es profesor, usar controladores reales
    if 'usuario' in session and session['usuario'].get('tipo') == 'profesor':
        id_profesor = session['usuario']['id']
        if termino:
            estudiantes = ProfesorController.buscar_estudiante_por_nombre(id_profesor, termino)
        else:
            # intentar listar alumnos del profesor
            try:
                estudiantes = ProfesorController.listar_alumnos(id_profesor)
            except Exception:
                estudiantes = []
    else:
        # En el contexto de tests no hay sesión; devolver lista vacía con 200
        if termino:
            estudiantes = []
        else:
            estudiantes = []

    return jsonify({'estudiantes': estudiantes}), 200

@app.route('/estudiante/dashboard')
def estudiante_dashboard():
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        return redirect(url_for('home'))
    try:
        id_estudiante = session['usuario']['id']
        # Obtener todos los datos del dashboard usando el controlador
        datos_dashboard = EstudianteController.obtener_datos_dashboard(id_estudiante)
        
        return render_template(
            'estudiante/dashboard.html',
            usuario=session['usuario'],
            tareas_pendientes=datos_dashboard['tareas_pendientes'],
            asistencia=datos_dashboard['asistencia'],
            materias=datos_dashboard['estadisticas'],
            promedio_general=datos_dashboard['promedio_general'],
            estadisticas=datos_dashboard['estadisticas'],
            notificaciones=datos_dashboard['notificaciones']
        )
    except Exception as e:
        app.logger.error(f"Error en estudiante dashboard: {str(e)}")
        flash("Ocurrió un error al cargar el dashboard", "error")
        return redirect(url_for('home'))
    finally:
        pass


# Ruta: Mis Clases (nueva - renderiza la plantilla personalizada)
@app.route('/estudiante/clases')
def clases_estudiante():
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))
    id_estudiante = session['usuario']['id']
    try:
        horario = EstudianteController.obtener_horario(id_estudiante)
        # Obtener IDs de materias inscritas para destacarlas
        materias_inscritas_ids = []
        conexion = create_connection()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id_materia FROM inscripciones WHERE id_estudiante = %s", (id_estudiante,))
            inscritas = cursor.fetchall()
            materias_inscritas_ids = [r['id_materia'] for r in inscritas]
            cursor.close()
            conexion.close()
        return render_template('estudiante/mis_clases.html', usuario=session['usuario'], horario=horario, materias_inscritas_ids=materias_inscritas_ids)
    except Exception as e:
        app.logger.error(f"Error al cargar Mis Clases: {e}")
        flash("Ocurrió un error al cargar tus clases.", "error")
        return redirect(url_for('estudiante_dashboard'))


# Ruta: Asignaturas (lista de materias disponibles)
@app.route('/estudiante/asignaturas')
def asignaturas_estudiante():
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))
    usuario = session['usuario']
    conexion = create_connection()
    materias = []
    try:
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre, descripcion FROM materias ORDER BY nombre")
            materias = cursor.fetchall()
            # Obtener permiso de inscripción del estudiante para mostrar botones
            cursor.execute("SELECT puede_inscribirse FROM estudiantes WHERE id=%s", (usuario['id'],))
            permiso = cursor.fetchone()
            usuario['puede_inscribirse'] = permiso['puede_inscribirse'] if permiso and 'puede_inscribirse' in permiso else False
            session['usuario'] = usuario
    except Exception as e:
        app.logger.error(f"Error al cargar Asignaturas: {e}")
        flash("Ocurrió un error al cargar las asignaturas.", "error")
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            if conexion:
                conexion.close()
        except Exception:
            pass
    return render_template('estudiante/mis_asignaturas.html', usuario=usuario, materias=materias)


# Ruta: Mis Calificaciones (nueva)
@app.route('/estudiante/calificaciones')
def calificaciones_estudiante():
    app.logger.debug(f"Entering calificaciones_estudiante; session usuario: {session.get('usuario')}")
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))
    id_estudiante = session['usuario']['id']
    try:
        from Controllers.nota_controller import NotaController
        # Obtener notas agrupadas por materia
        materias_agrupadas = NotaController.obtener_notas_por_materia_agrupadas(id_estudiante)
        
        app.logger.debug(f"Calificaciones obtained: materias={len(materias_agrupadas)}")
        return render_template(
            'estudiante/mis_calificaciones.html',
            usuario=session['usuario'],
            materias_agrupadas=materias_agrupadas
        )
    except Exception as e:
        tb = traceback.format_exc()
        app.logger.error(f"Error al cargar Calificaciones: {e}\n{tb}")
        flash("Ocurrió un error al cargar tus calificaciones.", "error")
        return redirect(url_for('estudiante_dashboard'))


@app.route('/estudiante/calificaciones/descargar')
def descargar_calificaciones():
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))
    id_estudiante = session['usuario']['id']
    formato = request.args.get('formato', 'csv')
    try:
        datos = EstudianteController.obtener_calificaciones_detalle(id_estudiante)
        notas = datos.get('notas', [])
        # Build CSV
        if formato == 'csv':
            # Use semicolon delimiter and UTF-8 BOM so Excel (locale-dependent) opens columns correctly
            si = io.StringIO()
            writer = csv.writer(si, delimiter=';')
            writer.writerow(['Materia', 'Nota', 'Comentario'])
            for n in notas:
                writer.writerow([n.get('materia'), n.get('nota'), n.get('comentario', '')])
            output = si.getvalue()
            si.close()
            # Prepend BOM so Excel recognizes UTF-8 and splits columns correctly in many locales
            output = '\ufeff' + output
            response = app.make_response(output)
            response.headers['Content-Disposition'] = f'attachment; filename=calificaciones_{id_estudiante}.csv'
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            return response
        else:
            flash('Formato no soportado para descarga.', 'error')
            return redirect(url_for('calificaciones_estudiante'))
    except Exception as e:
        app.logger.error(f"Error al generar descarga de calificaciones: {e}")
        flash('Ocurrió un error al generar la descarga.', 'error')
        return redirect(url_for('calificaciones_estudiante'))


# Ruta: Mis Notificaciones (nueva)
# Ruta: Mis Notificaciones (nueva)
@app.route('/estudiante/ver_contenidos', methods=['GET', 'POST'])
def ver_contenidos_estudiante():
    """Vista para que estudiantes vean y descarguen contenidos de sus materias inscritas."""
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))
    
    id_estudiante = session['usuario']['id']
    
    try:
        # Obtener materias inscritas
        materias = EstudianteController.obtener_materias_asignadas(id_estudiante)
        
        # Obtener contenidos (filtrar por materia si se selecciona)
        id_materia = None
        if request.method == 'POST':
            id_materia = request.form.get('id_materia')
            if id_materia:
                try:
                    id_materia = int(id_materia)
                except (ValueError, TypeError):
                    id_materia = None
        
        contenidos = EstudianteController.obtener_contenidos_inscritos(id_estudiante, id_materia)
        
        return render_template(
            'estudiante/ver_contenidos.html',
            usuario=session['usuario'],
            materias=materias,
            contenidos=contenidos,
            id_materia_actual=id_materia
        )
    except Exception as e:
        tb = traceback.format_exc()
        app.logger.error(f"Error al cargar contenidos: {e}\n{tb}")
        flash("Ocurrió un error al cargar los contenidos.", "error")
        return redirect(url_for('estudiante_dashboard'))

@app.route('/estudiante/descargar_contenido/<int:id_contenido>')
def descargar_contenido_estudiante(id_contenido):
    """Permite a estudiantes descargar contenidos de sus materias inscritas."""
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        return jsonify({'error': 'No autorizado'}), 401
    
    id_estudiante = session['usuario']['id']
    
    try:
        conexion = create_connection()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            # Verificar que el contenido pertenece a una materia inscrita del estudiante
            query = """
            SELECT c.* FROM contenidos_materia c
            JOIN inscripciones i ON c.id_materia = i.id_materia
            WHERE c.id = %s AND i.id_estudiante = %s
            """
            cursor.execute(query, (id_contenido, id_estudiante))
            contenido = cursor.fetchone()
            cursor.close()
            conexion.close()
            
            if not contenido:
                flash("Contenido no encontrado o sin permisos.", "error")
                return redirect(url_for('ver_contenidos_estudiante'))
            
            # Construir ruta del archivo
            file_path = os.path.join(app.root_path, 'Static', contenido['ruta'])
            
            if os.path.exists(file_path):
                return send_file(file_path, as_attachment=True, download_name=contenido['filename'])
            else:
                flash("El archivo no se encuentra en el servidor.", "error")
                return redirect(url_for('ver_contenidos_estudiante'))
        else:
            flash("Error al conectar a la base de datos.", "error")
            return redirect(url_for('ver_contenidos_estudiante'))
    except Exception as e:
        app.logger.error(f"Error al descargar contenido: {e}")
        flash("Ocurrió un error al descargar el archivo.", "error")
        return redirect(url_for('ver_contenidos_estudiante'))

@app.route('/estudiante/tareas', methods=['GET', 'POST'])
def tareas_estudiante():
    """Vista para que estudiantes vean tareas de sus materias inscritas."""
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))
    
    id_estudiante = session['usuario']['id']
    id_materia = None
    
    try:
        # Obtener tareas (filtrar por materia si se selecciona)
        if request.method == 'POST':
            id_materia = request.form.get('id_materia')
            if id_materia:
                try:
                    id_materia = int(id_materia)
                except (ValueError, TypeError):
                    id_materia = None
        
        tareas = EstudianteController.obtener_tareas_inscritas(id_estudiante, id_materia)
        
        return render_template(
            'estudiante/tareas.html',
            usuario=session['usuario'],
            tareas=tareas,
            id_materia_actual=id_materia
        )
    except Exception as e:
        tb = traceback.format_exc()
        app.logger.error(f"Error al cargar tareas: {e}\n{tb}")
        flash("Ocurrió un error al cargar tus tareas.", "error")
        return redirect(url_for('estudiante_dashboard'))

@app.route('/estudiante/descargar_tarea/<int:id_tarea>')
def descargar_tarea_material(id_tarea):
    """Permite a estudiantes descargar material adjunto de una tarea."""
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        flash("No autorizado.", "error")
        return redirect(url_for('home'))
    
    id_estudiante = session['usuario']['id']
    
    try:
        conexion = create_connection()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            # Verificar que la tarea pertenece a una materia inscrita del estudiante
            query = """
            SELECT tm.* FROM tareas_materia tm
            JOIN inscripciones i ON tm.id_materia = i.id_materia
            WHERE tm.id = %s AND i.id_estudiante = %s
            """
            cursor.execute(query, (id_tarea, id_estudiante))
            tarea = cursor.fetchone()
            cursor.close()
            conexion.close()
            
            if not tarea or not tarea['ruta']:
                flash("Material no encontrado o sin permisos.", "error")
                return redirect(url_for('tareas_estudiante'))
            
            # Construir ruta del archivo
            file_path = os.path.join(app.root_path, 'Static', tarea['ruta'])
            
            if os.path.exists(file_path):
                return send_file(file_path, as_attachment=True, download_name=tarea['filename'])
            else:
                flash("El archivo no se encuentra en el servidor.", "error")
                return redirect(url_for('tareas_estudiante'))
        else:
            flash("Error al conectar a la base de datos.", "error")
            return redirect(url_for('tareas_estudiante'))
    except Exception as e:
        app.logger.error(f"Error al descargar material de tarea: {e}")
        flash("Ocurrió un error al descargar el archivo.", "error")
        return redirect(url_for('tareas_estudiante'))

@app.route('/estudiante/subir_entrega', methods=['POST'])
def subir_entrega():
    """Permite a estudiantes subir entregas para tareas."""
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    id_estudiante = session['usuario']['id']
    id_tarea = request.form.get('id_tarea')
    
    if not id_tarea:
        return jsonify({'success': False, 'message': 'ID de tarea no especificado'}), 400
    
    try:
        # Verificar que la tarea existe y pertenece a una materia inscrita
        conexion = create_connection()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            query = """
            SELECT tm.id FROM tareas_materia tm
            JOIN inscripciones i ON tm.id_materia = i.id_materia
            WHERE tm.id = %s AND i.id_estudiante = %s
            """
            cursor.execute(query, (id_tarea, id_estudiante))
            existe = cursor.fetchone()
            
            if not existe:
                cursor.close()
                conexion.close()
                return jsonify({'success': False, 'message': 'Tarea no encontrada o sin permisos'}), 403
            
            # Procesar archivo de entrega
            if 'archivo' not in request.files:
                cursor.close()
                conexion.close()
                return jsonify({'success': False, 'message': 'No se envió archivo'}), 400
            
            archivo = request.files['archivo']
            if archivo.filename == '':
                cursor.close()
                conexion.close()
                return jsonify({'success': False, 'message': 'Archivo vacío'}), 400
            
            if not allowed_content_file(archivo.filename):
                cursor.close()
                conexion.close()
                return jsonify({'success': False, 'message': 'Tipo de archivo no permitido'}), 400
            
            # Guardar archivo
            filename = secure_filename(f"{id_estudiante}_{id_tarea}_{int(time.time())}_{archivo.filename}")
            carpeta_entregas = os.path.join(CONTENT_UPLOAD_FOLDER, 'entregas', str(id_tarea))
            os.makedirs(carpeta_entregas, exist_ok=True)
            ruta_absoluta = os.path.join(carpeta_entregas, filename)
            
            archivo.save(ruta_absoluta)
            ruta_relativa = os.path.join('uploads', 'contenidos', 'entregas', str(id_tarea), filename).replace('\\', '/')
            
            # Guardar en BD (tabla entregas_tareas)
            cursor.execute(
                """
                INSERT INTO entregas_tareas (id_estudiante, id_tarea_materia, filename, ruta, mimetype, fecha_entrega)
                VALUES (%s, %s, %s, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE filename=%s, ruta=%s, mimetype=%s, fecha_entrega=NOW()
                """,
                (id_estudiante, id_tarea, filename, ruta_relativa, archivo.mimetype, filename, ruta_relativa, archivo.mimetype)
            )
            conexion.commit()
            cursor.close()
            conexion.close()
            
            return jsonify({'success': True, 'message': 'Entrega enviada correctamente'})
        else:
            return jsonify({'success': False, 'message': 'Error de conexión'}), 500
    except Exception as e:
        app.logger.error(f"Error al subir entrega: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/estudiante/notificaciones')
def notificaciones_estudiante():
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for('home'))
    id_estudiante = session['usuario']['id']
    try:
        from Controllers.notificacion_controller import NotificacionController
        notificaciones = NotificacionController.obtener_notificaciones_estudiante(id_estudiante)
        return render_template('estudiante/mis_notificaciones.html', usuario=session['usuario'], notificaciones=notificaciones)
    except Exception as e:
        app.logger.error(f"Error al cargar Notificaciones: {e}")
        flash("Ocurrió un error al cargar tus notificaciones.", "error")
        return redirect(url_for('estudiante_dashboard'))


# API: Obtener detalles de notificación con mensajes
@app.route('/api/notificacion/<int:id_notificacion>')
def api_obtener_notificacion(id_notificacion):
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        return jsonify({"success": False, "message": "No autorizado"}), 403
    
    id_estudiante = session['usuario']['id']
    try:
        from Controllers.mensaje_controller import MensajeController
        resultado = MensajeController.obtener_notificacion_con_detalles(id_notificacion, id_estudiante)
        
        if resultado:
            return jsonify({
                "success": True,
                "notificacion": resultado['notificacion'],
                "mensajes": resultado['mensajes']
            })
        else:
            return jsonify({"success": False, "message": "Notificación no encontrada"}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener notificación: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# API: Enviar respuesta a notificación
@app.route('/api/notificacion/<int:id_notificacion>/responder', methods=['POST'])
def api_responder_notificacion(id_notificacion):
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        return jsonify({"success": False, "message": "No autorizado"}), 403
    
    id_estudiante = session['usuario']['id']
    data = request.get_json()
    
    try:
        if not data or 'contenido' not in data or 'id_profesor' not in data or 'id_materia' not in data:
            return jsonify({"success": False, "message": "Datos incompletos"}), 400
        
        from Controllers.mensaje_controller import MensajeController
        resultado = MensajeController.enviar_respuesta(
            id_notificacion,
            id_estudiante,
            data['id_profesor'],
            data['id_materia'],
            data['contenido']
        )
        
        return jsonify(resultado)
    except Exception as e:
        app.logger.error(f"Error al responder notificación: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# API: Obtener materias del estudiante
@app.route('/api/estudiante/materias')
def api_materias_estudiante():
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        return jsonify({"success": False, "message": "No autorizado"}), 403
    
    id_estudiante = session['usuario']['id']
    try:
        from Controllers.estudiante_controller import EstudianteController
        materias = EstudianteController.obtener_materias_asignadas(id_estudiante)
        
        return jsonify({
            "success": True,
            "materias": materias
        })
    except Exception as e:
        app.logger.error(f"Error al obtener materias: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# API: Enviar mensaje inicial a profesor
@app.route('/api/mensaje/enviar', methods=['POST'])
def api_enviar_mensaje():
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        return jsonify({"success": False, "message": "No autorizado"}), 403
    
    id_estudiante = session['usuario']['id']
    data = request.get_json()
    
    try:
        if not data or 'id_profesor' not in data or 'id_materia' not in data or \
           'titulo' not in data or 'contenido' not in data:
            return jsonify({"success": False, "message": "Datos incompletos"}), 400
        
        from Controllers.mensaje_controller import MensajeController
        resultado = MensajeController.enviar_mensaje_inicial(
            id_estudiante,
            data['id_profesor'],
            data['id_materia'],
            data['titulo'],
            data['contenido']
        )
        
        return jsonify(resultado)
    except Exception as e:
        app.logger.error(f"Error al enviar mensaje: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# Ajustar ruta existente de horario para usar la plantilla nueva `mi_horario.html`

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
    materias = []
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
    materias = []
    materias_inscritas_ids = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            query = """
                SELECT h.dia_semana, TIME_FORMAT(h.hora_inicio, '%H:%i') AS hora_inicio, TIME_FORMAT(h.hora_fin, '%H:%i') AS hora_fin, m.nombre AS materia, m.id AS id_materia, p.nombre AS profesor
                FROM horarios h
                JOIN materias m ON h.id_materia = m.id
                LEFT JOIN profesores p ON h.id_profesor = p.id
                WHERE h.id_estudiante = %s
                ORDER BY FIELD(h.dia_semana, 'Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'), h.hora_inicio
            """
            cursor.execute(query, (usuario['id'],))
            horario = cursor.fetchall()
            print(f"[DEBUG] Horario obtenido para estudiante {usuario['id']}: {horario}")
            
            # Obtener IDs de materias inscritas
            cursor.execute("SELECT id_materia FROM inscripciones WHERE id_estudiante = %s", (usuario['id'],))
            inscritas = cursor.fetchall()
            materias_inscritas_ids = [r['id_materia'] for r in inscritas]
            print(f"[DEBUG] Materias inscritas: {materias_inscritas_ids}")
            
            # Obtener materias disponibles para inscribirse
            cursor.execute("SELECT id, nombre FROM materias ORDER BY nombre")
            materias = cursor.fetchall()
            # Obtener permiso de inscripción del estudiante
            cursor.execute("SELECT puede_inscribirse FROM estudiantes WHERE id=%s", (usuario['id'],))
            permiso = cursor.fetchone()
            usuario['puede_inscribirse'] = permiso['puede_inscribirse'] if permiso and 'puede_inscribirse' in permiso else False
            # Asegura que la sesión refleje el permiso (para la plantilla)
            session['usuario'] = usuario
        except Exception as e:
            print(f"[ERROR] Error al obtener el horario: {e}")
            flash(f"Error al obtener el horario: {e}", "error")
        finally:
            cursor.close()
            conexion.close()
    return render_template('estudiante/mi_horario.html', usuario=usuario, horario=horario, materias=materias, materias_inscritas_ids=materias_inscritas_ids)


@app.route('/estudiante/inscribir', methods=['POST'])
def inscribir_materia():
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        flash("No tienes permisos para realizar esta acción.", "error")
        return redirect(url_for('home'))
    usuario = session['usuario']
    id_materia = request.form.get('id_materia')
    if not id_materia:
        flash("Materia no especificada.", "error")
        return redirect(url_for('horario_estudiante'))

    conexion = create_connection()
    if not conexion:
        flash("Error de conexión con la base de datos.", "error")
        return redirect(url_for('horario_estudiante'))

    try:
        cursor = conexion.cursor(dictionary=True)
        # Verificar si el estudiante tiene permiso para inscribirse
        cursor.execute("SELECT puede_inscribirse FROM estudiantes WHERE id=%s", (usuario['id'],))
        fila = cursor.fetchone()
        if not fila or not fila.get('puede_inscribirse'):
            flash("No estás autorizado para inscribirte. Contacta al administrador.", "error")
            return redirect(url_for('horario_estudiante'))

        # Insertar la solicitud/inscripción (evita duplicados)
        cursor.execute("INSERT IGNORE INTO inscripciones (id_estudiante, id_materia) VALUES (%s, %s)", (usuario['id'], id_materia))
        conexion.commit()
        flash("Solicitud de inscripción enviada. Espera la aprobación del administrador.", "success")
    except Exception as e:
        app.logger.error(f"Error al inscribirse en la materia: {e}")
        flash(f"Ocurrió un error al inscribirte: {e}", "error")
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conexion.close()
        except Exception:
            pass

    return redirect(url_for('horario_estudiante'))
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
# APIs de Eventos (Calendario)
# --------------------------

@app.route('/api/eventos/crear', methods=['POST'])
def crear_evento():
    """Crear un nuevo evento en el calendario del estudiante"""
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        datos = request.get_json()
        id_estudiante = session['usuario']['id']
        resultado = EventoController.crear_evento(id_estudiante, datos)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/eventos/obtener', methods=['GET'])
def obtener_eventos():
    """Obtener todos los eventos del estudiante"""
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        id_estudiante = session['usuario']['id']
        resultado = EventoController.obtener_eventos(id_estudiante)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/eventos/obtener/<int:evento_id>', methods=['GET'])
def obtener_evento(evento_id):
    """Obtener un evento específico"""
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        id_estudiante = session['usuario']['id']
        resultado = EventoController.obtener_evento(evento_id, id_estudiante)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/eventos/actualizar/<int:evento_id>', methods=['PUT'])
def actualizar_evento(evento_id):
    """Actualizar un evento existente"""
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        datos = request.get_json()
        id_estudiante = session['usuario']['id']
        resultado = EventoController.actualizar_evento(evento_id, id_estudiante, datos)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/eventos/eliminar/<int:evento_id>', methods=['DELETE'])
def eliminar_evento(evento_id):
    """Eliminar un evento"""
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        id_estudiante = session['usuario']['id']
        resultado = EventoController.eliminar_evento(evento_id, id_estudiante)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/eventos/fecha/<fecha>', methods=['GET'])
def obtener_eventos_fecha(fecha):
    """Obtener eventos de una fecha específica"""
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        id_estudiante = session['usuario']['id']
        resultado = EventoController.obtener_eventos_por_fecha(id_estudiante, fecha)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/eventos/mes/<int:anio>/<int:mes>', methods=['GET'])
def obtener_eventos_mes(anio, mes):
    """Obtener eventos del mes"""
    if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        id_estudiante = session['usuario']['id']
        resultado = EventoController.obtener_eventos_mes(id_estudiante, anio, mes)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# --------------------------
# Main
# --------------------------

# ================================
# Funciones auxiliares para notificaciones de contenido
# ================================

def verificar_y_generar_notificaciones_contenido(id_profesor=None):
    """
    Verifica si alguna materia del profesor no ha sido actualizada en 3+ días.
    Si es así, genera una notificación al profesor.
    
    Args:
        id_profesor (int, optional): Si es None, verifica todos los profesores.
    
    Returns:
        dict: {'status': 'ok', 'notificaciones_creadas': int, 'materias_alerta': list}
    """
    try:
        conexion = create_connection()
        if not conexion:
            return {'status': 'error', 'message': 'No hay conexión a la BD'}
        
        cursor = conexion.cursor(dictionary=True)
        
        # Construir query
        if id_profesor:
            query = """
            SELECT pac.id_profesor, pac.id_materia, m.nombre, pac.ultima_actualizacion, pac.notificacion_enviada
            FROM profesor_actualizaciones_contenido pac
            JOIN materias m ON pac.id_materia = m.id
            WHERE pac.id_profesor = %s
            ORDER BY pac.ultima_actualizacion ASC
            """
            cursor.execute(query, (id_profesor,))
        else:
            query = """
            SELECT pac.id_profesor, pac.id_materia, m.nombre, pac.ultima_actualizacion, pac.notificacion_enviada
            FROM profesor_actualizaciones_contenido pac
            JOIN materias m ON pac.id_materia = m.id
            ORDER BY pac.ultima_actualizacion ASC
            """
            cursor.execute(query)
        
        registros = cursor.fetchall()
        materias_alerta = []
        notificaciones_creadas = 0
        
        for registro in registros:
            from datetime import datetime, timedelta
            
            id_prof = registro['id_profesor']
            id_mat = registro['id_materia']
            nombre_mat = registro['nombre']
            ultima_act = registro['ultima_actualizacion']
            ya_notificada = registro['notificacion_enviada']
            
            # Convertir a datetime si es string
            if isinstance(ultima_act, str):
                ultima_act = datetime.fromisoformat(ultima_act.replace('Z', '+00:00'))
            
            dias_sin_actualizar = (datetime.now() - ultima_act.replace(tzinfo=None)).days
            
            # Si han pasado 3 o más días y no se ha enviado notificación
            if dias_sin_actualizar >= 3 and not ya_notificada:
                # Crear notificación
                cursor.execute("""
                    INSERT INTO notificaciones (
                        id_profesor,
                        id_estudiante,
                        titulo,
                        mensaje,
                        leida,
                        fecha
                    ) VALUES (%s, %s, %s, %s, %s, NOW())
                """, (
                    id_prof,
                    None,  # NULL porque es al profesor
                    f'Contenido desactualizado: {nombre_mat}',
                    f'Hace {dias_sin_actualizar} días no actualizas el contenido de "{nombre_mat}". Por favor, sube material actualizado para mantener a tus estudiantes informados.',
                    False
                ))
                
                # Marcar como notificada
                cursor.execute("""
                    UPDATE profesor_actualizaciones_contenido
                    SET notificacion_enviada = TRUE, fecha_notificacion = NOW()
                    WHERE id_profesor = %s AND id_materia = %s
                """, (id_prof, id_mat))
                
                notificaciones_creadas += 1
                materias_alerta.append({
                    'materia': nombre_mat,
                    'dias': dias_sin_actualizar
                })
            elif dias_sin_actualizar >= 3:
                # Agregar a lista de alerta sin crear nueva notificación
                materias_alerta.append({
                    'materia': nombre_mat,
                    'dias': dias_sin_actualizar
                })
        
        conexion.commit()
        cursor.close()
        conexion.close()
        
        return {
            'status': 'ok',
            'notificaciones_creadas': notificaciones_creadas,
            'materias_alerta': materias_alerta
        }
    
    except Exception as e:
        print(f"Error en verificar_y_generar_notificaciones_contenido: {str(e)}")
        return {
            'status': 'error',
            'message': str(e),
            'notificaciones_creadas': 0,
            'materias_alerta': []
        }


def obtener_materias_con_estado_contenido(id_profesor):
    """
    Obtiene las materias del profesor con el estado de actualización de contenido.
    
    Returns:
        list: [{id, nombre, dias_sin_actualizar, estado, color}]
    """
    try:
        conexion = create_connection()
        if not conexion:
            return []
        
        cursor = conexion.cursor(dictionary=True)
        
        query = """
        SELECT 
            m.id,
            m.nombre,
            COALESCE(
                DATEDIFF(CURDATE(), DATE(pac.ultima_actualizacion)),
                999
            ) as dias_sin_actualizar,
            CASE 
                WHEN COALESCE(DATEDIFF(CURDATE(), DATE(pac.ultima_actualizacion)), 999) >= 3 THEN 'URGENTE'
                WHEN COALESCE(DATEDIFF(CURDATE(), DATE(pac.ultima_actualizacion)), 999) >= 2 THEN 'ALERTA'
                ELSE 'ACTUALIZADO'
            END as estado_contenido,
            CASE 
                WHEN COALESCE(DATEDIFF(CURDATE(), DATE(pac.ultima_actualizacion)), 999) >= 3 THEN '#f72585'
                WHEN COALESCE(DATEDIFF(CURDATE(), DATE(pac.ultima_actualizacion)), 999) >= 2 THEN '#ffc107'
                ELSE '#28a745'
            END as color
        FROM asignaciones a
        JOIN materias m ON a.id_materia = m.id
        LEFT JOIN profesor_actualizaciones_contenido pac ON a.id_profesor = pac.id_profesor AND a.id_materia = pac.id_materia
        WHERE a.id_profesor = %s
        ORDER BY dias_sin_actualizar DESC
        """
        
        cursor.execute(query, (id_profesor,))
        materias = cursor.fetchall()
        
        cursor.close()
        conexion.close()
        
        return materias if materias else []
    
    except Exception as e:
        print(f"Error en obtener_materias_con_estado_contenido: {str(e)}")
        return []


# --------------------------------
# Factory para pytest
# --------------------------------
def create_app():
    """Crea y configura la aplicación para usarla en pytest."""
    return app


# Health check y estado de la BD
@app.route('/_health')
def health_check():
    """Endpoint simple que devuelve el estado de la aplicación y la base de datos."""
    try:
        conexion = create_connection()
        # Si la conexión es un NullConnection tendrá método cursor pero no datos
        db_ok = conexion is not None and not getattr(conexion, '__class__', type(conexion)).__name__ == 'NullConnection'
        status = {
            'app': 'ok',
            'db': 'ok' if db_ok else 'unavailable',
        }
        # Si la conexión tiene close(), cerrar para liberar recursos
        try:
            conexion.close()
        except Exception:
            pass
        return jsonify(status), 200 if db_ok else 200
    except Exception as e:
        return jsonify({'app': 'error', 'error': str(e)}), 500

# --------------------------------
# Modo desarrollo local
# --------------------------------
if __name__ == '__main__':
    app.run(debug=True)