from Config.database_connection import create_connection
from Models.indice_aprendizaje import IndiceAprendizaje
from Models.evaluacion_indice import EvaluacionIndice
from mysql.connector import Error

class IndicesController:
    
    @staticmethod
    def obtener_materias_profesor(id_profesor):
        """Obtiene las materias asignadas a un profesor."""
        # Usa el método del ProfesorController
        from Controllers.profesor_controller import ProfesorController
        return ProfesorController.obtener_materias_asignadas(id_profesor)

    @staticmethod
    def crear_indice(id_materia, id_profesor, nombre, descripcion, porcentaje, parcial):
        """Crea un nuevo índice de aprendizaje."""
        # Validar que no excedan 4 índices
        total = IndiceAprendizaje.contar_indices_por_materia(id_materia, id_profesor)
        if total >= 4:
            return {"success": False, "message": "No se pueden crear más de 4 índices de aprendizaje por materia"}
        
        # Validar que la suma de porcentajes no exceda 100
        indices = IndiceAprendizaje.obtener_indices_por_materia(id_materia, id_profesor)
        suma_porcentajes = sum(float(idx['porcentaje']) for idx in indices) + float(porcentaje)
        if suma_porcentajes > 100:
            return {"success": False, "message": f"La suma de porcentajes no puede exceder 100%. Suma actual: {suma_porcentajes}%"}
        
        id_indice = IndiceAprendizaje.crear_indice(id_materia, id_profesor, nombre, descripcion, porcentaje, parcial)
        if id_indice:
            return {"success": True, "message": "Índice creado exitosamente", "id_indice": id_indice}
        return {"success": False, "message": "Error al crear el índice"}

    @staticmethod
    def obtener_indices_por_materia(id_materia, id_profesor):
        """Obtiene todos los índices de una materia."""
        return IndiceAprendizaje.obtener_indices_por_materia(id_materia, id_profesor)

    @staticmethod
    def obtener_indices_con_evaluaciones(id_materia):
        """Obtiene índices de una materia con sus evaluaciones."""
        indices = IndiceAprendizaje.obtener_indices_por_materia_sin_profesor(id_materia)
        resumen = []
        
        for indice in indices:
            ultima_evaluacion = EvaluacionIndice.obtener_ultima_evaluacion(indice['id'])
            promedio = EvaluacionIndice.obtener_promedio_dominio(indice['id'])
            
            resumen.append({
                'id': indice['id'],
                'nombre': indice['nombre'],
                'descripcion': indice['descripcion'],
                'porcentaje': indice['porcentaje'],
                'parcial': indice['parcial'],
                'id_materia': indice['id_materia'],
                'id_profesor': indice['id_profesor'],
                'ultima_evaluacion': ultima_evaluacion,
                'promedio_dominio': promedio
            })
        
        return resumen

    @staticmethod
    def actualizar_indice(id_indice, nombre, descripcion, porcentaje, parcial):
        """Actualiza un índice de aprendizaje."""
        indice_actual = IndiceAprendizaje.obtener_indice_por_id(id_indice)
        if not indice_actual:
            return {"success": False, "message": "Índice no encontrado"}
        
        # Validar que la suma de porcentajes no exceda 100
        indices = IndiceAprendizaje.obtener_indices_por_materia(indice_actual['id_materia'], indice_actual['id_profesor'])
        suma_porcentajes = 0
        for idx in indices:
            if idx['id'] != id_indice:
                suma_porcentajes += float(idx['porcentaje'])
        suma_porcentajes += float(porcentaje)
        
        if suma_porcentajes > 100:
            return {"success": False, "message": f"La suma de porcentajes no puede exceder 100%. Suma actual: {suma_porcentajes}%"}
        
        exito = IndiceAprendizaje.actualizar_indice(id_indice, nombre, descripcion, porcentaje, parcial)
        if exito:
            return {"success": True, "message": "Índice actualizado exitosamente"}
        return {"success": False, "message": "Error al actualizar el índice"}

    @staticmethod
    def obtener_indice_por_id(id_indice):
        """Obtiene un índice por su ID."""
        return IndiceAprendizaje.obtener_indice_por_id(id_indice)

    @staticmethod
    def guardar_evaluacion_indice(id_indice, id_profesor, porcentaje_dominio, comentario):
        """Guarda una evaluación grupal de un índice."""
        # Validar porcentaje
        if not (0 <= porcentaje_dominio <= 100):
            return {"success": False, "message": "El porcentaje de dominio debe estar entre 0 y 100"}
        
        id_evaluacion = EvaluacionIndice.crear_evaluacion(id_indice, id_profesor, porcentaje_dominio, comentario)
        if id_evaluacion:
            return {"success": True, "message": "Evaluación registrada exitosamente", "id_evaluacion": id_evaluacion}
        return {"success": False, "message": "Error al registrar la evaluación"}

    @staticmethod
    def obtener_evaluaciones_indice(id_indice):
        """Obtiene todas las evaluaciones de un índice, ordenadas de más reciente a más antigua."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT * FROM evaluaciones_indices
                WHERE id_indice = %s
                ORDER BY fecha_evaluacion DESC
                """
                cursor.execute(query, (id_indice,))
                return cursor.fetchall()
            except Error as e:
                print(f"Error al obtener evaluaciones: {e}")
                return []
            finally:
                cursor.close()
                conexion.close()
        return []

    @staticmethod
    def obtener_resumen_indices(id_materia, id_profesor):
        """Obtiene un resumen completo de todos los índices de una materia."""
        indices = IndiceAprendizaje.obtener_indices_por_materia(id_materia, id_profesor)
        resumen = []
        
        for indice in indices:
            ultima_evaluacion = EvaluacionIndice.obtener_ultima_evaluacion(indice['id'])
            promedio = EvaluacionIndice.obtener_promedio_dominio(indice['id'])
            
            resumen.append({
                'id': indice['id'],
                'nombre': indice['nombre'],
                'descripcion': indice['descripcion'],
                'porcentaje': indice['porcentaje'],
                'parcial': indice['parcial'],
                'ultima_evaluacion': ultima_evaluacion,
                'promedio_dominio': promedio
            })
        
        return resumen

    @staticmethod
    def eliminar_indice(id_indice):
        """Elimina un índice de aprendizaje."""
        exito = IndiceAprendizaje.eliminar_indice(id_indice)
        if exito:
            return {"success": True, "message": "Índice eliminado exitosamente"}
        return {"success": False, "message": "Error al eliminar el índice"}
