from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from FranjaHoraria import FranjaHoraria

class EspacioFisico:

    def __init__(self, codigoAula: str, capacidadMaxima: int):
        self._codigoAula: str = codigoAula
        self._capacidadMaxima: int = capacidadMaxima
        self._franjasOcupadas: List["FranjaHoraria"] = []

    @property
    def codigoAula(self) -> str:
        return self._codigoAula

    @property
    def capacidadMaxima(self) -> int:
        return self._capacidadMaxima

    def verificarAforo(self, cantidad: int) -> bool:
        return cantidad <= self._capacidadMaxima

    def estaDisponible(self, franja: "FranjaHoraria") -> bool:
        for f in self._franjasOcupadas:
            if hasattr(f, "verificarSolapamiento") and f.verificarSolapamiento(
                franja
            ):
                return False
        return True

    def reservarFranja(self, franja: "FranjaHoraria") -> bool:
        if self.estaDisponible(franja):
            self._franjasOcupadas.append(franja)
            return True
        return False