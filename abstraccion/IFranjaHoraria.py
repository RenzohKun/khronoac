from abc import ABC, abstractmethod
from datetime import time


class IFranjaHoraria(ABC):
    """Abstracción de una franja horaria.

    Principio DIP: los módulos de alto nivel (Horario) y los de bajo nivel
    (FranjaHoraria concreta) dependen de esta interfaz, no entre sí.
    """

    @property
    @abstractmethod
    def diaSemana(self) -> str:
        """Día de la semana al que pertenece la franja."""
        ...

    @property
    @abstractmethod
    def horaInicio(self) -> time:
        """Hora de inicio de la franja."""
        ...

    @property
    @abstractmethod
    def horaFin(self) -> time:
        """Hora de fin de la franja."""
        ...

    @abstractmethod
    def verificarSolapamiento(self, otraFranja: "IFranjaHoraria") -> bool:
        """Retorna True si esta franja se solapa con otraFranja."""
        ...

