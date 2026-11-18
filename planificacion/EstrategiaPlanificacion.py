from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Mapping, Sequence


class EstrategiaPlanificacion(ABC):
    """Interfaz base del patrón Strategy para priorizar franjas candidatas."""

    @abstractmethod
    def ordenarCandidatos(
        self,
        candidatos: Sequence[tuple[str, int, str]],
        sesionesPorDia: Mapping[str, int],
        diasOrdenados: tuple[str, ...],
    ) -> list[tuple[str, int, str]]:
        """Ordena las combinaciones (dia, hora, codigoEspacio) según el criterio."""
        ...


class EstrategiaBalanceada(EstrategiaPlanificacion):
    """Distribuye equitativamente la carga académica a lo largo de la semana."""

    def ordenarCandidatos(
        self,
        candidatos: Sequence[tuple[str, int, str]],
        sesionesPorDia: Mapping[str, int],
        diasOrdenados: tuple[str, ...],
    ) -> list[tuple[str, int, str]]:
        return sorted(
            candidatos,
            key=lambda candidato: (
                sesionesPorDia.get(candidato[0], 0),
                diasOrdenados.index(candidato[0]),
                candidato[1],
                candidato[2],
            ),
        )


class EstrategiaMatutina(EstrategiaPlanificacion):
    """Prioriza los bloques horarios más tempranos antes que el balanceo por día."""

    def ordenarCandidatos(
        self,
        candidatos: Sequence[tuple[str, int, str]],
        sesionesPorDia: Mapping[str, int],
        diasOrdenados: tuple[str, ...],
    ) -> list[tuple[str, int, str]]:
        return sorted(
            candidatos,
            key=lambda candidato: (
                candidato[1],
                sesionesPorDia.get(candidato[0], 0),
                diasOrdenados.index(candidato[0]),
                candidato[2],
            ),
        )


class EstrategiaCompacta(EstrategiaPlanificacion):
    """Agrupa las sesiones en los primeros días disponibles de la semana."""

    def ordenarCandidatos(
        self,
        candidatos: Sequence[tuple[str, int, str]],
        sesionesPorDia: Mapping[str, int],
        diasOrdenados: tuple[str, ...],
    ) -> list[tuple[str, int, str]]:
        return sorted(
            candidatos,
            key=lambda candidato: (
                diasOrdenados.index(candidato[0]),
                candidato[1],
                candidato[2],
            ),
        )