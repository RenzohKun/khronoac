import json
from pathlib import Path
from typing import Any, Mapping


class KhronoacPersistenciaDatos:

    def __init__(self, directorio_datos: Path) -> None:
        self.__directorio_datos = Path(directorio_datos)

    def cargar_datos(self) -> dict[str, Any]:
        # Carga las secciones existentes y aplica los valores predeterminados.
        self.__directorio_datos.mkdir(parents=True, exist_ok=True)
        return {
            "docentes": self.__leer_seccion("docentes", []),
            "asignaturas": self.__leer_seccion("asignaturas", []),
            "espacios": self.__leer_seccion("espacios", []),
            "ultimoHorario": self.__leer_seccion("horario", None),
        }

    def guardar_datos(self, datos: Mapping[str, Any]) -> None:
        # Guarda las secciones principales en sus archivos JSON.
        self.__guardar_seccion("docentes", datos["docentes"])
        self.__guardar_seccion("asignaturas", datos["asignaturas"])
        self.__guardar_seccion("espacios", datos["espacios"])
        self.__guardar_seccion("horario", datos["ultimoHorario"])

    def guardar_horario_exportado(
        self,
        horario: Mapping[str, Any],
        nombre_archivo: str = "horario_exportado.json",
    ) -> Path:
        # Guarda una copia exportada del horario y devuelve la ruta resultante.
        self.__directorio_datos.mkdir(parents=True, exist_ok=True)
        archivo = self.__directorio_datos / nombre_archivo
        with archivo.open("w", encoding="utf-8") as salida:
            json.dump(horario, salida, ensure_ascii=False, indent=2)
        return archivo

    def __leer_seccion(self, nombre: str, por_defecto: Any) -> Any:
        archivo = self.__directorio_datos / f"{nombre}.json"
        if not archivo.exists():
            return por_defecto
        try:
            with archivo.open("r", encoding="utf-8") as entrada:
                return json.load(entrada)
        except (OSError, json.JSONDecodeError):
            return por_defecto

    def __guardar_seccion(self, nombre: str, contenido: Any) -> None:
        self.__directorio_datos.mkdir(parents=True, exist_ok=True)
        archivo = self.__directorio_datos / f"{nombre}.json"
        temporal = self.__directorio_datos / f"{nombre}.tmp"
        with temporal.open("w", encoding="utf-8") as salida:
            json.dump(contenido, salida, ensure_ascii=False, indent=2)
        temporal.replace(archivo)
