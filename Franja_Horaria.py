from datetime import time

class FranjaHoraria:
    def __init__(self, dia_semana: str, hora_inicio: time, hora_fin: time):
        self._dia_semana: str = dia_semana
        self._hora_inicio: time = hora_inicio
        self._hora_fin: time = hora_fin

    @property
    def dia_semana(self) -> str:
        return self._dia_semana

    @property
    def hora_inicio(self) -> time:
        return self._hora_inicio

    @property
    def hora_fin(self) -> time:
        return self._hora_fin

    def verificar_solapamiento(self, otra_franja: "FranjaHoraria") -> bool:
        
        if self._dia_semana.lower() != otra_franja.dia_semana.lower():
            return False
        
        return self._hora_inicio < otra_franja.hora_fin and otra_franja.hora_inicio < self._hora_fin