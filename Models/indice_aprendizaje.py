from Config.database_connection import create_connection
from mysql.connector import Error

class IndiceAprendizaje:
    def __init__(self, id=None, id_materia=None, id_profesor=None, nombre=None, descripcion=None, porcentaje=None, parcial=None):
        self.id = id
        self.id_materia = id_materia
        self.id_profesor = id_profesor
        self.nombre = nombre
        self.descripcion = descripcion
        self.porcentaje = porcentaje
        self.parcial = parcial

    @staticmethod
    def crear_indice(id_materia, id_profesor, nombre, descripcion, porcentaje, parcial):
        """Crea un nuevo índice de aprendizaje para una materia."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = """
                INSERT INTO indices_aprendizaje (id_materia, id_profesor, nombre, descripcion, porcentaje, parcial)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (id_materia, id_profesor, nombre, descripcion, porcentaje, parcial))
                conexion.commit()
                return cursor.lastrowid
            except Error as e:
                print(f"Error al crear índice de aprendizaje: {e}")
                conexion.rollback()
                return None
            finally:
                cursor.close()
                conexion.close()
        return None

    @staticmethod
    def obtener_indices_por_materia(id_materia, id_profesor):
        """Obtiene todos los índices de aprendizaje para una materia específica."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT * FROM indices_aprendizaje 
                WHERE id_materia = %s AND id_profesor = %s
                ORDER BY parcial ASC
                """
                cursor.execute(query, (id_materia, id_profesor))
                return cursor.fetchall()
            except Error as e:
                print(f"Error al obtener índices de aprendizaje: {e}")
                return []
            finally:
                cursor.close()
                conexion.close()
        return []

    @staticmethod
    def obtener_indices_por_materia_sin_profesor(id_materia):
        """Obtiene todos los índices de aprendizaje para una materia (sin filtrar por profesor)."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT * FROM indices_aprendizaje 
                WHERE id_materia = %s
                ORDER BY parcial ASC
                """
                cursor.execute(query, (id_materia,))
                return cursor.fetchall()
            except Error as e:
                print(f"Error al obtener índices de aprendizaje: {e}")
                return []
            finally:
                cursor.close()
                conexion.close()
        return []

    @staticmethod
    def obtener_indice_por_id(id_indice):
        """Obtiene un índice de aprendizaje específico."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = "SELECT * FROM indices_aprendizaje WHERE id = %s"
                cursor.execute(query, (id_indice,))
                return cursor.fetchone()
            except Error as e:
                print(f"Error al obtener índice de aprendizaje: {e}")
                return None
            finally:
                cursor.close()
                conexion.close()
        return None

    @staticmethod
    def actualizar_indice(id_indice, nombre, descripcion, porcentaje, parcial):
        """Actualiza un índice de aprendizaje."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = """
                UPDATE indices_aprendizaje 
                SET nombre = %s, descripcion = %s, porcentaje = %s, parcial = %s
                WHERE id = %s
                """
                cursor.execute(query, (nombre, descripcion, porcentaje, parcial, id_indice))
                conexion.commit()
                return True
            except Error as e:
                print(f"Error al actualizar índice de aprendizaje: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                conexion.close()
        return False

    @staticmethod
    def eliminar_indice(id_indice):
        """Elimina un índice de aprendizaje."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                # Primero eliminar evaluaciones asociadas
                query_eval = "DELETE FROM evaluaciones_indices WHERE id_indice = %s"
                cursor.execute(query_eval, (id_indice,))
                
                # Luego eliminar el índice
                query = "DELETE FROM indices_aprendizaje WHERE id = %s"
                cursor.execute(query, (id_indice,))
                conexion.commit()
                return True
            except Error as e:
                print(f"Error al eliminar índice de aprendizaje: {e}")
                conexion.rollback()
                return False
            finally:
                cursor.close()
                conexion.close()
        return False

    @staticmethod
    def contar_indices_por_materia(id_materia, id_profesor):
        """Cuenta el número de índices para una materia (máx 4)."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = """
                SELECT COUNT(*) as total FROM indices_aprendizaje 
                WHERE id_materia = %s AND id_profesor = %s
                """
                cursor.execute(query, (id_materia, id_profesor))
                resultado = cursor.fetchone()
                return resultado[0] if resultado else 0
            except Error as e:
                print(f"Error al contar índices: {e}")
                return 0
            finally:
                cursor.close()
                conexion.close()
        return 0
