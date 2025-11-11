from Config.database_connection import create_connection
from Models.usuario import Usuario
from Controllers.admin_controller import AdminController

class Admin:
    def __init__(self, id, nombre, correo, contraseña):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.contraseña = contraseña

    @staticmethod
    def obtener_por_correo(correo):
        """Obtiene un administrador por su correo."""
        conexion = create_connection()
        if conexion:
            try:
                with conexion.cursor(dictionary=True) as cursor:
                    query = "SELECT * FROM administradores WHERE correo = %s"
                    cursor.execute(query, (correo,))
                    admin_data = cursor.fetchone()
                    if admin_data:
                        print(f"Administrador encontrado: {admin_data}")  # Depuración
                        return Admin(
                            id=admin_data['id'],
                            nombre=admin_data['nombre'],
                            correo=admin_data['correo'],
                            contraseña=admin_data['contraseña']
                        )
                    else:
                        print(f"No se encontró un administrador con el correo: {correo}")  # Depuración
            except Exception as e:
                print(f"Error al obtener administrador por correo: {str(e)}")  # Depuración
            finally:
                conexion.close()
        else:
            print("No se pudo establecer la conexión con la base de datos.")  # Depuración
        return None

class AdminModel:
    @staticmethod
    def obtener_usuarios_con_roles():
        """Llama al controlador para obtener usuarios con ID, nombre y rol."""
        return AdminController.obtener_usuarios_con_roles()