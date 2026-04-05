import pandas as pd
from models.Partido import Partido

def obtener_todos_los_partidos():
    df = pd.read_csv('data/partidos.csv')

    partidos = []

    for _, fila in df.iterrows():
        partido = Partido(
            id=int(fila['id']),
            equipo_local=str(fila['equipo_local']),
            equipo_visitante=str(fila['equipo_visitante']),
            fecha=str(fila['fecha']),
            fase=str(fila['fase']),
            estadio=str(fila['estadio']),
            ciudad=str(fila['ciudad']),
        )
        partidos.append(partido)

    return partidos