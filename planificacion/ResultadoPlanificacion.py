# Este objeto transporta el resultado calculado antes de construir un Horario.

from typing import Any


class ResultadoPlanificacion:
    # Transporta los datos calculados y puede reconstruirse desde el JSON guardado.

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

    @classmethod
    def desdeDiccionario(cls, datos: dict[str, Any]) -> ResultadoPlanificacion:
        # Reconstruye el DTO sin incluir metadatos propios del horario final.
        estadisticas = {
            clave: datos[clave]
            for clave in ("minimoEstudiantes", "bloqueMinutos")
            if clave in datos
        }
        return cls(
            paralelos=[dict(paralelo) for paralelo in datos.get("paralelos", [])],
            sesiones=[dict(sesion) for sesion in datos.get("sesiones", [])],
            estadisticas=estadisticas,
            franjasSinConflicto=datos.get("franjasSinConflicto", False),
        )

    def aDiccionario(self) -> dict[str, Any]:
        return {
            "paralelos": [dict(paralelo) for paralelo in self.paralelos],
            "sesiones": [dict(sesion) for sesion in self.sesiones],
            **self.estadisticas,
            "franjasSinConflicto": self.franjasSinConflicto,
        }
