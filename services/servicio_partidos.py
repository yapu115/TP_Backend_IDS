import pandas as pd
import csv
from models.PartidoBase import PartidoBase

def obtener_todos_los_partidos():
    df = pd.read_csv('data/partidos.csv')

    partidos = []

    for _, fila in df.iterrows():
        partido = PartidoBase(
            equipo_local=str(fila['equipo_local']),
            equipo_visitante=str(fila['equipo_visitante']),
            fecha=str(fila['fecha']),
            fase=str(fila['fase']),
        )
        partidos.append(partido)

    return partidos

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
    partidos = obtener_todos_los_partidos()

    for partido in partidos:
        if partido.equipo_local == nuevo_partido.equipo_local and partido.equipo_visitante == nuevo_partido.equipo_visitante and partido.fase == nuevo_partido.fase:
            raise ValueError('El partido ya existe')

        if partido.fecha == nuevo_partido.fecha:
            if nuevo_partido.equipo_local in [partido.equipo_local, partido.equipo_visitante]:
                 raise ValueError(f"{nuevo_partido.equipo_local} ya juega un partido en la fecha {partido.fecha}.")

            if nuevo_partido.equipo_visitante in [partido.equipo_local, partido.equipo_visitante]:
                 raise ValueError(f"{nuevo_partido.equipo_visitante} ya juega un partido en la fecha {partido.fecha}.")
