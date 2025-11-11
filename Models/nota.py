from Config.database_connection import create_connection

class Nota:
    def __init__(self, id=None, id_estudiante=None, id_materia=None, calificacion=None, fecha=None):
        self.id = id
        self.id_estudiante = id_estudiante
        self.id_materia = id_materia
        self.calificacion = calificacion
        self.fecha = fecha

    def guardar(self):
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = """
                INSERT INTO notas (id_estudiante, id_materia, calificacion)
                VALUES (%s, %s, %s)
                """
                cursor.execute(query, (self.id_estudiante, self.id_materia, self.calificacion))
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