from abc import ABC, abstractmethod
from typing import Any, Mapping

from modelos.EspacioFisico import EspacioFisico
from modelos.Laboratorio import Laboratorio


class CreadorEspacio(ABC):
    def crear(self, datos: Mapping[str, Any]) -> EspacioFisico:
        return self.factoryMethod(datos)

    @abstractmethod
    def factoryMethod(self, datos: Mapping[str, Any]) -> EspacioFisico:
        """Construye el tipo concreto de espacio."""


class CreadorAula(CreadorEspacio):
    def factoryMethod(self, datos: Mapping[str, Any]) -> EspacioFisico:
        return EspacioFisico(datos["codigoAula"], int(datos["capacidadMaxima"]))


class CreadorLaboratorio(CreadorEspacio):
    def factoryMethod(self, datos: Mapping[str, Any]) -> EspacioFisico:
        return Laboratorio(
            datos["codigoAula"],
            int(datos["capacidadMaxima"]),
            datos.get("equiposEspeciales", ""),
            datos.get("tipoLaboratorio", ""),
        )


CREADORES_ESPACIO: dict[str, CreadorEspacio] = {
    "Aula": CreadorAula(),
    "Laboratorio": CreadorLaboratorio(),
}


def crearEspacio(datos: Mapping[str, Any]) -> EspacioFisico:
    tipo = datos.get("tipo", "Aula")
    try:
        creador = CREADORES_ESPACIO[tipo]
    except KeyError as error:
        raise ValueError(f"Tipo de espacio no compatible: {tipo}") from error
    return creador.crear(datos)
