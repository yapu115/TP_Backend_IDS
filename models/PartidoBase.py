class PartidoBase:
    """
    Datos mínimos necesarios para registrar un partido dentro del fixture
    """
    def __init__(self, equipo_local: str, equipo_visitante: str, fecha: str, fase: str):
        self.equipo_local = equipo_local
        self.equipo_visitante = equipo_visitante
        self.fecha = fecha
        self.fase = fase

    def to_dict(self):
        """
        Devuelve los datos del partido en formato de diccionario
        """
        return {
            "equipo_local": self.equipo_local,
            "equipo_visitante": self.equipo_visitante,
            "fecha": self.fecha,
            "fase": self.fase
        }