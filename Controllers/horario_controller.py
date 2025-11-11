from Models.horario import Horario

class HorarioController:
    @staticmethod
    def listar_horarios():
        return Horario.obtener_todos()

    @staticmethod
    def obtener_horario(id):
        return Horario.obtener_por_id(id)