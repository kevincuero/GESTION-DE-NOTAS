from Models.usuario import Usuario

class Profesor(Usuario):
    def __init__(self, id=None, nombre=None, correo=None, contraseña=None):
        super().__init__(id, nombre, correo, contraseña, 'profesor')