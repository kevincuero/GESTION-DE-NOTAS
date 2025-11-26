# Controllers/mensaje_controller.py
"""
Controlador para gestionar mensajes y respuestas entre estudiantes y profesores.
"""
from Config.database_connection import create_connection
from Models.mensaje import Mensaje
from Models.notificacion import Notificacion

class MensajeController:
    
    @staticmethod
    def enviar_respuesta(id_notificacion, id_estudiante, id_profesor, id_materia, contenido):
        """
        Envía una respuesta a una notificación.
        
        Args:
            id_notificacion (int): ID de la notificación original
            id_estudiante (int): ID del estudiante que responde
            id_profesor (int): ID del profesor destinatario
            id_materia (int): ID de la materia
            contenido (str): Contenido del mensaje
        
        Returns:
            dict: {"success": bool, "message": str, "mensaje_id": int}
        """
        try:
            mensaje_id = Mensaje.crear(
                id_notificacion, 
                id_estudiante, 
                id_profesor, 
                id_materia, 
                'estudiante', 
                contenido
            )
            
            if mensaje_id:
                return {
                    "success": True,
                    "message": "Respuesta enviada correctamente.",
                    "mensaje_id": mensaje_id
                }
            else:
                return {
                    "success": False,
                    "message": "Error al enviar la respuesta.",
                    "mensaje_id": None
                }
        except Exception as e:
            print(f"Error en enviar_respuesta: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "mensaje_id": None
            }
    
    @staticmethod
    def obtener_mensajes_notificacion(id_notificacion):
        """
        Obtiene todos los mensajes (respuestas) de una notificación.
        
        Args:
            id_notificacion (int): ID de la notificación
        
        Returns:
            list: Lista de mensajes
        """
        try:
            mensajes = Mensaje.obtener_por_notificacion(id_notificacion)
            return mensajes
        except Exception as e:
            print(f"Error en obtener_mensajes_notificacion: {e}")
            return []
    
    @staticmethod
    def obtener_conversacion(id_estudiante, id_profesor):
        """
        Obtiene la conversación completa entre un estudiante y un profesor.
        
        Args:
            id_estudiante (int): ID del estudiante
            id_profesor (int): ID del profesor
        
        Returns:
            list: Lista de mensajes de la conversación
        """
        try:
            mensajes = Mensaje.obtener_conversacion(id_estudiante, id_profesor)
            return mensajes
        except Exception as e:
            print(f"Error en obtener_conversacion: {e}")
            return []
    
    @staticmethod
    def marcar_como_leido(id_mensaje):
        """
        Marca un mensaje como leído.
        
        Args:
            id_mensaje (int): ID del mensaje
        
        Returns:
            dict: {"success": bool, "message": str}
        """
        try:
            result = Mensaje.marcar_como_leido(id_mensaje)
            if result:
                return {
                    "success": True,
                    "message": "Mensaje marcado como leído."
                }
            else:
                return {
                    "success": False,
                    "message": "Error al marcar como leído."
                }
        except Exception as e:
            print(f"Error en marcar_como_leido: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    @staticmethod
    def obtener_profesores_con_conversacion(id_estudiante):
        """
        Obtiene lista de profesores con los que hay conversación.
        
        Args:
            id_estudiante (int): ID del estudiante
        
        Returns:
            list: Lista de profesores
        """
        try:
            profesores = Mensaje.obtener_profesores_conversacion(id_estudiante)
            return profesores
        except Exception as e:
            print(f"Error en obtener_profesores_con_conversacion: {e}")
            return []
    
    @staticmethod
    def obtener_notificacion_con_detalles(id_notificacion, id_estudiante):
        """
        Obtiene una notificación con sus detalles y conversación.
        
        Args:
            id_notificacion (int): ID de la notificación
            id_estudiante (int): ID del estudiante
        
        Returns:
            dict: Notificación con mensajes
        """
        try:
            # Obtener notificación
            notificacion = Notificacion.obtener_por_id(id_notificacion)
            
            if not notificacion:
                return None
            
            # Obtener mensajes de esta notificación
            mensajes = Mensaje.obtener_por_notificacion(id_notificacion)
            
            return {
                "notificacion": notificacion,
                "mensajes": mensajes
            }
        except Exception as e:
            print(f"Error en obtener_notificacion_con_detalles: {e}")
            return None
    
    @staticmethod
    def enviar_mensaje_inicial(id_estudiante, id_profesor, id_materia, titulo, contenido):
        """
        Envía un mensaje inicial a un profesor iniciando una conversación.
        
        Args:
            id_estudiante (int): ID del estudiante
            id_profesor (int): ID del profesor
            id_materia (int): ID de la materia
            titulo (str): Título del mensaje
            contenido (str): Contenido del mensaje
        
        Returns:
            dict: {"success": bool, "message": str, "notificacion_id": int}
        """
        try:
            # Crear notificación inicial (como si fuera del profesor al estudiante)
            # Pero es iniciada por el estudiante
            notificacion_id = Notificacion.crear(
                id_estudiante,
                id_profesor,
                titulo,
                contenido
            )
            
            if notificacion_id:
                # Crear el mensaje inicial como respuesta
                mensaje_id = Mensaje.crear(
                    notificacion_id,
                    id_estudiante,
                    id_profesor,
                    id_materia,
                    'estudiante',
                    contenido
                )
                
                if mensaje_id:
                    return {
                        "success": True,
                        "message": "Mensaje enviado al profesor.",
                        "notificacion_id": notificacion_id,
                        "mensaje_id": mensaje_id
                    }
            
            return {
                "success": False,
                "message": "Error al enviar el mensaje.",
                "notificacion_id": None
            }
        except Exception as e:
            print(f"Error en enviar_mensaje_inicial: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "notificacion_id": None
            }
