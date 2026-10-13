from Estudiante import Estudiante

class AsistenteDocente(Estudiante):

    def __init__(self, cedula: str, nombres: str, apellidos: str, correoElectronico: str, tipoEstudiante: str, horasAsignadaAsistencia: int, docenteApoya: str,):
        super().__init__(
            cedula, nombres, apellidos, correoElectronico, tipoEstudiante
        )
        self.__horasAsignadaAsistencia: int = horasAsignadaAsistencia
        self.__docenteApoya: str = docenteApoya

    def programarAsistencia(self) -> None:
        print(
            f"Asistencia programada con el docente {self.__docenteApoya} por {self.__horasAsignadaAsistencia} horas."
        )

    def obtenerCargaAcademica(self) -> str:
        return (
            f"Estudiante Asistente apoyando a: {self.__docenteApoya} - "
            f"Horas de Asistencia: {self.__horasAsignadaAsistencia} hrs"
        )