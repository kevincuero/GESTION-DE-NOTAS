from Config.database_connection import create_connection
from mysql.connector import Error
from datetime import datetime

class EvaluacionIndice:
    def __init__(self, id=None, id_indice=None, id_profesor=None, porcentaje_dominio=None, comentario=None, fecha_evaluacion=None):
        self.id = id
        self.id_indice = id_indice
        self.id_profesor = id_profesor
        self.porcentaje_dominio = porcentaje_dominio
        self.comentario = comentario
        self.fecha_evaluacion = fecha_evaluacion

    @staticmethod
    def crear_evaluacion(id_indice, id_profesor, porcentaje_dominio, comentario):
        """Crea una evaluación de índice de aprendizaje del grupo."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = """
                INSERT INTO evaluaciones_indices (id_indice, id_profesor, porcentaje_dominio, comentario, fecha_evaluacion)
                VALUES (%s, %s, %s, %s, NOW())
                """
                cursor.execute(query, (id_indice, id_profesor, porcentaje_dominio, comentario))
                conexion.commit()
                return cursor.lastrowid
            except Error as e:
                print(f"Error al crear evaluación de índice: {e}")
                conexion.rollback()
                return None
            finally:
                cursor.close()
                conexion.close()
        return None

    @staticmethod
    def obtener_evaluaciones_por_indice(id_indice):
        """Obtiene todas las evaluaciones de un índice."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT * FROM evaluaciones_indices 
                WHERE id_indice = %s
                ORDER BY fecha_evaluacion DESC
                """
                cursor.execute(query, (id_indice,))
                return cursor.fetchall()
            except Error as e:
                print(f"Error al obtener evaluaciones de índice: {e}")
                return []
            finally:
                cursor.close()
                conexion.close()
        return []

    @staticmethod
    def obtener_ultima_evaluacion(id_indice):
        """Obtiene la última evaluación de un índice."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT * FROM evaluaciones_indices 
                WHERE id_indice = %s
                ORDER BY fecha_evaluacion DESC
                LIMIT 1
                """
                cursor.execute(query, (id_indice,))
                return cursor.fetchone()
            except Error as e:
                print(f"Error al obtener última evaluación: {e}")
                return None
            finally:
                cursor.close()
                conexion.close()
        return None

    @staticmethod
    def actualizar_evaluacion(id_evaluacion, porcentaje_dominio, comentario):
        """Actualiza una evaluación de índice."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = """
                UPDATE evaluaciones_indices 
                SET porcentaje_dominio = %s, comentario = %s
                WHERE id = %s
                """
                cursor.execute(query, (porcentaje_dominio, comentario, id_evaluacion))
                conexion.commit()
                return True
            except Error as e:
                print(f"Error al actualizar evaluación: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                conexion.close()
        return False

    @staticmethod
    def obtener_promedio_dominio(id_indice):
        """Obtiene el promedio de dominio de un índice."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT AVG(porcentaje_dominio) as promedio FROM evaluaciones_indices 
                WHERE id_indice = %s
                """
                cursor.execute(query, (id_indice,))
                resultado = cursor.fetchone()
                return resultado['promedio'] if resultado and resultado['promedio'] else 0
            except Error as e:
                print(f"Error al obtener promedio de dominio: {e}")
                return 0
            finally:
                cursor.close()
                conexion.close()
        return 0
