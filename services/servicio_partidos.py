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

#Defino la función de PUT para actualizar los resultados de los partidos. En caso de no haber actualización, devuelve none
def actualizar_resultado(id_partido, goles_local, goles_visitante):
    df = pd.read_csv('data/partidos.csv')

    partido_encontrado = False
    partido_actualizado = None

    for i in range(len(df)):
        if int(df.loc[i, 'id']) == id_partido:
            df.loc[i, 'goles_local'] = goles_local
            df.loc[i, 'goles_visitante'] = goles_visitante
            partido_encontrado = True

            partido_actualizado = {
                "id": int(df.loc[i, 'id']),
                "equipo_local": str(df.loc[i, 'equipo_local']),
                "equipo_visitante": str(df.loc[i, 'equipo_visitante']),
                "fecha": str(df.loc[i, 'fecha']),
                "fase": str(df.loc[i, 'fase']),
                "estadio": str(df.loc[i, 'estadio']),
                "ciudad": str(df.loc[i, 'ciudad']),
                "goles_local": int(df.loc[i, 'goles_local']),
                "goles_visitante": int(df.loc[i, 'goles_visitante'])
            }

            break

    if partido_encontrado == False:
        return None

    df.to_csv('data/partidos.csv', index=False) 

    return partido_actualizado


#defino la función de PUT para partidos
def actualizar_partidos(id, equipo_local, equipo_visitante, fecha, fase, estadio, ciudad):
    df = pd.read_csv('data/partidos.csv')

    partido_encontrado = False
    partido_actualizado = None

    for i in range(len(df)):
        if int(df.loc[i, 'id']) == id:
            df.loc[i, 'equipo_local'] = equipo_local
            df.loc[i, 'equipo_visitante'] = equipo_visitante
            df.loc[i, 'fecha'] = fecha
            df.loc[i, 'fase'] = fase
            df.loc[i, 'estadio'] = estadio
            df.loc[i, 'ciudad'] = ciudad

            partido_encontrado = True

            goles_local = df.loc[i, 'goles_local']
            goles_visitante = df.loc[i, 'goles_visitante']

            if str(goles_local) == 'nan':
                goles_local = None
            else:
                goles_local = int(goles_local)

            if str(goles_visitante) == 'nan':
                goles_visitante = None
            else:
                goles_visitante = int(goles_visitante)
            
            partido_actualizado = {
                "id": int(df.loc[i, 'id']),
                "equipo_local": str(df.loc[i, 'equipo_local']),
                "equipo_visitante": str(df.loc[i, 'equipo_visitante']),
                "fecha": str(df.loc[i, 'fecha']),
                "fase": str(df.loc[i,'fase']),
                "estadio": str(df.loc[i, 'estadio']),
                "ciudad": str(df.loc[i, 'ciudad']),
                "goles_local": goles_local,
                "goles_visitante": goles_visitante
            }

            break

    if partido_encontrado == False:
       return None

    df.to_csv('data/partidos.csv', index=False)

    return partido_actualizado