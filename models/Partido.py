class Partido:
    def __init__(self, id, equipo_local, equipo_visitante, fecha, fase, estadio, ciudad, goles_local=None, goles_visitante=None):
        self.id = id
        self.equipo_local = equipo_local
        self.equipo_visitante = equipo_visitante
        self.fecha = fecha
        self.fase = fase
        self.estadio = estadio
        self.ciudad = ciudad
        self.goles_local = goles_local
        self.goles_visitante = goles_visitante

    def to_dict(self):
        """
        Devuelve los datos del partido en formato de diccionario
        """
        return {
            "id": self.id,
            "equipo_local": self.equipo_local,
            "equipo_visitante": self.equipo_visitante,
            "fecha": self.fecha,
            "fase": self.fase
        }