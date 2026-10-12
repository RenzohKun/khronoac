from Estudiante import Estudiante

class AsistenteDocente(Estudiante):

    def __init__(self, cedula: str, nombres: str, apellidos: str, correoElectronico: str, tipoEstudiante: str, horasAsignadaAsistencia: int, docenteApoya: str,):
        super().__init__(
            cedula, nombres, apellidos, correoElectronico, tipoEstudiante
        )
        self.horasAsignadaAsistencia: int = horasAsignadaAsistencia
        self.docenteApoya: str = docenteApoya

    def programarAsistencia(self) -> None:
        print(
            f"Asistencia programada con el docente {self.docenteApoya} por {self.horasAsignadaAsistencia} horas."
        )

    def obtenerCargaAcademica(self) -> str:
        return (
            f"Estudiante Asistente apoyando a: {self.docenteApoya} - "
            f"Horas de Asistencia: {self.horasAsignadaAsistencia} hrs"
        )