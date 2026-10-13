from typing import List

from Persona import Persona
from Asignatura import Asignatura


class Estudiante(Persona):
    def __init__(
        self,
        cedula: str,
        nombres: str,
        apellidos: str,
        correoElectronico: str,
        tipoEstudiante: str = "",
        materiasInscritas: List[Asignatura] | None = None,
    ) -> None:
        super().__init__(cedula, nombres, apellidos, correoElectronico)
        self.__tipoEstudiante = tipoEstudiante
        self.__materiasInscritas = list(materiasInscritas or [])

    @property
    def tipoEstudiante(self) -> str:
        return self.__tipoEstudiante

    @tipoEstudiante.setter
    def tipoEstudiante(self, valor: str) -> None:
        self.__tipoEstudiante = valor

    @property
    def materiasInscritas(self) -> List[Asignatura]:
        # Se entrega una copia para que la lista interna no pueda alterarse desde fuera.
        return self.__materiasInscritas.copy()

    @materiasInscritas.setter
    def materiasInscritas(self, valor: List[Asignatura]) -> None:
        self.__materiasInscritas = list(valor)

    def obtenerTipoEstudiante(self) -> str:
        return self.__tipoEstudiante

    def obtenerMateriasInscritas(self) -> List[Asignatura]:
        return self.materiasInscritas

    def obtenerDatos(self) -> str:
        return (
            f"{self.nombres} {self.apellidos} ({self.cedula}) "
            f"- Tipo: {self.__tipoEstudiante}"
        )

    def obtenerCargaAcademica(self) -> str:
        return f"Materias inscritas: {len(self.__materiasInscritas)}"
