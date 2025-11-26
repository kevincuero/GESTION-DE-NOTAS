from Models.evento import Evento

class EventoController:
    """Controlador para manejar la lógica de eventos del estudiante"""

    @staticmethod
    def crear_evento(id_estudiante, datos):
        """Crear un nuevo evento"""
        try:
            titulo = datos.get('titulo')
            descripcion = datos.get('descripcion', '')
            fecha = datos.get('fecha')
            hora_inicio = datos.get('hora_inicio')
            hora_fin = datos.get('hora_fin')
            color = datos.get('color', '#4facfe')

            # Validaciones
            if not titulo or not fecha or not hora_inicio or not hora_fin:
                return {'success': False, 'message': 'Faltan datos requeridos'}

            if hora_inicio >= hora_fin:
                return {'success': False, 'message': 'La hora de inicio debe ser anterior a la hora de fin'}

            resultado = Evento.crear_evento(
                id_estudiante, titulo, descripcion, fecha, hora_inicio, hora_fin, color
            )
            return resultado
        except Exception as e:
            return {'success': False, 'message': f'Error en el controlador: {str(e)}'}

    @staticmethod
    def obtener_eventos(id_estudiante):
        """Obtener todos los eventos del estudiante"""
        try:
            eventos = Evento.obtener_eventos(id_estudiante)
            return {'success': True, 'eventos': eventos}
        except Exception as e:
            return {'success': False, 'message': f'Error al obtener eventos: {str(e)}'}

    @staticmethod
    def obtener_evento(evento_id, id_estudiante):
        """Obtener un evento específico"""
        try:
            evento = Evento.obtener_evento_por_id(evento_id, id_estudiante)
            if evento:
                return {'success': True, 'evento': evento}
            return {'success': False, 'message': 'Evento no encontrado'}
        except Exception as e:
            return {'success': False, 'message': f'Error al obtener evento: {str(e)}'}

    @staticmethod
    def actualizar_evento(evento_id, id_estudiante, datos):
        """Actualizar un evento existente"""
        try:
            titulo = datos.get('titulo')
            descripcion = datos.get('descripcion', '')
            fecha = datos.get('fecha')
            hora_inicio = datos.get('hora_inicio')
            hora_fin = datos.get('hora_fin')
            color = datos.get('color', '#4facfe')

            # Validaciones
            if not titulo or not fecha or not hora_inicio or not hora_fin:
                return {'success': False, 'message': 'Faltan datos requeridos'}

            if hora_inicio >= hora_fin:
                return {'success': False, 'message': 'La hora de inicio debe ser anterior a la hora de fin'}

            resultado = Evento.actualizar_evento(
                evento_id, id_estudiante, titulo, descripcion, fecha, hora_inicio, hora_fin, color
            )
            return resultado
        except Exception as e:
            return {'success': False, 'message': f'Error en el controlador: {str(e)}'}

    @staticmethod
    def eliminar_evento(evento_id, id_estudiante):
        """Eliminar un evento"""
        try:
            resultado = Evento.eliminar_evento(evento_id, id_estudiante)
            return resultado
        except Exception as e:
            return {'success': False, 'message': f'Error al eliminar evento: {str(e)}'}

    @staticmethod
    def obtener_eventos_por_fecha(id_estudiante, fecha):
        """Obtener eventos de una fecha específica"""
        try:
            eventos = Evento.obtener_eventos_por_fecha(id_estudiante, fecha)
            return {'success': True, 'eventos': eventos}
        except Exception as e:
            return {'success': False, 'message': f'Error al obtener eventos: {str(e)}'}

    @staticmethod
    def obtener_eventos_mes(id_estudiante, anio, mes):
        """Obtener eventos del mes"""
        try:
            eventos = Evento.obtener_eventos_mes(id_estudiante, anio, mes)
            return {'success': True, 'eventos': eventos}
        except Exception as e:
            return {'success': False, 'message': f'Error al obtener eventos: {str(e)}'}
