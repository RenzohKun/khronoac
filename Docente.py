from Persona import Persona

class Docente(Persona):

    def __init__(self, cedula, nombres, apellidos, correoElectronico, titulo_academico, disponibilidad=None,):
        super().__init__(cedula, nombres, apellidos, correoElectronico)
        self.__titulo_academico = titulo_academico
        self.__disponibilidad = (
            disponibilidad if disponibilidad is not None else []
        )

    def registrar_disponibilidad(self, franja):
        self.__disponibilidad.append(franja)

    def verificar_disponibilidad(self, franja_horaria):
        return True

    def obtener_datos(self):
        return f"Docente: {self.nombres} {self.apellidos} - Título: {self.__titulo_academico}"

    def obtener_carga_academica(self):
        return f"Horarios disponibles: {len(self.__disponibilidad)}"