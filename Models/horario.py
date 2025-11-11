from Config.database_connection import create_connection

class Horario:
    def __init__(self, id=None, id_estudiante=None, dia_semana=None, hora_inicio=None, hora_fin=None, materia=None):
        self.id = id
        self.id_estudiante = id_estudiante
        self.dia_semana = dia_semana
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.materia = materia

    @staticmethod
    def obtener_todos():
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("SELECT * FROM horarios")
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener horarios: {e}")
                return []
            finally:
                if conexion.is_connected():
                    cursor.close()
                    conexion.close()
        return []

    @staticmethod
    def obtener_por_id(id):
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("SELECT * FROM horarios WHERE id=%s", (id,))
                return cursor.fetchone()
            except Exception as e:
                print(f"Error al obtener horario: {e}")
                return None
            finally:
                if conexion.is_connected():
                    cursor.close()
                    conexion.close()
        return None