from flask import flash, redirect, render_template, session, url_for
from Config.database_connection import create_connection
from Models.estudiante import Estudiante
from mysql.connector import Error

class EstudianteController:
    @staticmethod
    def obtener_materias_asignadas(id_estudiante):
        """Obtiene las materias en las que está inscrito un estudiante."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT m.id, m.nombre, m.descripcion
                FROM materias m
                INNER JOIN inscripciones i ON m.id = i.id_materia
                WHERE i.id_estudiante = %s
                """
                cursor.execute(query, (id_estudiante,))
                materias = cursor.fetchall()
                return materias
            except Error as e:
                print(f"Error al obtener materias asignadas: {e}")
                return []
            finally:
                cursor.close()
                conexion.close()

    @staticmethod
    def obtener_calificaciones(id_estudiante):
        """Obtiene las calificaciones del estudiante en sus materias."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT m.nombre AS materia, n.nota
                FROM notas n
                INNER JOIN materias m ON n.id_materia = m.id
                WHERE n.id_estudiante = %s
                """
                cursor.execute(query, (id_estudiante,))
                calificaciones = cursor.fetchall()
                return calificaciones
            except Error as e:
                print(f"Error al obtener calificaciones: {e}")
                return []
            finally:
                cursor.close()
                conexion.close()

    @staticmethod
    def obtener_detalle_materia(id_estudiante, id_materia):
        """Obtiene los detalles de una materia específica en la que está inscrito el estudiante."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT m.id, m.nombre, m.descripcion, p.nombre AS profesor
                FROM materias m
                INNER JOIN asignaciones a ON m.id = a.id_materia
                INNER JOIN profesores p ON a.id_profesor = p.id
                INNER JOIN inscripciones i ON m.id = i.id_materia
                WHERE i.id_estudiante = %s AND m.id = %s
                """
                cursor.execute(query, (id_estudiante, id_materia))
                detalle = cursor.fetchone()
                return detalle
            except Error as e:
                print(f"Error al obtener detalle de la materia: {e}")
                return None
            finally:
                cursor.close()
                conexion.close()

    @staticmethod
    def obtener_promedio_general(id_estudiante):
        """Calcula el promedio general de las calificaciones del estudiante."""
        return Estudiante.obtener_promedio_general(id_estudiante)

    @staticmethod
    def obtener_notificaciones(id_estudiante):
        """Obtiene las notificaciones enviadas al estudiante (usa el modelo si existe)."""
        # Preferir el método del modelo que normaliza campos
        try:
            raw = Estudiante.obtener_notificaciones_detalle(id_estudiante)
            # Normalizar claves para las vistas que esperan 'mensaje' y 'fecha'
            normalized = []
            for n in (raw or []):
                notif = dict(n) if isinstance(n, dict) else dict(n)
                # mapear campos posibles
                mensaje = notif.get('mensaje') or notif.get('descripcion') or notif.get('mensaje_notificacion') or ''
                fecha = notif.get('fecha') or notif.get('fecha_creacion') or notif.get('fecha_enviado') or ''
                notif['mensaje'] = mensaje
                notif['fecha'] = fecha
                normalized.append(notif)
            return normalized
        except Exception as e:
            print(f"Error al obtener notificaciones desde modelo: {e}")
            # Fallback a una consulta directa si el modelo falla
            conexion = create_connection()
            if conexion:
                try:
                    cursor = conexion.cursor(dictionary=True)
                    query = """
                    SELECT id, titulo, mensaje AS descripcion, fecha AS fecha_creacion, '' AS remitente, 0 AS leida, 'academica' AS tipo
                    FROM notificaciones
                    WHERE id_estudiante = %s
                    ORDER BY fecha DESC
                    """
                    cursor.execute(query, (id_estudiante,))
                    notificaciones = cursor.fetchall()
                    return notificaciones
                except Error as e2:
                    print(f"Error al obtener notificaciones (fallback): {e2}")
                    return []
                finally:
                    cursor.close()
                    conexion.close()

    @staticmethod
    def obtener_datos_dashboard(id_estudiante):
        """Obtiene todos los datos necesarios para el dashboard del estudiante."""
        # Obtener notificaciones desde el controlador de notificaciones (misma fuente que la vista de "mis_notificaciones")
        try:
            from Controllers.notificacion_controller import NotificacionController
            notificaciones_completas = NotificacionController.obtener_notificaciones_estudiante(id_estudiante)
        except Exception:
            # Fallback al método anterior del modelo/estudiante
            notificaciones_completas = EstudianteController.obtener_notificaciones(id_estudiante)
        datos = {
            'tareas_pendientes': Estudiante.obtener_tareas_pendientes(id_estudiante),
            'asistencia': Estudiante.obtener_asistencia(id_estudiante),
            'materias_inscritas': Estudiante.obtener_materias_inscritas(id_estudiante),
            'promedio_general': Estudiante.obtener_promedio_general(id_estudiante),
            'estadisticas': Estudiante.obtener_estadisticas_por_materia(id_estudiante),
            # Mostrar únicamente las 5 notificaciones más recientes en el dashboard
            'notificaciones': (notificaciones_completas or [])[:5]
        }
        return datos

    @staticmethod
    def obtener_horario(id_estudiante):
        """Obtiene el horario detallado del estudiante."""
        conexion = create_connection()
        horario = []
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
                cursor.execute(query, (id_estudiante,))
                horario = cursor.fetchall()
            except Error as e:
                print(f"Error al obtener horario: {e}")
                horario = []
            finally:
                cursor.close()
                conexion.close()
        return horario

    @staticmethod
    def obtener_tareas_detalle(id_estudiante):
        """Obtiene la lista completa de tareas para el estudiante (detalladas)."""
        try:
            return Estudiante.obtener_tareas(id_estudiante)
        except Exception as e:
            print(f"Error al obtener tareas desde modelo: {e}")
            return []

    @staticmethod
    def obtener_calificaciones_detalle(id_estudiante):
        """Obtiene calificaciones y estadísticas por materia para la vista de calificaciones."""
        conexion = create_connection()
        notas = []
        estadisticas = []
        promedio = 0
        try:
            notas = Estudiante.obtener_notas(id_estudiante)
            estadisticas = Estudiante.obtener_estadisticas_por_materia(id_estudiante)
            promedio = Estudiante.obtener_promedio_general(id_estudiante)
        except Exception as e:
            print(f"Error al obtener calificaciones detalladas: {e}")
        return {
            'notas': notas,
            'estadisticas': estadisticas,
            'promedio_general': promedio
        }

    @staticmethod
    def obtener_informe_estudiante(id_estudiante):
        """Genera un informe general del estudiante: materias inscritas, notas (con tipo) y profesor de cada nota."""
        conexion = create_connection()
        informe = []
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                # Obtener todas las materias en las que está inscrito
                query = """
                SELECT m.id as id_materia, m.nombre as materia, p.id as id_profesor, p.nombre as profesor,
                       n.id as id_nota, n.tipo_evaluacion, n.nota, n.comentario, n.fecha
                FROM inscripciones i
                JOIN materias m ON i.id_materia = m.id
                LEFT JOIN notas n ON n.id_materia = m.id AND n.id_estudiante = i.id_estudiante
                LEFT JOIN profesores p ON n.id_profesor = p.id OR p.id = (
                    SELECT a.id_profesor FROM asignaciones a WHERE a.id_materia = m.id LIMIT 1
                )
                WHERE i.id_estudiante = %s
                ORDER BY m.nombre, n.tipo_evaluacion
                """
                cursor.execute(query, (id_estudiante,))
                rows = cursor.fetchall()

                # Agrupar por materia
                materias = {}
                for r in rows:
                    mid = r.get('id_materia')
                    if mid not in materias:
                        materias[mid] = {
                            'id': mid,
                            'materia': r.get('materia'),
                            'profesor': r.get('profesor'),
                            'notas': []
                        }
                    if r.get('id_nota'):
                        materias[mid]['notas'].append({
                            'id_nota': r.get('id_nota'),
                            'tipo': r.get('tipo_evaluacion'),
                            'nota': r.get('nota'),
                            'comentario': r.get('comentario'),
                            'fecha': r.get('fecha')
                        })

                # Convertir a lista
                for m in materias.values():
                    informe.append(m)

                return informe
            except Exception as e:
                print(f"Error al generar informe del estudiante: {e}")
                return []
            finally:
                cursor.close()
                conexion.close()
        return informe

    @staticmethod
    def obtener_contenidos_inscritos(id_estudiante, id_materia=None):
        """Obtiene los contenidos de las materias inscritas del estudiante, opcionalmente filtrados por materia."""
        conexion = create_connection()
        contenidos = []
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                if id_materia:
                    # Filtrar por materia específica
                    query = """
                    SELECT c.id, c.titulo, c.descripcion, c.tipo, c.filename, c.ruta, c.fecha_subida, c.tamano,
                           m.id AS id_materia, m.nombre AS nombre_materia, p.nombre AS nombre_profesor
                    FROM contenidos_materia c
                    JOIN materias m ON c.id_materia = m.id
                    JOIN profesores p ON c.id_profesor = p.id
                    JOIN inscripciones i ON m.id = i.id_materia
                    WHERE i.id_estudiante = %s AND m.id = %s
                    ORDER BY c.fecha_subida DESC
                    """
                    cursor.execute(query, (id_estudiante, id_materia))
                else:
                    # Traer contenidos de todas las materias inscritas
                    query = """
                    SELECT c.id, c.titulo, c.descripcion, c.tipo, c.filename, c.ruta, c.fecha_subida, c.tamano,
                           m.id AS id_materia, m.nombre AS nombre_materia, p.nombre AS nombre_profesor
                    FROM contenidos_materia c
                    JOIN materias m ON c.id_materia = m.id
                    JOIN profesores p ON c.id_profesor = p.id
                    JOIN inscripciones i ON m.id = i.id_materia
                    WHERE i.id_estudiante = %s
                    ORDER BY m.nombre, c.fecha_subida DESC
                    """
                    cursor.execute(query, (id_estudiante,))
                contenidos = cursor.fetchall()
            except Error as e:
                print(f"Error al obtener contenidos inscritos: {e}")
                contenidos = []
            finally:
                cursor.close()
                conexion.close()
        return contenidos

    @staticmethod
    def ver_notas():
        """Obtiene las notas del estudiante desde la base de datos."""
        if 'usuario' not in session or session['usuario']['tipo'] != 'estudiante':
            flash("Debes iniciar sesión como estudiante para acceder a esta página.", "error")
            return redirect(url_for('home'))

        id_estudiante = session['usuario']['id']
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT 
                    m.nombre AS materia,
                    p.nombre AS profesor,
                    n.nota AS nota
                FROM notas n
                JOIN materias m ON n.id_materia = m.id
                LEFT JOIN profesores p ON n.id_profesor = p.id
                WHERE n.id_estudiante = %s
                """
                cursor.execute(query, (id_estudiante,))
                notas = cursor.fetchall()
                return render_template('estudiante/ver_notas.html', usuario=session['usuario'], notas=notas)
            except Error as e:
                print(f"Error al obtener notas: {e}")
                flash("Ocurrió un error al obtener tus notas.", "error")
                return redirect(url_for('estudiante_dashboard'))
            finally:
                cursor.close()
                conexion.close()
        else:
            flash("Error al conectar con la base de datos.", "error")
            return redirect(url_for('estudiante_dashboard'))

    @staticmethod
    def obtener_tareas_inscritas(id_estudiante, id_materia=None):
        """Obtiene tareas de las materias en las que está inscrito el estudiante.
        Retorna información: id, id_materia, nombre_materia, titulo, descripcion, tipo_tarea,
        fecha_entrega, id_profesor, nombre_profesor, filename, ruta."""
        conexion = create_connection()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            if id_materia:
                query = """
                SELECT tm.id, tm.id_materia, m.nombre AS nombre_materia, tm.titulo, tm.descripcion,
                       tm.tipo_tarea, tm.fecha_entrega, tm.id_profesor, p.nombre AS nombre_profesor,
                       tm.filename, tm.ruta
                FROM tareas_materia tm
                JOIN materias m ON tm.id_materia = m.id
                JOIN profesores p ON tm.id_profesor = p.id
                JOIN inscripciones i ON tm.id_materia = i.id_materia
                WHERE i.id_estudiante = %s AND tm.id_materia = %s
                ORDER BY tm.fecha_entrega ASC
                """
                cursor.execute(query, (id_estudiante, id_materia))
            else:
                query = """
                SELECT tm.id, tm.id_materia, m.nombre AS nombre_materia, tm.titulo, tm.descripcion,
                       tm.tipo_tarea, tm.fecha_entrega, tm.id_profesor, p.nombre AS nombre_profesor,
                       tm.filename, tm.ruta
                FROM tareas_materia tm
                JOIN materias m ON tm.id_materia = m.id
                JOIN profesores p ON tm.id_profesor = p.id
                JOIN inscripciones i ON tm.id_materia = i.id_materia
                WHERE i.id_estudiante = %s
                ORDER BY tm.fecha_entrega ASC
                """
                cursor.execute(query, (id_estudiante,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener tareas del estudiante: {e}")
            return []
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conexion.close()
            except Exception:
                pass