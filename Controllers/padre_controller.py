from Config.database_connection import create_connection
from mysql.connector import Error

class PadreController:
    @staticmethod
    def obtener_hijos(id_padre):
        """Obtiene los hijos asociados a un padre."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT e.id, e.nombre, e.correo
                FROM estudiantes e
                INNER JOIN padres_estudiantes pe ON e.id = pe.id_estudiante
                WHERE pe.id_padre = %s
                """
                cursor.execute(query, (id_padre,))
                hijos = cursor.fetchall()
                return hijos
            except Error as e:
                print(f"Error al obtener hijos: {e}")
                return []
            finally:
                cursor.close()
                conexion.close()

    @staticmethod
    def obtener_materias_hijo(id_estudiante):
        """Obtiene las materias en las que está inscrito un hijo."""
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
                print(f"Error al obtener materias del hijo: {e}")
                return []
            finally:
                cursor.close()
                conexion.close()

    @staticmethod
    def obtener_calificaciones_hijo(id_estudiante):
        """Obtiene las calificaciones del hijo en sus materias."""
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
                print(f"Error al obtener calificaciones del hijo: {e}")
                return []
            finally:
                cursor.close()
                conexion.close()

    @staticmethod
    def obtener_promedio_hijo(id_estudiante):
        """Calcula el promedio general de las calificaciones del hijo."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = """
                SELECT AVG(nota) AS promedio
                FROM notas
                WHERE id_estudiante = %s
                """
                cursor.execute(query, (id_estudiante,))
                resultado = cursor.fetchone()
                return resultado['promedio'] if resultado else None
            except Error as e:
                print(f"Error al calcular promedio del hijo: {e}")
                return None
            finally:
                cursor.close()
                conexion.close()

    @staticmethod
    def obtener_notificaciones_hijo(id_estudiante):
        """Obtiene las notificaciones enviadas al hijo."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT n.id, n.titulo, n.mensaje, n.fecha
                FROM notificaciones n
                WHERE n.id_estudiante = %s
                ORDER BY n.fecha DESC
                """
                cursor.execute(query, (id_estudiante,))
                notificaciones = cursor.fetchall()
                return notificaciones
            except Error as e:
                print(f"Error al obtener notificaciones del hijo: {e}")
                return []
            finally:
                cursor.close()
                conexion.close()