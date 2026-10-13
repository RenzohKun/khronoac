from datetime import time


class FranjaHoraria:
    def __init__(self, diaSemana: str, horaInicio: time, horaFin: time) -> None:
        self.__diaSemana = diaSemana
        self.__horaInicio = horaInicio
        self.__horaFin = horaFin
        self.__validarHoras()

    @property
    def diaSemana(self) -> str:
        return self.__diaSemana

    @diaSemana.setter
    def diaSemana(self, valor: str) -> None:
        self.__diaSemana = valor

    @property
    def horaInicio(self) -> time:
        return self.__horaInicio

    @horaInicio.setter
    def horaInicio(self, valor: time) -> None:
        anterior = self.__horaInicio
        self.__horaInicio = valor
        try:
            self.__validarHoras()
        except (TypeError, ValueError):
            self.__horaInicio = anterior
            raise

    @property
    def horaFin(self) -> time:
        return self.__horaFin

    @horaFin.setter
    def horaFin(self, valor: time) -> None:
        anterior = self.__horaFin
        self.__horaFin = valor
        try:
            self.__validarHoras()
        except (TypeError, ValueError):
            self.__horaFin = anterior
            raise

    def __validarHoras(self) -> None:
        if not isinstance(self.__horaInicio, time) or not isinstance(self.__horaFin, time):
            raise TypeError("Las horas deben ser objetos datetime.time.")
        if self.__horaInicio >= self.__horaFin:
            raise ValueError("La hora de inicio debe ser anterior a la hora de fin.")

    def verificarSolapamiento(self, otraFranja: "FranjaHoraria") -> bool:
        if self.__diaSemana.casefold() != otraFranja.diaSemana.casefold():
            return False
        return (
            self.__horaInicio < otraFranja.horaFin
            and otraFranja.horaInicio < self.__horaFin
        )
