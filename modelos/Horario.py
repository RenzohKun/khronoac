from typing import List

from modelos.FranjaHoraria import FranjaHoraria

class Horario:
    def __init__(self, idHorario: str, periodoAcademico: str, tipoHorario: str) -> None:
        self.__idHorario = idHorario
        self.__periodoAcademico = periodoAcademico
        self.__tipoHorario = tipoHorario
        self.__franjasHorarias: List[FranjaHoraria] = []

    @property
    def idHorario(self) -> str:
        return self.__idHorario

    @idHorario.setter
    def idHorario(self, valor: str) -> None:
        self.__idHorario = valor

    @property
    def periodoAcademico(self) -> str:
        return self.__periodoAcademico

    @periodoAcademico.setter
    def periodoAcademico(self, valor: str) -> None:
        self.__periodoAcademico = valor

    @property
    def tipoHorario(self) -> str:
        return self.__tipoHorario

    @tipoHorario.setter
    def tipoHorario(self, valor: str) -> None:
        self.__tipoHorario = valor

    @property
    def franjasHorarias(self) -> List[FranjaHoraria]:
        return self.__franjasHorarias.copy()

    def agregarFranja(self, franja: FranjaHoraria) -> None:
        if not isinstance(franja, FranjaHoraria):
            raise TypeError("Solo se pueden agregar objetos FranjaHoraria.")
        self.__franjasHorarias.append(franja)

    def validarConflictos(self) -> bool:
        """Devuelve True cuando hay al menos dos franjas que se solapan."""
        for indice, franja in enumerate(self.__franjasHorarias):
            if any(
                franja.verificarSolapamiento(otra)
                for otra in self.__franjasHorarias[indice + 1 :]
            ):
                return True
        return False

    def generarMallaHoraria(self) -> str:
        lineas = [
            f"--- Malla Horaria: {self.__idHorario} ({self.__periodoAcademico}) ---"
        ]
        for franja in self.__franjasHorarias:
            lineas.append(
                f"- {franja.diaSemana}: "
                f"{franja.horaInicio.strftime('%H:%M')} - "
                f"{franja.horaFin.strftime('%H:%M')}"
            )
        return "\n".join(lineas)
