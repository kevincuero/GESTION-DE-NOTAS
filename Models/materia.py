from Config.database_connection import create_connection

class Materia:
    def __init__(self, id=None, nombre=None):
        self.id = id
        self.nombre = nombre

    @staticmethod
    def obtener_todas():
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("SELECT * FROM materias")
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener materias: {e}")
                return []
            finally:
                if conexion.is_connected():
                    cursor.close()
                    conexion.close()
        return []