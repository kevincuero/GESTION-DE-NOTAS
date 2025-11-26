# Models/notificacion.py
from Config.database_connection import create_connection
from datetime import datetime

class Notificacion:
    def __init__(self, id=None, id_estudiante=None, id_profesor=None, titulo=None, mensaje=None, fecha=None, leida=False):
        self.id = id
        self.id_estudiante = id_estudiante
        self.id_profesor = id_profesor
        self.titulo = titulo
        self.mensaje = mensaje
        self.fecha = fecha
        self.leida = leida

    @staticmethod
    def crear(id_estudiante, id_profesor, titulo, mensaje):
        """Crea una nueva notificación en la BD (SIN envío de correos)."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = """
                INSERT INTO notificaciones (id_estudiante, id_profesor, titulo, mensaje, leida, fecha)
                VALUES (%s, %s, %s, %s, FALSE, NOW())
                """
                cursor.execute(query, (id_estudiante, id_profesor, titulo, mensaje))
                conexion.commit()
                notification_id = cursor.lastrowid
                cursor.close()
                conexion.close()
                return notification_id
            except Exception as e:
                print(f"Error al crear notificación: {e}")
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
    def crear_multiples(id_estudiantes, id_profesor, titulo, mensaje):
        """Crea notificaciones para múltiples estudiantes."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = """
                INSERT INTO notificaciones (id_estudiante, id_profesor, titulo, mensaje, leida, fecha)
                VALUES (%s, %s, %s, %s, FALSE, NOW())
                """
                count = 0
                for id_estudiante in id_estudiantes:
                    cursor.execute(query, (id_estudiante, id_profesor, titulo, mensaje))
                    count += 1
                conexion.commit()
                cursor.close()
                conexion.close()
                return count
            except Exception as e:
                print(f"Error al crear notificaciones múltiples: {e}")
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
    def obtener_por_estudiante(id_estudiante, leidas=None):
        """
        Obtiene todas las notificaciones de un estudiante (ordenadas por fecha DESC).
        Si leidas=True, retorna solo leídas. Si leidas=False, retorna solo no leídas.
        Si leidas=None, retorna todas.
        """
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT n.id, n.titulo, n.mensaje, n.fecha, n.leida, 
                       p.nombre as profesor_nombre, p.id as id_profesor
                FROM notificaciones n
                JOIN profesores p ON n.id_profesor = p.id
                WHERE n.id_estudiante = %s
                """
                params = [id_estudiante]
                
                if leidas is not None:
                    query += " AND n.leida = %s"
                    params.append(leidas)
                
                query += " ORDER BY n.fecha DESC"
                
                cursor.execute(query, params)
                notificaciones = cursor.fetchall()
                cursor.close()
                conexion.close()
                return notificaciones
            except Exception as e:
                print(f"Error al obtener notificaciones: {e}")
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
    def obtener_por_id(id_notificacion):
        """Obtiene una notificación específica por su ID."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT n.*, p.nombre as profesor_nombre
                FROM notificaciones n
                JOIN profesores p ON n.id_profesor = p.id
                WHERE n.id = %s
                """
                cursor.execute(query, (id_notificacion,))
                notificacion = cursor.fetchone()
                cursor.close()
                conexion.close()
                return notificacion
            except Exception as e:
                print(f"Error al obtener notificación: {e}")
                return None
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
        return None

    @staticmethod
    def marcar_como_leida(id_notificacion):
        """Marca una notificación como leída."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "UPDATE notificaciones SET leida = TRUE WHERE id = %s"
                cursor.execute(query, (id_notificacion,))
                conexion.commit()
                result = cursor.rowcount > 0
                cursor.close()
                conexion.close()
                return result
            except Exception as e:
                print(f"Error al marcar notificación como leída: {e}")
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
    def marcar_multiples_como_leidas(id_notificaciones):
        """Marca múltiples notificaciones como leídas."""
        if not id_notificaciones:
            return 0
        
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                placeholders = ','.join(['%s'] * len(id_notificaciones))
                query = f"UPDATE notificaciones SET leida = TRUE WHERE id IN ({placeholders})"
                cursor.execute(query, id_notificaciones)
                conexion.commit()
                count = cursor.rowcount
                cursor.close()
                conexion.close()
                return count
            except Exception as e:
                print(f"Error al marcar múltiples notificaciones como leídas: {e}")
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
    def marcar_todas_como_leidas(id_estudiante):
        """Marca todas las notificaciones de un estudiante como leídas."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "UPDATE notificaciones SET leida = TRUE WHERE id_estudiante = %s AND leida = FALSE"
                cursor.execute(query, (id_estudiante,))
                conexion.commit()
                count = cursor.rowcount
                cursor.close()
                conexion.close()
                return count
            except Exception as e:
                print(f"Error al marcar todas las notificaciones como leídas: {e}")
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
    def obtener_no_leidas_count(id_estudiante):
        """Obtiene el conteo de notificaciones no leídas."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "SELECT COUNT(*) as total FROM notificaciones WHERE id_estudiante = %s AND leida = FALSE"
                cursor.execute(query, (id_estudiante,))
                resultado = cursor.fetchone()
                count = resultado[0] if resultado else 0
                cursor.close()
                conexion.close()
                return count
            except Exception as e:
                print(f"Error al contar notificaciones no leídas: {e}")
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
    def eliminar(id_notificacion):
        """Elimina una notificación."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "DELETE FROM notificaciones WHERE id = %s"
                cursor.execute(query, (id_notificacion,))
                conexion.commit()
                result = cursor.rowcount > 0
                cursor.close()
                conexion.close()
                return result
            except Exception as e:
                print(f"Error al eliminar notificación: {e}")
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
    def obtener_por_profesor(id_profesor):
        """Obtiene todas las notificaciones enviadas por un profesor."""
        conexion = create_connection()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                query = """
                SELECT n.id, n.titulo, n.mensaje, n.fecha, n.leida,
                       e.nombre as estudiante_nombre, e.id as id_estudiante
                FROM notificaciones n
                JOIN estudiantes e ON n.id_estudiante = e.id
                WHERE n.id_profesor = %s
                ORDER BY n.fecha DESC
                """
                cursor.execute(query, (id_profesor,))
                notificaciones = cursor.fetchall()
                cursor.close()
                conexion.close()
                return notificaciones
            except Exception as e:
                print(f"Error al obtener notificaciones del profesor: {e}")
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