from Config.database_connection import create_connection
from mysql.connector import Error
from werkzeug.security import generate_password_hash

class AdminController:
    @staticmethod
    def obtener_usuarios():
        """Obtiene todos los usuarios del sistema."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = "SELECT * FROM usuarios"
                cursor.execute(query)
                usuarios = cursor.fetchall()
                return usuarios
            except Error as e:
                print(f"Error al obtener usuarios: {e}")
                return []
            finally:
                cursor.close()
                conexion.close()

    @staticmethod
    def agregar_usuario(nombre, correo, contraseña, rol):
        """Agrega un nuevo usuario al sistema en la tabla general y en la tabla específica según su rol."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                # Cifrar la contraseña antes de almacenarla
                contraseña_cifrada = generate_password_hash(contraseña)

                # Insertar en la tabla general `usuarios`
                query_usuarios = """
                INSERT INTO usuarios (nombre, correo, contraseña, rol)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query_usuarios, (nombre, correo, contraseña_cifrada, rol))

                # Determinar la tabla específica según el rol
                if rol == 'admin':
                    tabla = 'administradores'
                elif rol == 'profesor':
                    tabla = 'profesores'
                elif rol == 'estudiante':
                    tabla = 'estudiantes'
                elif rol == 'padre':
                    tabla = 'padres'
                else:
                    raise ValueError("Rol no válido")

                # Insertar en la tabla específica
                query_tabla_especifica = f"""
                INSERT INTO {tabla} (nombre, correo, contraseña)
                VALUES (%s, %s, %s)
                """
                cursor.execute(query_tabla_especifica, (nombre, correo, contraseña_cifrada))

                conexion.commit()
                return True
            except Exception as e:
                print(f"Error al agregar usuario: {e}")
                return False
            finally:
                cursor.close()
                conexion.close()
                
    @staticmethod
    def eliminar_usuario(id_usuario):
        """Elimina un usuario por su ID."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "DELETE FROM usuarios WHERE id = %s"
                cursor.execute(query, (id_usuario,))
                conexion.commit()
                return True
            except Error as e:
                print(f"Error al eliminar usuario: {e}")
                return False
            finally:
                cursor.close()
                conexion.close()

    @staticmethod
    def obtener_usuario_por_id(id_usuario):
        """Obtiene un usuario por su ID."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = "SELECT * FROM usuarios WHERE id = %s"
                cursor.execute(query, (id_usuario,))
                usuario = cursor.fetchone()
                return usuario
            except Error as e:
                print(f"Error al obtener usuario por ID: {e}")
                return None
            finally:
                cursor.close()
                conexion.close()
        return None

    @staticmethod
    def modificar_usuario(id_usuario, nombre, correo, rol, solo_rol=False):
        """Modifica los datos de un usuario (excepto contraseña)."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                if solo_rol:
                    query = "UPDATE usuarios SET rol = %s WHERE id = %s"
                    cursor.execute(query, (rol, id_usuario))
                else:
                    query = "UPDATE usuarios SET nombre = %s, correo = %s, rol = %s WHERE id = %s"
                    cursor.execute(query, (nombre, correo, rol, id_usuario))
                conexion.commit()
                return True
            except Error as e:
                print(f"Error al modificar usuario: {e}")
                return False
            finally:
                cursor.close()
                conexion.close()

    @staticmethod
    def obtener_usuarios_con_roles():
        """Obtiene todos los usuarios con su ID, nombre y rol."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = "SELECT id, nombre, rol FROM usuarios"
                cursor.execute(query)
                usuarios = cursor.fetchall()
                return usuarios
            except Error as e:
                print(f"Error al obtener usuarios con roles: {e}")
                return []
            finally:
                cursor.close()
                conexion.close()

    @staticmethod
    def obtener_inscripciones():
        """Obtiene todas las inscripciones con nombres de estudiante y materia."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                    SELECT i.id_estudiante, i.id_materia,
                           e.nombre AS estudiante,
                           m.nombre AS materia
                    FROM inscripciones i
                    JOIN estudiantes e ON i.id_estudiante = e.id
                    JOIN materias m ON i.id_materia = m.id
                """
                cursor.execute(query)
                return cursor.fetchall()
            except Error as e:
                print(f"Error al obtener inscripciones: {e}")
                return []
            finally:
                cursor.close()
                conexion.close()
        return []

    @staticmethod
    def eliminar_inscripcion(id_estudiante, id_materia):
        """Elimina una inscripción por estudiante y materia."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "DELETE FROM inscripciones WHERE id_estudiante = %s AND id_materia = %s"
                cursor.execute(query, (id_estudiante, id_materia))
                conexion.commit()
                return True
            except Error as e:
                print(f"Error al eliminar inscripción: {e}")
                return False
            finally:
                cursor.close()
                conexion.close()
        return False

    @staticmethod
    def modificar_inscripcion(id_estudiante, id_materia, nuevo_id_estudiante, nuevo_id_materia):
        """Modifica una inscripción cambiando estudiante o materia."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                # Eliminar la inscripción anterior
                cursor.execute("DELETE FROM inscripciones WHERE id_estudiante = %s AND id_materia = %s", (id_estudiante, id_materia))
                # Insertar la nueva inscripción
                cursor.execute("INSERT INTO inscripciones (id_estudiante, id_materia) VALUES (%s, %s)", (nuevo_id_estudiante, nuevo_id_materia))
                conexion.commit()
                return True
            except Error as e:
                print(f"Error al modificar inscripción: {e}")
                return False
            finally:
                cursor.close()
                conexion.close()
        return False

    @staticmethod
    def habilitar_estudiante_inscripcion(id_estudiante, puede_inscribirse):
        """Habilita o deshabilita a un estudiante para inscribirse."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "UPDATE estudiantes SET puede_inscribirse = %s WHERE id = %s"
                cursor.execute(query, (puede_inscribirse, id_estudiante))
                conexion.commit()
                return True
            except Error as e:
                print(f"Error al actualizar permiso de inscripción: {e}")
                return False
            finally:
                cursor.close()
                conexion.close()
        return False


#Metodo para contar el total de inscripciones para las 
    @staticmethod
    def contar_inscripciones():
        """Devuelve el total de inscripciones."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "SELECT COUNT(*) FROM inscripciones"
                cursor.execute(query)
                total = cursor.fetchone()[0]
                return total
            except Exception as e:
                print(f"Error al contar inscripciones: {e}")
                return 0
            finally:
                cursor.close()
                conexion.close()
        return 0