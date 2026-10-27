from typing import List

from modelos.FranjaHoraria import FranjaHoraria
from modelos.Persona import Persona


class Docente(Persona):
    def __init__(
        self,
        cedula: str,
        nombres: str,
        apellidos: str,
        correoElectronico: str,
        tituloAcademico: str = "",
        disponibilidad: List[FranjaHoraria] | None = None,
    ) -> None:
        super().__init__(cedula, nombres, apellidos, correoElectronico)
        self.__tituloAcademico = tituloAcademico
        self.__disponibilidad = list(disponibilidad or [])

    @property
    def tituloAcademico(self) -> str:
        return self.__tituloAcademico

    @tituloAcademico.setter
    def tituloAcademico(self, valor: str) -> None:
        self.__tituloAcademico = valor

    @property
    def disponibilidad(self) -> List[FranjaHoraria]:
        return self.__disponibilidad.copy()

    @disponibilidad.setter
    def disponibilidad(self, valor: List[FranjaHoraria]) -> None:
        self.__disponibilidad = list(valor)

    def registrarDisponibilidad(self, franja: FranjaHoraria) -> None:
        if not isinstance(franja, FranjaHoraria):
            raise TypeError("La disponibilidad debe ser una FranjaHoraria.")
        if franja not in self.__disponibilidad:
            self.__disponibilidad.append(franja)

    def verificarDisponibilidad(self, franja: FranjaHoraria) -> bool:
        """Indica si la franja solicitada está contenida en una disponibilidad."""
        for disponible in self.__disponibilidad:
            if (
                disponible.diaSemana.casefold() == franja.diaSemana.casefold()
                and disponible.horaInicio <= franja.horaInicio
                and franja.horaFin <= disponible.horaFin
            ):
                return True
        return False

    def obtenerDatos(self) -> str:
        return (
            f"Docente: {self.nombres} {self.apellidos} "
            f"- Título: {self.__tituloAcademico}"
        )

    def obtenerCargaAcademica(self) -> str:
        return f"Franjas disponibles: {len(self.__disponibilidad)}"
