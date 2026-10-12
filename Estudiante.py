from Persona import Persona

class Estudiante(Persona):

    def __init__(self, cedula, nombre, apellidos, correo, tipo_estudiante, materias_matriculadas=None,):
        super().__init__(cedula, nombre, apellidos, correo)
        self.tipo_estudiante = tipo_estudiante
        self.materias_matriculadas = (
            materias_matriculadas if materias_matriculadas is not None else []
        )

    def obtener_tipo_estudiante(self):
        return self.tipo_estudiante

    def obtener_materias_matriculadas(self):
        return self.materias_matriculadas

    def obtener_datos(self):
        return f"{self.nombres} {self.apellidos} ({self.cedula}) - Tipo: {self.tipo_estudiante}"

    def obtener_carga_academica(self):
        return f"Materias matriculadas: {len(self.materias_matriculadas)}"