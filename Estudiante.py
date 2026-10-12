from persona import Persona 

class Estudiante(Persona):
    def __init__(self, cedula,nombre, apellidos, correo, tipo_estudiante, materias_matriculadas): 
        super().__init__(cedula, nombre, apellidos, correo)
        self.tipo_estudiante = tipo_estudiante
        self.materias_matriculadas = materias_matriculadas 


    def obtener_tipo_estudiante(self):
        return self._obtener_tipo_estudiante()

    def obtener_materias_matriculadas(self):
        return self._obtener_materias_matriculadas()

    def obtener_carga_academica(self): 
        return 

