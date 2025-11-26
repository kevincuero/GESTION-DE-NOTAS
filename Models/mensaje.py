# Models/mensaje.py
from Config.database_connection import create_connection
from datetime import datetime

class Mensaje:
    def __init__(self, id=None, id_notificacion=None, id_estudiante=None, id_profesor=None, 
                 id_materia=None, remitente_tipo=None, contenido=None, leido=False, fecha=None):
        self.id = id
        self.id_notificacion = id_notificacion
        self.id_estudiante = id_estudiante
        self.id_profesor = id_profesor
        self.id_materia = id_materia
        self.remitente_tipo = remitente_tipo
        self.contenido = contenido
        self.leido = leido
        self.fecha = fecha

    @staticmethod
    def crear(id_notificacion, id_estudiante, id_profesor, id_materia, remitente_tipo, contenido):
        """Crea un nuevo mensaje de respuesta."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = """
                INSERT INTO mensajes (id_notificacion, id_estudiante, id_profesor, id_materia, 
                                    remitente_tipo, contenido, leido, fecha)
                VALUES (%s, %s, %s, %s, %s, %s, FALSE, NOW())
                """
                cursor.execute(query, (id_notificacion, id_estudiante, id_profesor, id_materia, 
                                      remitente_tipo, contenido))
                conexion.commit()
                mensaje_id = cursor.lastrowid
                cursor.close()
                conexion.close()
                return mensaje_id
            except Exception as e:
                print(f"Error al crear mensaje: {e}")
                return False
            finally:
                if conexion and conexion.is_connected():
                    try:
                        cursor.close()
                    except:
                        pass
                    try:
                        conexion.close()
                    except:
                        pass
        return False

    @staticmethod
    def obtener_por_notificacion(id_notificacion):
        """Obtiene todos los mensajes (respuestas) de una notificación."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT m.id, m.id_notificacion, m.id_estudiante, m.id_profesor, m.id_materia,
                       m.remitente_tipo, m.contenido, m.leido, m.fecha,
                       CASE 
                           WHEN m.remitente_tipo = 'estudiante' THEN e.nombre
                           WHEN m.remitente_tipo = 'profesor' THEN p.nombre
                       END as remitente_nombre
                FROM mensajes m
                LEFT JOIN estudiantes e ON m.id_estudiante = e.id AND m.remitente_tipo = 'estudiante'
                LEFT JOIN profesores p ON m.id_profesor = p.id AND m.remitente_tipo = 'profesor'
                WHERE m.id_notificacion = %s
                ORDER BY m.fecha ASC
                """
                cursor.execute(query, (id_notificacion,))
                mensajes = cursor.fetchall()
                cursor.close()
                conexion.close()
                return mensajes
            except Exception as e:
                print(f"Error al obtener mensajes: {e}")
                return []
            finally:
                if conexion and conexion.is_connected():
                    try:
                        cursor.close()
                    except:
                        pass
                    try:
                        conexion.close()
                    except:
                        pass
        return []

    @staticmethod
    def obtener_conversacion(id_estudiante, id_profesor):
        """Obtiene todas las conversaciones entre un estudiante y un profesor."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT m.id, m.id_notificacion, n.titulo as notificacion_titulo, 
                       m.remitente_tipo, m.contenido, m.leido, m.fecha,
                       CASE 
                           WHEN m.remitente_tipo = 'estudiante' THEN e.nombre
                           WHEN m.remitente_tipo = 'profesor' THEN p.nombre
                       END as remitente_nombre,
                       m.id_materia, mat.nombre as materia_nombre
                FROM mensajes m
                JOIN notificaciones n ON m.id_notificacion = n.id
                LEFT JOIN estudiantes e ON m.id_estudiante = e.id AND m.remitente_tipo = 'estudiante'
                LEFT JOIN profesores p ON m.id_profesor = p.id AND m.remitente_tipo = 'profesor'
                LEFT JOIN materias mat ON m.id_materia = mat.id
                WHERE m.id_estudiante = %s AND m.id_profesor = %s
                ORDER BY m.fecha ASC
                """
                cursor.execute(query, (id_estudiante, id_profesor))
                mensajes = cursor.fetchall()
                cursor.close()
                conexion.close()
                return mensajes
            except Exception as e:
                print(f"Error al obtener conversación: {e}")
                return []
            finally:
                if conexion and conexion.is_connected():
                    try:
                        cursor.close()
                    except:
                        pass
                    try:
                        conexion.close()
                    except:
                        pass
        return []

    @staticmethod
    def marcar_como_leido(id_mensaje):
        """Marca un mensaje como leído."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "UPDATE mensajes SET leido = TRUE WHERE id = %s"
                cursor.execute(query, (id_mensaje,))
                conexion.commit()
                result = cursor.rowcount > 0
                cursor.close()
                conexion.close()
                return result
            except Exception as e:
                print(f"Error al marcar mensaje como leído: {e}")
                return False
            finally:
                if conexion and conexion.is_connected():
                    try:
                        cursor.close()
                    except:
                        pass
                    try:
                        conexion.close()
                    except:
                        pass
        return False

    @staticmethod
    def obtener_no_leidos_count(id_estudiante):
        """Obtiene el conteo de mensajes no leídos del estudiante."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = """
                SELECT COUNT(*) as total FROM mensajes 
                WHERE id_estudiante = %s AND leido = FALSE AND remitente_tipo = 'profesor'
                """
                cursor.execute(query, (id_estudiante,))
                resultado = cursor.fetchone()
                count = resultado[0] if resultado else 0
                cursor.close()
                conexion.close()
                return count
            except Exception as e:
                print(f"Error al contar mensajes no leídos: {e}")
                return 0
            finally:
                if conexion and conexion.is_connected():
                    try:
                        cursor.close()
                    except:
                        pass
                    try:
                        conexion.close()
                    except:
                        pass
        return 0

    @staticmethod
    def obtener_profesores_conversacion(id_estudiante):
        """Obtiene lista de profesores con los que el estudiante tiene conversaciones."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT DISTINCT p.id, p.nombre, 
                       (SELECT COUNT(*) FROM mensajes m 
                        WHERE m.id_estudiante = %s AND m.id_profesor = p.id 
                        AND m.leido = FALSE AND m.remitente_tipo = 'profesor') as no_leidos
                FROM mensajes m
                JOIN profesores p ON m.id_profesor = p.id
                WHERE m.id_estudiante = %s
                ORDER BY m.fecha DESC
                """
                cursor.execute(query, (id_estudiante, id_estudiante))
                profesores = cursor.fetchall()
                cursor.close()
                conexion.close()
                return profesores
            except Exception as e:
                print(f"Error al obtener profesores en conversación: {e}")
                return []
            finally:
                if conexion and conexion.is_connected():
                    try:
                        cursor.close()
                    except:
                        pass
                    try:
                        conexion.close()
                    except:
                        pass
        return []

    @staticmethod
    def eliminar(id_mensaje):
        """Elimina un mensaje."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "DELETE FROM mensajes WHERE id = %s"
                cursor.execute(query, (id_mensaje,))
                conexion.commit()
                result = cursor.rowcount > 0
                cursor.close()
                conexion.close()
                return result
            except Exception as e:
                print(f"Error al eliminar mensaje: {e}")
                return False
            finally:
                if conexion and conexion.is_connected():
                    try:
                        cursor.close()
                    except:
                        pass
                    try:
                        conexion.close()
                    except:
                        pass
        return False
