from abc import ABC, abstractmethod


class Persona(ABC):
    """Clase abstracta con los datos comunes de las personas del sistema."""

    def __init__(self, cedula: str, nombres: str, apellidos: str, correoElectronico: str) -> None:
        self.__cedula = cedula
        self.__nombres = nombres
        self.__apellidos = apellidos
        self.__correoElectronico = correoElectronico

    @property
    def cedula(self) -> str:
        return self.__cedula

    @cedula.setter
    def cedula(self, valor: str) -> None:
        self.__cedula = valor

    @property
    def nombres(self) -> str:
        return self.__nombres

    @nombres.setter
    def nombres(self, valor: str) -> None:
        self.__nombres = valor

    @property
    def apellidos(self) -> str:
        return self.__apellidos

    @apellidos.setter
    def apellidos(self, valor: str) -> None:
        self.__apellidos = valor

    @property
    def correoElectronico(self) -> str:
        return self.__correoElectronico

    @correoElectronico.setter
    def correoElectronico(self, valor: str) -> None:
        self.__correoElectronico = valor

    @abstractmethod
    def obtenerDatos(self) -> str:
        pass

    @abstractmethod
    def obtenerCargaAcademica(self) -> str:
        pass
