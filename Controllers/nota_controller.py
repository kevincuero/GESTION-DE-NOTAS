from Config.database_connection import create_connection
from Models.nota import Nota
from Models.materia import Materia

class NotaController:
    
    @staticmethod
    def asignar_nota(id_estudiante, id_profesor, id_materia, nota, tipo_evaluacion='parcial', comentario=''):
        """Asigna una nueva nota a un estudiante con tipo de evaluación."""
        nueva_nota = Nota(
            id_estudiante=id_estudiante,
            id_profesor=id_profesor,
            id_materia=id_materia,
            nota=nota,
            tipo_evaluacion=tipo_evaluacion,
            comentario=comentario
        )
        return nueva_nota.guardar()

    @staticmethod
    def obtener_notas_estudiante(id_estudiante):
        """Obtiene todas las notas de un estudiante con detalles de materia."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT n.*, m.nombre as materia, p.nombre as profesor
                FROM notas n
                JOIN materias m ON n.id_materia = m.id
                JOIN profesores p ON n.id_profesor = p.id
                WHERE n.id_estudiante = %s
                ORDER BY m.nombre, n.tipo_evaluacion, n.fecha DESC
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

    @staticmethod
    def obtener_notas_por_materia_agrupadas(id_estudiante):
        """Obtiene las notas agrupadas por materia para la vista de estudiante."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT 
                    m.id as materia_id,
                    m.nombre as materia,
                    n.id,
                    n.nota,
                    n.tipo_evaluacion,
                    n.comentario,
                    n.fecha,
                    p.nombre as profesor
                FROM notas n
                JOIN materias m ON n.id_materia = m.id
                JOIN profesores p ON n.id_profesor = p.id
                WHERE n.id_estudiante = %s
                ORDER BY m.nombre, n.tipo_evaluacion, n.fecha DESC
                """
                cursor.execute(query, (id_estudiante,))
                notas = cursor.fetchall()
                
                # Agrupar por materia
                materias_dict = {}
                for nota in notas:
                    materia_nombre = nota['materia']
                    if materia_nombre not in materias_dict:
                        materias_dict[materia_nombre] = {
                            'materia_id': nota['materia_id'],
                            'nombre': materia_nombre,
                            'notas': []
                        }
                    materias_dict[materia_nombre]['notas'].append(nota)
                
                return list(materias_dict.values())
            except Exception as e:
                print(f"Error al obtener notas agrupadas: {e}")
                return []
            finally:
                if conexion.is_connected():
                    cursor.close()
                    conexion.close()
        return []

    @staticmethod
    def obtener_notas_por_tipo(id_estudiante, id_materia, tipo_evaluacion):
        """Obtiene notas de un estudiante por tipo de evaluación en una materia."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT n.*, m.nombre as materia, p.nombre as profesor
                FROM notas n
                JOIN materias m ON n.id_materia = m.id
                JOIN profesores p ON n.id_profesor = p.id
                WHERE n.id_estudiante = %s AND n.id_materia = %s AND n.tipo_evaluacion = %s
                ORDER BY n.fecha DESC
                """
                cursor.execute(query, (id_estudiante, id_materia, tipo_evaluacion))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener notas por tipo: {e}")
                return []
            finally:
                if conexion.is_connected():
                    cursor.close()
                    conexion.close()
        return []

    @staticmethod
    def obtener_tipos_evaluacion():
        """Obtiene todos los tipos de evaluación disponibles."""
        tipos = [
            'Parcial 1',
            'Parcial 2',
            'Parcial 3',
            'Quiz',
            'Tarea',
            'Proyecto',
            'Participación',
            'Examen Final'
        ]
        return tipos

    @staticmethod
    def actualizar_nota(id_nota, nota, tipo_evaluacion, comentario):
        """Actualiza una nota existente."""
        nota_obj = Nota.obtener_por_id(id_nota)
        if nota_obj:
            nota_obj['nota'] = nota
            nota_obj['tipo_evaluacion'] = tipo_evaluacion
            nota_obj['comentario'] = comentario
            
            nota_actualizada = Nota(
                id=id_nota,
                nota=nota,
                tipo_evaluacion=tipo_evaluacion,
                comentario=comentario
            )
            return nota_actualizada.actualizar()
        return False

    @staticmethod
    def eliminar_nota(id_nota):
        """Elimina una nota."""
        nota_obj = Nota(id=id_nota)
        return nota_obj.eliminar()

    @staticmethod
    def calcular_promedio_por_tipo(id_estudiante, id_materia, tipo_evaluacion):
        """Calcula el promedio de un tipo de evaluación en una materia."""
        notas = NotaController.obtener_notas_por_tipo(id_estudiante, id_materia, tipo_evaluacion)
        if not notas:
            return 0.0
        
        total = sum([float(nota['nota']) for nota in notas])
        promedio = total / len(notas)
        return round(promedio, 2)

    @staticmethod
    def calcular_promedio_materia(id_estudiante, id_materia):
        """Calcula el promedio general de un estudiante en una materia."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT AVG(nota) as promedio
                FROM notas
                WHERE id_estudiante = %s AND id_materia = %s
                """
                cursor.execute(query, (id_estudiante, id_materia))
                resultado = cursor.fetchone()
                return round(float(resultado['promedio']), 2) if resultado['promedio'] else 0.0
            except Exception as e:
                print(f"Error al calcular promedio: {e}")
                return 0.0
            finally:
                if conexion.is_connected():
                    cursor.close()
                    conexion.close()
        return 0.0