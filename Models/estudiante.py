from Config.database_connection import create_connection

class Estudiante:
    def __init__(self, id, nombre, correo, contraseña):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.contraseña = contraseña

    @staticmethod
    def obtener_por_id(id_estudiante):
        """Obtiene un estudiante por su ID."""
        conexion = create_connection()
        if conexion:
            try:
                with conexion.cursor(dictionary=True) as cursor:
                    query = "SELECT * FROM estudiantes WHERE id = %s"
                    cursor.execute(query, (id_estudiante,))
                    estudiante_data = cursor.fetchone()
                    if estudiante_data:
                        return Estudiante(
                            id=estudiante_data['id'],
                            nombre=estudiante_data['nombre'],
                            correo=estudiante_data['correo'],
                            contraseña=estudiante_data['contraseña']
                        )
            except Exception as e:
                print(f"Error al obtener estudiante por ID: {e}")
            finally:
                conexion.close()
        return None

    @staticmethod
    def obtener_notas(id_estudiante):
        """Obtiene las notas de un estudiante por su ID con comentario y fecha."""
        conexion = create_connection()
        if conexion:
            try:
                with conexion.cursor(dictionary=True) as cursor:
                    query = """
                        SELECT m.nombre AS materia, n.nota, n.comentario, 
                               DATE_FORMAT(n.fecha, '%Y-%m-%d %H:%i') AS fecha
                        FROM notas n
                        JOIN materias m ON n.id_materia = m.id
                        WHERE n.id_estudiante = %s
                        ORDER BY n.fecha DESC
                    """
                    cursor.execute(query, (id_estudiante,))
                    return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener las notas del estudiante: {e}")
            finally:
                conexion.close()
        return []

    @staticmethod
    def obtener_promedio_general(id_estudiante):
        """Calcula el promedio general de calificaciones del estudiante."""
        conexion = create_connection()
        if conexion:
            try:
                with conexion.cursor(dictionary=True) as cursor:
                    query = """
                        SELECT ROUND(AVG(nota), 2) AS promedio
                        FROM notas
                        WHERE id_estudiante = %s
                    """
                    cursor.execute(query, (id_estudiante,))
                    resultado = cursor.fetchone()
                    return resultado['promedio'] if resultado and resultado['promedio'] else 0
            except Exception as e:
                print(f"Error al obtener promedio general: {e}")
            finally:
                conexion.close()
        return 0

    @staticmethod
    def obtener_tareas_pendientes(id_estudiante):
        """Obtiene el número de tareas pendientes del estudiante."""
        conexion = create_connection()
        if conexion:
            try:
                with conexion.cursor(dictionary=True) as cursor:
                    query = """
                        SELECT COUNT(*) AS total
                        FROM tareas
                        WHERE id_estudiante = %s AND estado = 'pendiente'
                    """
                    cursor.execute(query, (id_estudiante,))
                    resultado = cursor.fetchone()
                    return resultado['total'] if resultado else 0
            except Exception as e:
                print(f"Error al obtener tareas pendientes: {e}")
            finally:
                conexion.close()
        return 0

    @staticmethod
    def obtener_materias_inscritas(id_estudiante):
        """Obtiene el número de materias inscritas del estudiante."""
        conexion = create_connection()
        if conexion:
            try:
                with conexion.cursor(dictionary=True) as cursor:
                    query = """
                        SELECT COUNT(*) AS total
                        FROM inscripciones
                        WHERE id_estudiante = %s
                    """
                    cursor.execute(query, (id_estudiante,))
                    resultado = cursor.fetchone()
                    return resultado['total'] if resultado else 0
            except Exception as e:
                print(f"Error al obtener materias inscritas: {e}")
            finally:
                conexion.close()
        return 0

    @staticmethod
    def obtener_asistencia(id_estudiante):
        """Obtiene la asistencia del estudiante (si está registrada en la BD)."""
        conexion = create_connection()
        if conexion:
            try:
                with conexion.cursor(dictionary=True) as cursor:
                    # Verificar si existe tabla asistencias
                    cursor.execute("SHOW TABLES LIKE 'asistencias'")
                    if cursor.fetchone():
                        query = """
                            SELECT COUNT(*) AS total
                            FROM asistencias
                            WHERE id_estudiante = %s AND presente = 1
                        """
                        cursor.execute(query, (id_estudiante,))
                        resultado = cursor.fetchone()
                        return resultado['total'] if resultado else 0
            except Exception as e:
                print(f"Error al obtener asistencia: {e}")
            finally:
                conexion.close()
        return 0

    @staticmethod
    def obtener_estadisticas_por_materia(id_estudiante):
        """Obtiene promedio por cada materia del estudiante."""
        conexion = create_connection()
        if conexion:
            try:
                with conexion.cursor(dictionary=True) as cursor:
                    query = """
                        SELECT m.nombre AS materia, ROUND(AVG(n.nota), 2) AS promedio
                        FROM inscripciones i
                        JOIN materias m ON i.id_materia = m.id
                        LEFT JOIN notas n ON n.id_materia = m.id AND n.id_estudiante = i.id_estudiante
                        WHERE i.id_estudiante = %s
                        GROUP BY m.id, m.nombre
                    """
                    cursor.execute(query, (id_estudiante,))
                    return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener estadísticas por materia: {e}")
            finally:
                conexion.close()
        return []

    @staticmethod
    def obtener_tareas(id_estudiante):
        """Obtiene la lista de tareas del estudiante con detalle."""
        conexion = create_connection()
        if conexion:
            try:
                with conexion.cursor(dictionary=True) as cursor:
                    query = """
                        SELECT t.id, t.titulo, t.descripcion, DATE_FORMAT(t.fecha_entrega, '%Y-%m-%d') AS fecha_entrega,
                               t.prioridad, t.estado, m.nombre AS materia
                        FROM tareas t
                        LEFT JOIN materias m ON t.id_materia = m.id
                        WHERE t.id_estudiante = %s
                        ORDER BY t.fecha_entrega ASC
                    """
                    cursor.execute(query, (id_estudiante,))
                    return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener las tareas del estudiante: {e}")
            finally:
                conexion.close()
        return []

    @staticmethod
    def obtener_notificaciones_detalle(id_estudiante):
        """Obtiene las notificaciones para el estudiante con campos útiles para la vista."""
        conexion = create_connection()
        if conexion:
            try:
                with conexion.cursor(dictionary=True) as cursor:
                    # Intentamos usar nombres de columnas comunes; si no existen algunas columnas, devolverán NULL
                    query = """
                        SELECT n.id,
                               n.titulo,
                               COALESCE(n.mensaje, n.descripcion) AS descripcion,
                               COALESCE(n.fecha, n.fecha_creacion) AS fecha_creacion,
                               COALESCE(n.remitente, '') AS remitente,
                               COALESCE(n.leida, 0) AS leida,
                               COALESCE(n.tipo, 'academica') AS tipo
                        FROM notificaciones n
                        WHERE n.id_estudiante = %s
                        ORDER BY fecha_creacion DESC
                    """
                    cursor.execute(query, (id_estudiante,))
                    return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener notificaciones: {e}")
            finally:
                conexion.close()
        return []

    @staticmethod
    def obtener_todos():
        """Obtiene todos los estudiantes."""
        conexion = create_connection()
        if conexion:
            try:
                with conexion.cursor(dictionary=True) as cursor:
                    query = "SELECT * FROM estudiantes"
                    cursor.execute(query)
                    return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener todos los estudiantes: {e}")
            finally:
                conexion.close()
        return []

    def guardar(self):
        """Guarda un nuevo estudiante en la base de datos."""
        conexion = create_connection()
        if conexion:
            try:
                with conexion.cursor() as cursor:
                    query = """
                        INSERT INTO estudiantes (nombre, correo, contraseña)
                        VALUES (%s, %s, %s)
                    """
                    cursor.execute(query, (self.nombre, self.correo, self.contraseña))
                    conexion.commit()
                    self.id = cursor.lastrowid
                    print("Estudiante guardado correctamente.")
            except Exception as e:
                print(f"Error al guardar el estudiante: {e}")
            finally:
                conexion.close()

    def actualizar(self):
        """Actualiza los datos de un estudiante existente."""
        conexion = create_connection()
        if conexion:
            try:
                with conexion.cursor() as cursor:
                    query = """
                        UPDATE estudiantes
                        SET nombre = %s, correo = %s, contraseña = %s
                        WHERE id = %s
                    """
                    cursor.execute(query, (self.nombre, self.correo, self.contraseña, self.id))
                    conexion.commit()
                    print("Estudiante actualizado correctamente.")
            except Exception as e:
                print(f"Error al actualizar el estudiante: {e}")
            finally:
                conexion.close()

    def eliminar(self):
        """Elimina un estudiante de la base de datos."""
        conexion = create_connection()
        if conexion:
            try:
                with conexion.cursor() as cursor:
                    query = "DELETE FROM estudiantes WHERE id = %s"
                    cursor.execute(query, (self.id,))
                    conexion.commit()
                    print("Estudiante eliminado correctamente.")
            except Exception as e:
                print(f"Error al eliminar el estudiante: {e}")
            finally:
                conexion.close()