from Models.usuario import Usuario

class Padre(Usuario):
    def __init__(self, id=None, nombre=None, correo=None, contraseña=None):
        super().__init__(id, nombre, correo, contraseña, 'padre')