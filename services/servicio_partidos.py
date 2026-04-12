import pandas as pd
import csv
from models.PartidoBase import PartidoBase

def obtener_todos_los_partidos(equipo=None, fecha=None, fase=None, _limit=None, _offset=0):
    df = pd.read_csv('data/partidos.csv')

    partidos = []

    for _, fila in df.iterrows():
        if equipo and equipo.lower() not in str(fila['equipo_local']).lower() and equipo.lower() not in str(fila['equipo_visitante']).lower():
            continue
        
        if fecha and str(fecha).lower() != str(fila['fecha']).lower():
            continue
            
        if fase and str(fase).lower() != str(fila['fase']).lower():
            continue

        partido = PartidoBase(
            equipo_local=str(fila['equipo_local']),
            equipo_visitante=str(fila['equipo_visitante']),
            fecha=str(fila['fecha']),
            fase=str(fila['fase']),
        )
        partidos.append(partido)

    # Obtenemos la longitud de los resultados encontrados ANTES de "cortarlos" por pagina
    total_resultados = len(partidos)

    # Aplicamos la logica de offset saltando la cantidad ingresada
    if _offset > 0:
        partidos = partidos[_offset:]

    if _limit is not None and _limit > 0:
        partidos = partidos[:_limit]

    return partidos, total_resultados

def crear_partido(partido: PartidoBase):
    validar_nuevo_partido(partido)
    try:
        df = pd.read_csv('data/partidos.csv')
        nuevo_id = int(df['id'].max()) + 1 if not df.empty else 1
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df = pd.DataFrame(columns=['id', 'equipo_local', 'equipo_visitante', 'fecha', 'fase'])
        nuevo_id = 1
        
    partido.id = nuevo_id

    nueva_fila = pd.DataFrame([{
        'id': partido.id, 
        'equipo_local': partido.equipo_local, 
        'equipo_visitante': partido.equipo_visitante, 
        'fecha': partido.fecha, 
        'fase': partido.fase
    }])
    df = pd.concat([df, nueva_fila], ignore_index=True)
    
    df.to_csv('data/partidos.csv', index=False, encoding='utf-8')
    
    return partido


def validar_nuevo_partido(nuevo_partido):
    partidos, _ = obtener_todos_los_partidos()

    for partido in partidos:
        if partido.equipo_local == nuevo_partido.equipo_local and partido.equipo_visitante == nuevo_partido.equipo_visitante and partido.fase == nuevo_partido.fase:
            raise ValueError('El partido ya existe')

        if partido.fecha == nuevo_partido.fecha:
            if nuevo_partido.equipo_local in [partido.equipo_local, partido.equipo_visitante]:
                 raise ValueError(f"{nuevo_partido.equipo_local} ya juega un partido en la fecha {partido.fecha}.")

            if nuevo_partido.equipo_visitante in [partido.equipo_local, partido.equipo_visitante]:
                 raise ValueError(f"{nuevo_partido.equipo_visitante} ya juega un partido en la fecha {partido.fecha}.")
 

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