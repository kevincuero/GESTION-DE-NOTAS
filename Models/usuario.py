from pymysql import Error
from Config.database_connection import create_connection

class Usuario:
    def __init__(self, id=None, nombre=None, correo=None, contraseña=None, tipo=None):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.contraseña = contraseña
        self.tipo = tipo

    @classmethod
    def obtener_por_correo(cls, correo):
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT 'admin' as tipo, id, nombre, correo, contraseña FROM administradores WHERE correo = %s
                UNION SELECT 'profesor' as tipo, id, nombre, correo, contraseña FROM profesores WHERE correo = %s
                UNION SELECT 'estudiante' as tipo, id, nombre, correo, contraseña FROM estudiantes WHERE correo = %s
                UNION SELECT 'padre' as tipo, id, nombre, correo, contraseña FROM padres WHERE correo = %s
                """
                cursor.execute(query, (correo, correo, correo, correo))
                usuario = cursor.fetchone()
                if usuario:
                    return cls(
                        id=usuario['id'],
                        nombre=usuario['nombre'],
                        correo=usuario['correo'],
                        contraseña=usuario['contraseña'],
                        tipo=usuario['tipo']
                    )
                return None
            except Error as e:
                print(f"Error al obtener usuario: {e}")
                return None
            finally:
                if conexion.is_connected():
                    cursor.close()
                    conexion.close()