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
        self.__validarCapacidad(capacidadMaxima)

    @staticmethod
    def __validarCapacidad(valor: int) -> None:
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
        self.__validarCapacidad(valor)
        self.__capacidadMaxima = valor

    @property
    def franjasOcupadas(self) -> List[FranjaHoraria]:
        return self.__franjasOcupadas.copy()

    def verificarAforo(self, cantidad: int) -> int:
        """Devuelve los puestos restantes; un valor negativo indica exceso de aforo."""
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
        """Contrato base (LSP): Un aula física es apta si la asignatura NO exige laboratorio."""
        return not asignatura.requiereLaboratorio()

def esAptoParaAsignatura(self, asignatura: Asignatura) -> bool:
    return not asignatura.requiereLaboratorio()

def esAptoParaAsignatura(self, asignatura: Asignatura) -> bool:
    return asignatura.requiereLaboratorio()

    if espacio.esAptoParaAsignatura(asignatura):
        espacios_validos.append((clave, espacio))