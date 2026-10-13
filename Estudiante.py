from Persona import Persona

class Estudiante(Persona):

    def __init__(self, cedula, nombre, apellidos, correoElectronico, tipoEstudiante, materiasInscritas=None,):
        super().__init__(cedula, nombre, apellidos, correoElectronico)
        self.__tipoEstudiante = tipoEstudiante
        self.__materiasInscritas = (
            materiasInscritas if materiasInscritas is not None else []
        )

    def obtener_tipo_estudiante(self):
        return self.__tipoEstudiante

    def obtener_materias_matriculadas(self):
        return self.__materiasInscritas

    def obtener_datos(self):
        return f"{self.nombres} {self.apellidos} ({self.cedula}) - Tipo: {self.__tipoEstudiante}"

    def obtener_carga_academica(self):
        return f"Materias matriculadas: {len(self.__materiasInscritas)}"