import pandas as pd
import csv
from models.PartidoBase import PartidoBase
from mysql_db import get_db_connection;

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

    total_resultados = len(partidos)

    if _offset > 0:
        partidos = partidos[_offset:]

    if _limit is not None and _limit > 0:
        partidos = partidos[:_limit]

    return partidos, total_resultados

def crear_partido(partido: PartidoBase):
    # validar_nuevo_partido(partido)

    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)

    try:
        consulta = """
            INSERT INTO partidos (equipo_local, equipo_visitante, fecha, fase) 
            VALUES (%s, %s, %s, %s)
        """

        valores = (partido.equipo_local, partido.equipo_visitante, partido.fecha, partido.fase)
        
        cursor.execute(consulta, valores)
        conexion.commit()

        partido.id = cursor.lastrowid

        return partido

    except Exception as e:
        conexion.rollback()
        raise Exception(f"Error al crear el partido: {str(e)}")
    finally:
        cursor.close()
        conexion.close()



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

#def id para obtener partidos
def obtener_partido_por_id(id_partido: int):
    df = pd.read_csv('data/partidos.csv')

    for i in range(len(df)):
        if int(df.loc[i, 'id']) == id_partido:
            goles_local = df.loc[i, 'goles_local']
            goles_visitante = df.loc[i, 'goles_visitante']

            # pandas usa NaN para "vacío"
            if str(goles_local) == 'nan' or str(goles_visitante) == 'nan':
                resultado = None
            else:
                resultado = {
                    "local": int(goles_local),
                    "visitante": int(goles_visitante)
                }

            return {
                "id": int(df.loc[i, 'id']),
                "equipo_local": str(df.loc[i, 'equipo_local']),
                "equipo_visitante": str(df.loc[i, 'equipo_visitante']),
                "fecha": str(df.loc[i, 'fecha']),
                "fase": str(df.loc[i, 'fase']),
                "resultado": resultado
            }

    return None