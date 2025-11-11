from Models.admin import Admin
from Models.profesor import Profesor
from Models.estudiante import Estudiante
from Models.padre import Padre
from Models.usuario import Usuario
from werkzeug.security import check_password_hash

class AutenticacionController:
    @staticmethod
    def login(correo, contraseña):
        """Valida el inicio de sesión basado en correo y contraseña."""
        # Verifica si el correo pertenece a un usuario (no administradores)
        usuario = Usuario.obtener_por_correo(correo)
        if usuario and check_password_hash(usuario.contraseña, contraseña):
            if usuario.tipo == 'profesor':
                return Profesor(usuario.id, usuario.nombre, usuario.correo, usuario.contraseña)
            elif usuario.tipo == 'estudiante':
                return Estudiante(usuario.id, usuario.nombre, usuario.correo, usuario.contraseña)
            elif usuario.tipo == 'padre':
                return Padre(usuario.id, usuario.nombre, usuario.correo, usuario.contraseña)
        return None

    @staticmethod
    def login_por_correo(correo, contraseña):
        """Valida el inicio de sesión de un administrador por correo y contraseña."""
        try:
            administrador = Admin.obtener_por_correo(correo)
            if administrador:
                print(f"Administrador encontrado: {administrador.nombre}")  # Depuración
                if check_password_hash(administrador.contraseña, contraseña):
                    print("Contraseña válida")  # Depuración
                    return administrador
                else:
                    print("Contraseña inválida")  # Depuración
            else:
                print(f"No se encontró un administrador con el correo: {correo}")  # Depuración
        except Exception as e:
            print(f"Error en login_por_correo: {str(e)}")  # Depuración
        return None