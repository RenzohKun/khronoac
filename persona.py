class Persona:

    def __init__(
        self,
        cedula: str,
        nombres: str,
        apellidos: str,
        correo_institucional: str,
    ):
        self._cedula: str = cedula
        self._nombres: str = nombres
        self._apellidos: str = apellidos
        self._correo_institucional: str = correo_institucional

    @property
    def cedula(self) -> str:
        return self._cedula

    @property
    def nombres(self) -> str:
        return self._nombres

    @property
    def apellidos(self) -> str:
        return self._apellidos

    @property
    def correo_institucional(self) -> str:
        return self._correo_institucional

    def obtener_datos(self) -> str:
        return (
            f"Cedula: {self._cedula} - Nombre: {self._nombres} {self._apellidos}"
            f" - Correo: {self._correo_institucional}"
        )

    def obtener_carga_academica(self) -> str:
        """Metodo base para ser sobreescrito por las subclases (Estudiante/Docente)."""
        return "Sin carga academica asignada en la clase base."

if __name__ == "__main__":
    persona_prueba = Persona(
        cedula="1316100963",
        nombres="Francis Joseph",
        apellidos="Bailon Paredes",
        correo_institucional="e1316100963@live.uleam.edu.ec",
    )

    print("")
    print(persona_prueba.obtener_datos())
    print("Carga academica:", persona_prueba.obtener_carga_academica())