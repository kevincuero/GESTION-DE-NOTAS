from Config.database_connection import create_connection

class Nota:
    def __init__(self, id=None, id_estudiante=None, id_profesor=None, id_materia=None, 
                 nota=None, tipo_evaluacion='parcial', comentario=None, fecha=None):
        self.id = id
        self.id_estudiante = id_estudiante
        self.id_profesor = id_profesor
        self.id_materia = id_materia
        self.nota = nota
        self.tipo_evaluacion = tipo_evaluacion
        self.comentario = comentario
        self.fecha = fecha

    def guardar(self):
        """Guarda una nueva nota en la base de datos."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = """
                INSERT INTO notas (id_estudiante, id_profesor, id_materia, nota, tipo_evaluacion, comentario, fecha)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """
                cursor.execute(query, (self.id_estudiante, self.id_profesor, self.id_materia, 
                                      self.nota, self.tipo_evaluacion, self.comentario))
                conexion.commit()
                return True
            except Exception as e:
                print(f"Error al guardar nota: {e}")
                return False
            finally:
                if conexion.is_connected():
                    cursor.close()
                    conexion.close()
        return False

    def actualizar(self):
        """Actualiza una nota existente."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = """
                UPDATE notas 
                SET nota=%s, tipo_evaluacion=%s, comentario=%s, fecha=NOW()
                WHERE id=%s
                """
                cursor.execute(query, (self.nota, self.tipo_evaluacion, self.comentario, self.id))
                conexion.commit()
                return True
            except Exception as e:
                print(f"Error al actualizar nota: {e}")
                return False
            finally:
                if conexion.is_connected():
                    cursor.close()
                    conexion.close()
        return False

    def eliminar(self):
        """Elimina una nota de la base de datos."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "DELETE FROM notas WHERE id=%s"
                cursor.execute(query, (self.id,))
                conexion.commit()
                return True
            except Exception as e:
                print(f"Error al eliminar nota: {e}")
                return False
            finally:
                if conexion.is_connected():
                    cursor.close()
                    conexion.close()
        return False

    @staticmethod
    def obtener_por_id(id_nota):
        """Obtiene una nota específica por su ID."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = "SELECT * FROM notas WHERE id=%s"
                cursor.execute(query, (id_nota,))
                return cursor.fetchone()
            except Exception as e:
                print(f"Error al obtener nota: {e}")
                return None
            finally:
                if conexion.is_connected():
                    cursor.close()
                    conexion.close()
        return None