from Config.database_connection import create_connection

class Notificacion:
    def __init__(self, id=None, id_estudiante=None, mensaje=None, fecha=None):
        self.id = id
        self.id_estudiante = id_estudiante
        self.mensaje = mensaje
        self.fecha = fecha

    @staticmethod
    def crear(id_estudiante, mensaje):
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = """
                INSERT INTO notificaciones (id_estudiante, mensaje)
                VALUES (%s, %s)
                """
                cursor.execute(query, (id_estudiante, mensaje))
                conexion.commit()
                return True
            except Exception as e:
                print(f"Error al crear notificación: {e}")
                return False
            finally:
                if conexion.is_connected():
                    cursor.close()
                    conexion.close()
        return False