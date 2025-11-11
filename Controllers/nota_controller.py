from socket import create_connection
from Models.nota import Nota
from Models.materia import Materia

class NotaController:
    @staticmethod
    def asignar_nota(id_estudiante, id_materia, nota):
        nueva_nota = Nota(
            id_estudiante=id_estudiante,
            id_materia=id_materia,
            calificacion=nota
        )
        return nueva_nota.guardar()

    @staticmethod
    def obtener_notas_estudiante(id_estudiante):
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT n.*, m.nombre as materia 
                FROM notas n
                JOIN materias m ON n.id_materia = m.id
                WHERE n.id_estudiante = %s
                """
                cursor.execute(query, (id_estudiante,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener notas: {e}")
                return []
            finally:
                if conexion.is_connected():
                    cursor.close()
                    conexion.close()
        return []