from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class ObservadorHorario(ABC):
    """Interfaz del patrón Observer para suscriptores de eventos de planificación."""

    @abstractmethod
    def actualizar(self, evento: str, detalle: dict[str, Any]) -> None:
        """Recibe notificaciones cuando ocurre un cambio en la planificación."""
        ...


class SujetoPlanificacion:
    """Gestiona la suscripción y notificación de observadores de planificación."""

    def __init__(self) -> None:
        self.__observadores: list[ObservadorHorario] = []

    def suscribir(self, observador: ObservadorHorario) -> None:
        if not isinstance(observador, ObservadorHorario):
            raise TypeError("El observador debe implementar ObservadorHorario.")
        if observador not in self.__observadores:
            self.__observadores.append(observador)

    def desuscribir(self, observador: ObservadorHorario) -> None:
        if observador in self.__observadores:
            self.__observadores.remove(observador)

    def notificar(self, evento: str, detalle: dict[str, Any] | None = None) -> None:
        carga = dict(detalle or {})
        for observador in list(self.__observadores):
            observador.actualizar(evento, carga)


class HistorialEventosHorario(ObservadorHorario):
    """Observador concreto que registra los eventos ocurridos durante la planificación."""

    def __init__(self) -> None:
        self.__registros: list[dict[str, Any]] = []

    @property
    def registros(self) -> list[dict[str, Any]]:
        return list(self.__registros)

    def actualizar(self, evento: str, detalle: dict[str, Any]) -> None:
        self.__registros.append({
            "marcaTiempo": datetime.now().isoformat(timespec="seconds"),
            "evento": evento,
            "detalle": dict(detalle),
        })

    def limpiarHistorial(self) -> None:
        self.__registros.clear()