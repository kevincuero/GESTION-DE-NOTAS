from Config.database_connection import create_connection

class Estudiante:
    def __init__(self, id, nombre, correo, contraseña):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.contraseña = contraseña

    @staticmethod
    def obtener_por_id(id_estudiante):
        """Obtiene un estudiante por su ID."""
        conexion = create_connection()
        if conexion:
            try:
                with conexion.cursor(dictionary=True) as cursor:
                    query = "SELECT * FROM estudiantes WHERE id = %s"
                    cursor.execute(query, (id_estudiante,))
                    estudiante_data = cursor.fetchone()
                    if estudiante_data:
                        return Estudiante(
                            id=estudiante_data['id'],
                            nombre=estudiante_data['nombre'],
                            correo=estudiante_data['correo'],
                            contraseña=estudiante_data['contraseña']
                        )
            except Exception as e:
                print(f"Error al obtener estudiante por ID: {e}")
            finally:
                conexion.close()
        return None

    @staticmethod
    def obtener_notas(id_estudiante):
        """Obtiene las notas de un estudiante por su ID."""
        conexion = create_connection()
        if conexion:
            try:
                with conexion.cursor(dictionary=True) as cursor:
                    query = """
                        SELECT m.nombre AS materia, n.nota
                        FROM notas n
                        JOIN materias m ON n.id_materia = m.id
                        WHERE n.id_estudiante = %s
                    """
                    cursor.execute(query, (id_estudiante,))
                    return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener las notas del estudiante: {e}")
            finally:
                conexion.close()
        return []

    @staticmethod
    def obtener_todos():
        """Obtiene todos los estudiantes."""
        conexion = create_connection()
        if conexion:
            try:
                with conexion.cursor(dictionary=True) as cursor:
                    query = "SELECT * FROM estudiantes"
                    cursor.execute(query)
                    return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener todos los estudiantes: {e}")
            finally:
                conexion.close()
        return []

    def guardar(self):
        """Guarda un nuevo estudiante en la base de datos."""
        conexion = create_connection()
        if conexion:
            try:
                with conexion.cursor() as cursor:
                    query = """
                        INSERT INTO estudiantes (nombre, correo, contraseña)
                        VALUES (%s, %s, %s)
                    """
                    cursor.execute(query, (self.nombre, self.correo, self.contraseña))
                    conexion.commit()
                    self.id = cursor.lastrowid
                    print("Estudiante guardado correctamente.")
            except Exception as e:
                print(f"Error al guardar el estudiante: {e}")
            finally:
                conexion.close()

    def actualizar(self):
        """Actualiza los datos de un estudiante existente."""
        conexion = create_connection()
        if conexion:
            try:
                with conexion.cursor() as cursor:
                    query = """
                        UPDATE estudiantes
                        SET nombre = %s, correo = %s, contraseña = %s
                        WHERE id = %s
                    """
                    cursor.execute(query, (self.nombre, self.correo, self.contraseña, self.id))
                    conexion.commit()
                    print("Estudiante actualizado correctamente.")
            except Exception as e:
                print(f"Error al actualizar el estudiante: {e}")
            finally:
                conexion.close()

    def eliminar(self):
        """Elimina un estudiante de la base de datos."""
        conexion = create_connection()
        if conexion:
            try:
                with conexion.cursor() as cursor:
                    query = "DELETE FROM estudiantes WHERE id = %s"
                    cursor.execute(query, (self.id,))
                    conexion.commit()
                    print("Estudiante eliminado correctamente.")
            except Exception as e:
                print(f"Error al eliminar el estudiante: {e}")
            finally:
                conexion.close()