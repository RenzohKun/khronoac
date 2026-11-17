from __future__ import annotations
from typing import List, TYPE_CHECKING

from modelos.FranjaHoraria import FranjaHoraria

if TYPE_CHECKING:
    from modelos.Asignatura import Asignatura


class EspacioFisico:
    def __init__(self, codigoAula: str, capacidadMaxima: int) -> None:
        self.__codigoAula = codigoAula
        self.__capacidadMaxima = capacidadMaxima
        self.__franjasOcupadas: List[FranjaHoraria] = []
        self.validarCapacidad(capacidadMaxima)

    @staticmethod
    def validarCapacidad(valor: int) -> None:
        if valor < 0:
            raise ValueError("La capacidad máxima no puede ser negativa.")

    @property
    def codigoAula(self) -> str:
        return self.__codigoAula

    @codigoAula.setter
    def codigoAula(self, valor: str) -> None:
        self.__codigoAula = valor

    @property
    def capacidadMaxima(self) -> int:
        return self.__capacidadMaxima

    @capacidadMaxima.setter
    def capacidadMaxima(self, valor: int) -> None:
        self.validarCapacidad(valor)
        self.__capacidadMaxima = valor

    @property
    def franjasOcupadas(self) -> List[FranjaHoraria]:
        return self.__franjasOcupadas.copy()

    def verificarAforo(self, cantidad: int) -> int:
        return self.__capacidadMaxima - cantidad

    def estaDisponible(self, franja: FranjaHoraria) -> bool:
        return all(
            not ocupada.verificarSolapamiento(franja)
            for ocupada in self.__franjasOcupadas
        )

    def reservarFranja(self, franja: FranjaHoraria) -> bool:
        if not self.estaDisponible(franja):
            return False
        self.__franjasOcupadas.append(franja)
        return True

    def liberarFranja(self, franja: FranjaHoraria) -> bool:
        if franja not in self.__franjasOcupadas:
            return False
        self.__franjasOcupadas.remove(franja)
        return True

    def esAptoParaAsignatura(self, asignatura: Asignatura) -> bool:
        return not asignatura.requiereLaboratorio()


# -------- Decorator --------
class EspacioDecorador(EspacioFisico):
    """Envuelve un espacio y delega su comportamiento base."""

    def __init__(self, componente: EspacioFisico) -> None:
        super().__init__(componente.codigoAula, componente.capacidadMaxima)
        self.__componente = componente

    @property
    def codigoAula(self) -> str:
        return self.__componente.codigoAula

    @codigoAula.setter
    def codigoAula(self, valor: str) -> None:
        self.__componente.codigoAula = valor

    @property
    def capacidadMaxima(self) -> int:
        return self.__componente.capacidadMaxima

    @capacidadMaxima.setter
    def capacidadMaxima(self, valor: int) -> None:
        self.__componente.capacidadMaxima = valor

    @property
    def franjasOcupadas(self) -> List[FranjaHoraria]:
        return self.__componente.franjasOcupadas

    def verificarAforo(self, cantidad: int) -> int:
        return self.__componente.verificarAforo(cantidad)

    def estaDisponible(self, franja: FranjaHoraria) -> bool:
        return self.__componente.estaDisponible(franja)

    def reservarFranja(self, franja: FranjaHoraria) -> bool:
        return self.__componente.reservarFranja(franja)

    def liberarFranja(self, franja: FranjaHoraria) -> bool:
        return self.__componente.liberarFranja(franja)

    def esAptoParaAsignatura(self, asignatura: Asignatura) -> bool:
        return self.__componente.esAptoParaAsignatura(asignatura)
# ----- Fin del patrón Decorator ------------