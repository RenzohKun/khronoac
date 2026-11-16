# Este objeto transporta el resultado calculado antes de construir un Horario.

from typing import Any


class ResultadoPlanificacion:
    def __init__(
        self,
        paralelos: list[dict[str, Any]],
        sesiones: list[dict[str, Any]],
        estadisticas: dict[str, Any],
        franjasSinConflicto: bool,
    ) -> None:
        self.paralelos = paralelos
        self.sesiones = sesiones
        self.estadisticas = estadisticas
        self.franjasSinConflicto = franjasSinConflicto

    def aDiccionario(self) -> dict[str, Any]:
        return {
            "paralelos": [dict(paralelo) for paralelo in self.paralelos],
            "sesiones": [dict(sesion) for sesion in self.sesiones],
            **self.estadisticas,
            "franjasSinConflicto": self.franjasSinConflicto,
        }
