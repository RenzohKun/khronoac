from typing import List
from Franja_Horaria import FranjaHoraria

class Horario:
    def __init__(self, id_horario: str, periodo_academico: str, tipo_horario: str):
        self._id_horario: str = id_horario
        self._periodo_academico: str = periodo_academico
        self._tipo_horario: str = tipo_horario
        
        # Relación "se divide en" (1 a 1..*)
        self._franjas_horarias: List[FranjaHoraria] = []

    @property
    def id_horario(self) -> str:
        return self._id_horario

    @property
    def periodo_academico(self) -> str:
        return self._periodo_academico

    @property
    def tipo_horario(self) -> str:
        return self._tipo_horario

    @property
    def franjas_horarias(self) -> List[FranjaHoraria]:
        return self._franjas_horarias

    def agregar_franja(self, franja: FranjaHoraria) -> None:
        self._franjas_horarias.append(franja)

    def validar_conflictos(self) -> bool:

        n = len(self._franjas_horarias)
        for i in range(n):
            for j in range(i + 1, n):
                if self._franjas_horarias[i].verificar_solapamiento(self._franjas_horarias[j]):
                    return True  # Hay conflicto
        return False  # Sin conflictos

    def generar_malla_horaria(self) -> str:

        res = f"--- Malla Horaria: {self._id_horario} ({self._periodo_academico}) ---\n"
        for franja in self._franjas_horarias:
            res += f"- {franja.dia_semana}: {franja.hora_inicio.strftime('%H:%M')} - {franja.hora_fin.strftime('%H:%M')}\n"
        return res