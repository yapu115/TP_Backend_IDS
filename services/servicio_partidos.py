import pandas as pd
import csv
from models.PartidoBase import PartidoBase
from mysql_db import get_db_connection;

def obtener_todos_los_partidos(equipo=None, fecha=None, fase=None, _limit=None, _offset=0):

    # 1. Establecer conexión
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)
    
    try:
        # 2. Armar la consulta base
        query = "SELECT * FROM partidos WHERE 1=1" # al hacer el 1=1 se puede concatenar con AND fácilmente en los filtros
        count_query = "SELECT COUNT(*) as total FROM partidos WHERE 1=1"
        valores = []

        # 3. Aplicar Filtros
        if equipo:
            query += " AND (equipo_local LIKE %s OR equipo_visitante LIKE %s)"
            count_query += " AND (equipo_local LIKE %s OR equipo_visitante LIKE %s)"
            valores.extend([f"%{equipo}%", f"%{equipo}%"]) # Se usa f"%{equipo}%" para buscar si el texto coincide en cualquier parte string
            
        if fecha:
            query += " AND fecha = %s"
            count_query += " AND fecha = %s"
            valores.append(fecha)
            
        if fase:
            query += " AND fase = %s"
            count_query += " AND fase = %s"
            valores.append(fase)

        # 4. Obtener el Total de resultados (antes de aplicar LIMIT para la paginación)
        cursor.execute(count_query, valores)
        total_resultados = cursor.fetchone()['total']

        # 5. Aplicar Paginación
        if _limit is not None and _limit > 0:
            query += " LIMIT %s OFFSET %s"
            valores.extend([_limit, _offset])
        elif _offset > 0:
            # Si solo hay offset sin limit, le ponemos un limit gigante como buena práctica (no se puede usar offset sin limit en mysql)
            query += " LIMIT 1000000 OFFSET %s"
            valores.append(_offset)

        # 6. Ejecutar consulta principal
        cursor.execute(query, valores)
        resultados = cursor.fetchall()
        
        # 7. Convertir los diccionarios de MySQL a tus objetos PartidoBase
        partidos = []
        for fila in resultados:
            partido = PartidoBase(
                equipo_local=fila['equipo_local'],
                equipo_visitante=fila['equipo_visitante'],
                fecha=str(fila['fecha']), 
                fase=fila['fase']
            )
            partidos.append(partido)

        return partidos, total_resultados

    finally:
        cursor.close()
        conexion.close()

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
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)
    
    try:
        # Validación 1: Evitar duplicados (basado en ambos equipos y la fase)
        query_duplicado = """
            SELECT COUNT(*) as cuenta FROM partidos 
            WHERE equipo_local = %s AND equipo_visitante = %s AND fase = %s
        """
        cursor.execute(query_duplicado, (nuevo_partido.equipo_local, nuevo_partido.equipo_visitante, nuevo_partido.fase))
        if cursor.fetchone()['cuenta'] > 0:
            raise ValueError('El partido ya existe')

        # Validación 2: Chequear que ni el local ni el visitante jueguen ya en esa misma fecha
        query_fecha = """
            SELECT equipo_local, equipo_visitante FROM partidos 
            WHERE fecha = %s AND (
                equipo_local = %s OR equipo_local = %s OR 
                equipo_visitante = %s OR equipo_visitante = %s
            )
        """
        cursor.execute(query_fecha, (
            nuevo_partido.fecha,
            nuevo_partido.equipo_local, nuevo_partido.equipo_visitante,
            nuevo_partido.equipo_local, nuevo_partido.equipo_visitante
        ))
        
        conflictos = cursor.fetchall()
        for partido_conflictivo in conflictos:
            equipo_loc_db = partido_conflictivo['equipo_local']
            equipo_vis_db = partido_conflictivo['equipo_visitante']
            
            if nuevo_partido.equipo_local in [equipo_loc_db, equipo_vis_db]:
                raise ValueError(f"{nuevo_partido.equipo_local} ya juega un partido en la fecha {nuevo_partido.fecha}.")
            if nuevo_partido.equipo_visitante in [equipo_loc_db, equipo_vis_db]:
                raise ValueError(f"{nuevo_partido.equipo_visitante} ya juega un partido en la fecha {nuevo_partido.fecha}.")

    finally:
        cursor.close()
        conexion.close()
 

#Defino la función PUT para actualizar los resultados de los partidos. En caso de no haber actualización, devuelve none
def actualizar_resultado(id_partido, goles_local, goles_visitante):
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)

    try:
        #Verifica que el partido exista
        query_partido = """
            SELECT id, equipo_local, equipo_visitante, fecha, fase, estadio, ciudad
            FROM partidos
            WHERE id = %s
        """

        cursor.execute(query_partido, (id_partido,))
        partido = cursor.fetchone() 

        if not partido:
            return None

        #Verifica si existe el resultado para el partido buscado
        query_resultado = """
            SELECT id
            FROM resultados
            WHERE id = %s
        """

        cursor.execute(query_resultado,(id_partido,))
        resultado_existente = cursor.fetchone()

        if resultado_existente:
            
            #Se actualiza
            resultado_actualizado = """
            UPDATE resultados
            SET goles_local = %s,
                goles_visitante = %s,
                jugado = %s
            WHERE id = %s
            """
            cursor.execute(resultado_actualizado, (goles_local, goles_visitante, True, id_partido))
        else:
            insert_resultado = """
            INSERT INTO resultados (id, goles_local, goles_visitante, jugado)
            VALUES (%s, %s, %s, %s)
            """

            cursor.execute(insert_resultado, (id_partido, goles_local, goles_visitante, True))
        
        conexion.commit()

        #Se arma una respuesta final
        partido_actualizado = {
                "id": partido["id"],
                "equipo_local": partido["equipo_local"],
                "equipo_visitante": partido["equipo_visitante"],
                "fecha": str(partido["fecha"]),
                "fase": partido["fase"],
                "estadio": partido["estadio"],
                "ciudad": partido["ciudad"],
                "goles_local": goles_local,
                "goles_visitante": goles_visitante
            }

        return partido_actualizado

    except Exception as e:
        conexion.rollback()
        raise Exception(f"Error al actualizar el resultado: {str(e)}")

    finally:
        cursor.close()
        conexion.close()





#defino la función de PUT para partidos
def actualizar_partidos(id, equipo_local, equipo_visitante, fecha, fase, estadio, ciudad):
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)

    try:
        #Verifica la existencia del partido
        query_buscar = """
        SELECT id
        FROM partidos
        WHERE id = %s
        """ 
        cursor.execute(query_buscar, (id,))
        partido_existentte = cursor.fetchone()

        if not partido_existentte:
           return None
   
        #actualiza datos del partido
        query_actualizada = """
            UPDATE partidos
            SET equipo_local = %s,
                equipo_visitante = %s, 
                fecha = %s,
                fase = %s,
                estadio = %s, 
                ciudad = %s
            WHERE id = %s
        """

        cursor.execute(query_actualizada, (
            equipo_local, 
            equipo_visitante,
            fecha,
            fase,
            estadio,
            ciudad,
            id 
        ))

        conexion.commit()

        #Traer partido actualizado y el resultado si existe
        query_detalle = """
           SELECT p.id, p.equipo_local, p.equipo_visitante, p.fecha, p.fase,
                  p.estadio, p.ciudad,
                  r.goles_local, r.goles_visitante
           FROM partidos p
           LEFT JOIN resultados r ON p.id = r.id
           WHERE p.id = %s
        """

        cursor.execute(query_detalle, (id,))
        partido = cursor.fetchone()

        if not partido:
            return None

        partido_actualizado = {
                "id": partido["id"],
                "equipo_local": partido["equipo_local"],
                "equipo_visitante": partido["equipo_visitante"],
                "fecha": str(partido["fecha"]),
                "fase": partido["fase"],
                "estadio": partido["estadio"],
                "ciudad": partido["ciudad"],
                "goles_local": partido["goles_local"],
                "goles_visitante": partido["goles_visitante"]
        }

        return partido_actualizado

    except Exception as e:
        conexion.rollback()
        raise Exception(f"Error al actualizar el partido: {str(e)}")
    
    finally:
        cursor.close()
        conexion.close()


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

def crear_prediccion(partido_id, usuario_id, goles_local, goles_visitante):
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("SELECT jugado FROM resultados WHERE id = %s", (partido_id,))
        resultado_partido = cursor.fetchone()
        if resultado_partido and resultado_partido.get('jugado'):
            raise Exception("PARTIDO_JUGADO")

        consulta = """
            INSERT INTO predicciones (usuario_id, partido_id, goles_local, goles_visitante) 
            VALUES (%s, %s, %s, %s)
        """
        valores = (usuario_id, partido_id, goles_local, goles_visitante)
        
        cursor.execute(consulta, valores)
        conexion.commit()

        return {
            "id": cursor.lastrowid,
            "usuario_id": usuario_id,
            "partido_id": partido_id,
            "goles_local": goles_local,
            "goles_visitante": goles_visitante
        }

    except Exception as e:
        conexion.rollback()
        # El código 1062 es para violaciones a constraints de unicidad (el UNIQUE de tu BD)
        if hasattr(e, 'errno') and e.errno == 1062:
            raise Exception("DUPLICADA")
        # El código 1452 es para violaciones a foreign key (usuario_id o partido_id no existen)
        elif hasattr(e, 'errno') and e.errno == 1452:
             raise Exception("USUARIO O PARTIDO NO ENCONTRADO")
        else:
            raise Exception(f"Error al crear predicción: {str(e)}")
    finally:
        cursor.close()
        conexion.close()

# Función para actualizar parcialmente un partido (PATCH)
def actualizar_partido_parcial(id, **kwargs):
    df = pd.read_csv('data/partidos.csv')

    partido_encontrado = False
    partido_actualizado = None

    for i in range(len(df)):
        if int(df.loc[i, 'id']) == id:
            # Actualizar solo los campos proporcionados
            if 'equipo_local' in kwargs:
                df.loc[i, 'equipo_local'] = kwargs['equipo_local']
            if 'equipo_visitante' in kwargs:
                df.loc[i, 'equipo_visitante'] = kwargs['equipo_visitante']
            if 'fecha' in kwargs:
                df.loc[i, 'fecha'] = kwargs['fecha']
            if 'fase' in kwargs:
                df.loc[i, 'fase'] = kwargs['fase']
            if 'estadio' in kwargs:
                df.loc[i, 'estadio'] = kwargs['estadio']
            if 'ciudad' in kwargs:
                df.loc[i, 'ciudad'] = kwargs['ciudad']
            if 'goles_local' in kwargs:
                df.loc[i, 'goles_local'] = kwargs['goles_local']
            if 'goles_visitante' in kwargs:
                df.loc[i, 'goles_visitante'] = kwargs['goles_visitante']

            partido_encontrado = True

            # Construir el diccionario actualizado
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
                "fase": str(df.loc[i, 'fase']),
                "estadio": str(df.loc[i, 'estadio']),
                "ciudad": str(df.loc[i, 'ciudad']),
                "goles_local": goles_local,
                "goles_visitante": goles_visitante
            }

            break

    if not partido_encontrado:
        return None

    df.to_csv('data/partidos.csv', index=False)

    return partido_actualizado

# Función para eliminar un partido (DELETE)
def eliminar_partido(id):
    df = pd.read_csv('data/partidos.csv')

    partido_encontrado = False

    for i in range(len(df)):
        if int(df.loc[i, 'id']) == id:
            df = df.drop(i)
            partido_encontrado = True
            break

    if not partido_encontrado:
        return False

    df.to_csv('data/partidos.csv', index=False)

    return True