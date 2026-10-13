from typing import List

from Docente import Docente
from FranjaHoraria import FranjaHoraria


class AsistenteDocente(Docente):
    def __init__(
        self,
        cedula: str,
        nombres: str,
        apellidos: str,
        correoElectronico: str,
        tituloAcademico: str = "",
        horasAsignadaAsistencia: int = 0,
        docenteApoya: str = "",
        disponibilidad: List[FranjaHoraria] | None = None,
    ) -> None:
        super().__init__(
            cedula,
            nombres,
            apellidos,
            correoElectronico,
            tituloAcademico,
            disponibilidad,
        )
        if horasAsignadaAsistencia < 0:
            raise ValueError("Las horas de asistencia no pueden ser negativas.")
        self.__horasAsignadaAsistencia = horasAsignadaAsistencia
        self.__docenteApoya = docenteApoya

    @property
    def horasAsignadaAsistencia(self) -> int:
        return self.__horasAsignadaAsistencia

    @horasAsignadaAsistencia.setter
    def horasAsignadaAsistencia(self, valor: int) -> None:
        if valor < 0:
            raise ValueError("Las horas de asistencia no pueden ser negativas.")
        self.__horasAsignadaAsistencia = valor

    @property
    def docenteApoya(self) -> str:
        return self.__docenteApoya

    @docenteApoya.setter
    def docenteApoya(self, valor: str) -> None:
        self.__docenteApoya = valor

    def programarAsistencia(self) -> None:
        print(
            f"Asistencia programada con el docente {self.__docenteApoya} "
            f"por {self.__horasAsignadaAsistencia} horas."
        )

    def obtenerCargaAcademica(self) -> str:
        return (
            f"Asistencia a {self.__docenteApoya}: "
            f"{self.__horasAsignadaAsistencia} horas"
        )
