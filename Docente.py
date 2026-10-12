from persona import Persona 

class Docente(Persona): 
    def __init__(self, cedula, nombre, apellidos, correo, titulo_academico, disponibilidad):
        super().__init__(cedula, nombre, apellidos, correo)
        self.titulo_academico = titulo_academico
        self.disponibilidad = disponibilidad

    def registrar_disponibilidad(self, disponibilidad): 
        return 

    def verificar_disponibilidad(franja_horaria):
        return

    def obtener_carga_academica(self):
        return