"""
Controllers/notificacion_controller.py
Controlador para gestionar todas las operaciones de notificaciones en la plataforma.
"""
from Config.database_connection import create_connection
from Models.notificacion import Notificacion
from datetime import datetime

class NotificacionController:
    
    @staticmethod
    def enviar_notificacion_a_estudiante(id_estudiante, id_profesor, titulo, mensaje):
        """
        Envía una notificación a un estudiante específico.
        
        Args:
            id_estudiante (int): ID del estudiante receptor
            id_profesor (int): ID del profesor remitente
            titulo (str): Título de la notificación
            mensaje (str): Contenido del mensaje
        
        Returns:
            dict: {"success": bool, "message": str, "notification_id": int or None}
        """
        try:
            notification_id = Notificacion.crear(id_estudiante, id_profesor, titulo, mensaje)
            if notification_id:
                return {
                    "success": True,
                    "message": "Notificación enviada correctamente.",
                    "notification_id": notification_id
                }
            else:
                return {
                    "success": False,
                    "message": "Error al crear la notificación.",
                    "notification_id": None
                }
        except Exception as e:
            print(f"Error en enviar_notificacion_a_estudiante: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "notification_id": None
            }
    
    @staticmethod
    def enviar_notificacion_a_multiples(id_estudiantes, id_profesor, titulo, mensaje):
        """
        Envía una notificación a múltiples estudiantes.
        
        Args:
            id_estudiantes (list): Lista de IDs de estudiantes
            id_profesor (int): ID del profesor remitente
            titulo (str): Título de la notificación
            mensaje (str): Contenido del mensaje
        
        Returns:
            dict: {"success": bool, "message": str, "count": int}
        """
        try:
            if not id_estudiantes:
                return {
                    "success": False,
                    "message": "No hay estudiantes para enviar la notificación.",
                    "count": 0
                }
            
            count = Notificacion.crear_multiples(id_estudiantes, id_profesor, titulo, mensaje)
            if count > 0:
                return {
                    "success": True,
                    "message": f"Notificación enviada a {count} estudiante(s).",
                    "count": count
                }
            else:
                return {
                    "success": False,
                    "message": "Error al enviar notificaciones.",
                    "count": 0
                }
        except Exception as e:
            print(f"Error en enviar_notificacion_a_multiples: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "count": 0
            }
    
    @staticmethod
    def enviar_notificacion_a_clase(id_materia, id_profesor, titulo, mensaje):
        """
        Envía una notificación a todos los estudiantes inscritos en una materia.
        
        Args:
            id_materia (int): ID de la materia
            id_profesor (int): ID del profesor remitente
            titulo (str): Título de la notificación
            mensaje (str): Contenido del mensaje
        
        Returns:
            dict: {"success": bool, "message": str, "count": int}
        """
        try:
            conexion = create_connection()
            if not conexion:
                return {
                    "success": False,
                    "message": "Error de conexión a la base de datos.",
                    "count": 0
                }
            
            cursor = conexion.cursor(dictionary=True)
            
            # Obtener todos los estudiantes inscritos en la materia
            cursor.execute("""
                SELECT DISTINCT e.id
                FROM estudiantes e
                INNER JOIN inscripciones i ON e.id = i.id_estudiante
                WHERE i.id_materia = %s
            """, (id_materia,))
            
            estudiantes = cursor.fetchall()
            id_estudiantes = [est['id'] for est in estudiantes]
            
            cursor.close()
            conexion.close()
            
            if not id_estudiantes:
                return {
                    "success": False,
                    "message": "No hay estudiantes inscritos en esta materia.",
                    "count": 0
                }
            
            # Enviar a todos los estudiantes
            return NotificacionController.enviar_notificacion_a_multiples(
                id_estudiantes, id_profesor, titulo, mensaje
            )
        
        except Exception as e:
            print(f"Error en enviar_notificacion_a_clase: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "count": 0
            }
    
    @staticmethod
    def obtener_notificaciones_estudiante(id_estudiante, solo_no_leidas=False):
        """
        Obtiene las notificaciones de un estudiante.
        
        Args:
            id_estudiante (int): ID del estudiante
            solo_no_leidas (bool): Si True, retorna solo no leídas
        
        Returns:
            list: Lista de notificaciones
        """
        try:
            leidas = None if not solo_no_leidas else False
            notificaciones = Notificacion.obtener_por_estudiante(id_estudiante, leidas)
            return notificaciones
        except Exception as e:
            print(f"Error en obtener_notificaciones_estudiante: {e}")
            return []
    
    @staticmethod
    def obtener_notificaciones_sin_leer(id_estudiante):
        """Obtiene solo las notificaciones no leídas de un estudiante."""
        return NotificacionController.obtener_notificaciones_estudiante(
            id_estudiante, solo_no_leidas=True
        )
    
    @staticmethod
    def marcar_como_leida(id_notificacion):
        """
        Marca una notificación como leída.
        
        Args:
            id_notificacion (int): ID de la notificación
        
        Returns:
            dict: {"success": bool, "message": str}
        """
        try:
            result = Notificacion.marcar_como_leida(id_notificacion)
            if result:
                return {
                    "success": True,
                    "message": "Notificación marcada como leída."
                }
            else:
                return {
                    "success": False,
                    "message": "No se pudo marcar la notificación."
                }
        except Exception as e:
            print(f"Error en marcar_como_leida: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    @staticmethod
    def marcar_multiples_como_leidas(id_notificaciones):
        """
        Marca múltiples notificaciones como leídas.
        
        Args:
            id_notificaciones (list): Lista de IDs de notificaciones
        
        Returns:
            dict: {"success": bool, "message": str, "count": int}
        """
        try:
            if not id_notificaciones:
                return {
                    "success": False,
                    "message": "No hay notificaciones para marcar.",
                    "count": 0
                }
            
            count = Notificacion.marcar_multiples_como_leidas(id_notificaciones)
            return {
                "success": True,
                "message": f"{count} notificación(es) marcada(s) como leída(s).",
                "count": count
            }
        except Exception as e:
            print(f"Error en marcar_multiples_como_leidas: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "count": 0
            }
    
    @staticmethod
    def marcar_todas_como_leidas(id_estudiante):
        """
        Marca todas las notificaciones no leídas de un estudiante como leídas.
        
        Args:
            id_estudiante (int): ID del estudiante
        
        Returns:
            dict: {"success": bool, "message": str, "count": int}
        """
        try:
            count = Notificacion.marcar_todas_como_leidas(id_estudiante)
            return {
                "success": True,
                "message": f"{count} notificación(es) marcada(s) como leída(s).",
                "count": count
            }
        except Exception as e:
            print(f"Error en marcar_todas_como_leidas: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "count": 0
            }
    
    @staticmethod
    def obtener_conteo_no_leidas(id_estudiante):
        """
        Obtiene el conteo de notificaciones no leídas.
        
        Args:
            id_estudiante (int): ID del estudiante
        
        Returns:
            int: Número de notificaciones no leídas
        """
        try:
            return Notificacion.obtener_no_leidas_count(id_estudiante)
        except Exception as e:
            print(f"Error en obtener_conteo_no_leidas: {e}")
            return 0
    
    @staticmethod
    def eliminar_notificacion(id_notificacion):
        """
        Elimina una notificación.
        
        Args:
            id_notificacion (int): ID de la notificación
        
        Returns:
            dict: {"success": bool, "message": str}
        """
        try:
            result = Notificacion.eliminar(id_notificacion)
            if result:
                return {
                    "success": True,
                    "message": "Notificación eliminada correctamente."
                }
            else:
                return {
                    "success": False,
                    "message": "No se pudo eliminar la notificación."
                }
        except Exception as e:
            print(f"Error en eliminar_notificacion: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    @staticmethod
    def obtener_notificaciones_profesor(id_profesor):
        """
        Obtiene todas las notificaciones enviadas por un profesor.
        
        Args:
            id_profesor (int): ID del profesor
        
        Returns:
            list: Lista de notificaciones enviadas
        """
        try:
            return Notificacion.obtener_por_profesor(id_profesor)
        except Exception as e:
            print(f"Error en obtener_notificaciones_profesor: {e}")
            return []
    
    @staticmethod
    def obtener_notificacion_por_id(id_notificacion):
        """
        Obtiene una notificación específica por su ID.
        
        Args:
            id_notificacion (int): ID de la notificación
        
        Returns:
            dict: Datos de la notificación o None
        """
        try:
            return Notificacion.obtener_por_id(id_notificacion)
        except Exception as e:
            print(f"Error en obtener_notificacion_por_id: {e}")
            return None
    
    @staticmethod
    def crear_notificacion_sistema(id_estudiante, titulo, mensaje):
        """
        Crea una notificación del sistema (sin profesor específico).
        Usa id_profesor = 0 para identificarlas como del sistema.
        
        Args:
            id_estudiante (int): ID del estudiante
            titulo (str): Título de la notificación
            mensaje (str): Contenido del mensaje
        
        Returns:
            dict: {"success": bool, "message": str, "notification_id": int or None}
        """
        try:
            # Usar id_profesor = 0 para notificaciones del sistema
            notification_id = Notificacion.crear(id_estudiante, 0, titulo, mensaje)
            if notification_id:
                return {
                    "success": True,
                    "message": "Notificación del sistema creada correctamente.",
                    "notification_id": notification_id
                }
            else:
                return {
                    "success": False,
                    "message": "Error al crear la notificación del sistema.",
                    "notification_id": None
                }
        except Exception as e:
            print(f"Error en crear_notificacion_sistema: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "notification_id": None
            }
