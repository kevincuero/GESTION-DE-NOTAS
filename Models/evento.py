from Config.database_connection import create_connection
from datetime import datetime

class Evento:
    """Modelo para manejar eventos del calendario del estudiante"""

    @staticmethod
    def crear_evento(id_estudiante, titulo, descripcion, fecha, hora_inicio, hora_fin, color='#4facfe'):
        """Crear un nuevo evento para el estudiante"""
        try:
            conexion = create_connection()
            cursor = conexion.cursor()
            
            query = """
            INSERT INTO eventos (id_estudiante, titulo, descripcion, fecha, hora_inicio, hora_fin, color, creado_en)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            cursor.execute(query, (id_estudiante, titulo, descripcion, fecha, hora_inicio, hora_fin, color))
            conexion.commit()
            evento_id = cursor.lastrowid
            cursor.close()
            conexion.close()
            
            return {'success': True, 'id': evento_id, 'message': 'Evento creado exitosamente'}
        except Exception as e:
            return {'success': False, 'message': f'Error al crear evento: {str(e)}'}

    @staticmethod
    def obtener_eventos(id_estudiante):
        """Obtener todos los eventos del estudiante"""
        try:
            conexion = create_connection()
            cursor = conexion.cursor()
            
            query = """
            SELECT id, titulo, descripcion, fecha, hora_inicio, hora_fin, color, creado_en
            FROM eventos
            WHERE id_estudiante = %s
            ORDER BY fecha, hora_inicio
            """
            
            cursor.execute(query, (id_estudiante,))
            eventos = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            eventos_list = []
            for evento in eventos:
                eventos_list.append({
                    'id': evento[0],
                    'titulo': evento[1],
                    'descripcion': evento[2],
                    'fecha': str(evento[3]),
                    'hora_inicio': str(evento[4]),
                    'hora_fin': str(evento[5]),
                    'color': evento[6],
                    'creado_en': str(evento[7])
                })
            
            return eventos_list
        except Exception as e:
            print(f'Error al obtener eventos: {str(e)}')
            return []

    @staticmethod
    def obtener_evento_por_id(evento_id, id_estudiante):
        """Obtener un evento específico por ID"""
        try:
            conexion = create_connection()
            cursor = conexion.cursor()
            
            query = """
            SELECT id, titulo, descripcion, fecha, hora_inicio, hora_fin, color, creado_en
            FROM eventos
            WHERE id = %s AND id_estudiante = %s
            """
            
            cursor.execute(query, (evento_id, id_estudiante))
            evento = cursor.fetchone()
            cursor.close()
            conexion.close()
            
            if evento:
                return {
                    'id': evento[0],
                    'titulo': evento[1],
                    'descripcion': evento[2],
                    'fecha': str(evento[3]),
                    'hora_inicio': str(evento[4]),
                    'hora_fin': str(evento[5]),
                    'color': evento[6],
                    'creado_en': str(evento[7])
                }
            return None
        except Exception as e:
            print(f'Error al obtener evento: {str(e)}')
            return None

    @staticmethod
    def actualizar_evento(evento_id, id_estudiante, titulo, descripcion, fecha, hora_inicio, hora_fin, color):
        """Actualizar un evento existente"""
        try:
            conexion = create_connection()
            cursor = conexion.cursor()
            
            query = """
            UPDATE eventos
            SET titulo = %s, descripcion = %s, fecha = %s, hora_inicio = %s, hora_fin = %s, color = %s
            WHERE id = %s AND id_estudiante = %s
            """
            
            cursor.execute(query, (titulo, descripcion, fecha, hora_inicio, hora_fin, color, evento_id, id_estudiante))
            conexion.commit()
            cursor.close()
            conexion.close()
            
            return {'success': True, 'message': 'Evento actualizado exitosamente'}
        except Exception as e:
            return {'success': False, 'message': f'Error al actualizar evento: {str(e)}'}

    @staticmethod
    def eliminar_evento(evento_id, id_estudiante):
        """Eliminar un evento"""
        try:
            conexion = create_connection()
            cursor = conexion.cursor()
            
            query = """
            DELETE FROM eventos
            WHERE id = %s AND id_estudiante = %s
            """
            
            cursor.execute(query, (evento_id, id_estudiante))
            conexion.commit()
            cursor.close()
            conexion.close()
            
            return {'success': True, 'message': 'Evento eliminado exitosamente'}
        except Exception as e:
            return {'success': False, 'message': f'Error al eliminar evento: {str(e)}'}

    @staticmethod
    def obtener_eventos_por_fecha(id_estudiante, fecha):
        """Obtener eventos de un día específico"""
        try:
            conexion = create_connection()
            cursor = conexion.cursor()
            
            query = """
            SELECT id, titulo, descripcion, fecha, hora_inicio, hora_fin, color, creado_en
            FROM eventos
            WHERE id_estudiante = %s AND fecha = %s
            ORDER BY hora_inicio
            """
            
            cursor.execute(query, (id_estudiante, fecha))
            eventos = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            eventos_list = []
            for evento in eventos:
                eventos_list.append({
                    'id': evento[0],
                    'titulo': evento[1],
                    'descripcion': evento[2],
                    'fecha': str(evento[3]),
                    'hora_inicio': str(evento[4]),
                    'hora_fin': str(evento[5]),
                    'color': evento[6],
                    'creado_en': str(evento[7])
                })
            
            return eventos_list
        except Exception as e:
            print(f'Error al obtener eventos por fecha: {str(e)}')
            return []

    @staticmethod
    def obtener_eventos_mes(id_estudiante, anio, mes):
        """Obtener eventos de un mes específico"""
        try:
            conexion = create_connection()
            cursor = conexion.cursor()
            
            query = """
            SELECT id, titulo, descripcion, fecha, hora_inicio, hora_fin, color, creado_en
            FROM eventos
            WHERE id_estudiante = %s AND YEAR(fecha) = %s AND MONTH(fecha) = %s
            ORDER BY fecha, hora_inicio
            """
            
            cursor.execute(query, (id_estudiante, anio, mes))
            eventos = cursor.fetchall()
            cursor.close()
            conexion.close()
            
            eventos_list = []
            for evento in eventos:
                eventos_list.append({
                    'id': evento[0],
                    'titulo': evento[1],
                    'descripcion': evento[2],
                    'fecha': str(evento[3]),
                    'hora_inicio': str(evento[4]),
                    'hora_fin': str(evento[5]),
                    'color': evento[6],
                    'creado_en': str(evento[7])
                })
            
            return eventos_list
        except Exception as e:
            print(f'Error al obtener eventos del mes: {str(e)}')
            return []
