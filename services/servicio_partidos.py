from models.PartidoBase import PartidoBase
from mysql_db import get_db_connection

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
    validar_nuevo_partido(partido)

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
    # Validación: Los goles deben ser números enteros y no negativos
    if not isinstance(goles_local, int) or not isinstance(goles_visitante, int):
        raise ValueError("Los goles deben ser números enteros")
    if goles_local < 0 or goles_visitante < 0:
        raise ValueError("Los goles no pueden ser negativos")
    
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
def actualizar_partidos(id, equipo_local, equipo_visitante, fecha, fase):
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
                fase = %s
            WHERE id = %s
        """

        cursor.execute(query_actualizada, (
            equipo_local, 
            equipo_visitante,
            fecha,
            fase,
            id 
        ))

        conexion.commit()

        #Traer partido actualizado y el resultado si existe
        query_detalle = """
           SELECT p.id, p.equipo_local, p.equipo_visitante, p.fecha, p.fase,
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
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)

    try:
        query = """
           SELECT p.id, p.equipo_local, p.equipo_visitante, p.fecha, p.fase,
                  r.goles_local, r.goles_visitante
           FROM partidos p
           LEFT JOIN resultados r ON p.id = r.id
           WHERE p.id = %s
        """
        cursor.execute(query, (id_partido,))
        partido = cursor.fetchone()

        if not partido:
            return None

        if partido['goles_local'] is not None and partido['goles_visitante'] is not None:
            resultado = {
                "local": partido['goles_local'],
                "visitante": partido['goles_visitante']
            }
        else:
            resultado = None

        return {
            "id": partido["id"],
            "equipo_local": partido["equipo_local"],
            "equipo_visitante": partido["equipo_visitante"],
            "fecha": str(partido["fecha"]),
            "fase": partido["fase"],
            "resultado": resultado
        }

    finally:
        cursor.close()
        conexion.close()

def crear_prediccion(partido_id, usuario_id, goles_local, goles_visitante):
    # Validación: Los goles deben ser números enteros y no negativos
    if not isinstance(goles_local, int) or not isinstance(goles_visitante, int):
        raise ValueError("Los goles deben ser números enteros")
    if goles_local < 0 or goles_visitante < 0:
        raise ValueError("Los goles no pueden ser negativos")
    
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
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)

    try:
        # 1. Comprobar que existe el partido
        cursor.execute("SELECT id FROM partidos WHERE id = %s", (id,))
        if not cursor.fetchone():
            return None

        # Validación del compañero para goles
        if 'goles_local' in kwargs:
            if not isinstance(kwargs['goles_local'], int) and kwargs['goles_local'] is not None:
                raise ValueError("Los goles deben ser números enteros")
            if kwargs['goles_local'] is not None and kwargs['goles_local'] < 0:
                raise ValueError("Los goles no pueden ser negativos")
                
        if 'goles_visitante' in kwargs:
            if not isinstance(kwargs['goles_visitante'], int) and kwargs['goles_visitante'] is not None:
                raise ValueError("Los goles deben ser números enteros")
            if kwargs['goles_visitante'] is not None and kwargs['goles_visitante'] < 0:
                raise ValueError("Los goles no pueden ser negativos")

        campos_partidos = []
        valores_partidos = []
        
        # Filtramos los campos permitidos que pertenecen a la tabla partidos
        campos_permitidos = ['equipo_local', 'equipo_visitante', 'fecha', 'fase']
        for campo in campos_permitidos:
            if campo in kwargs:
                campos_partidos.append(f"{campo} = %s")
                valores_partidos.append(kwargs[campo])

        # Hacemos UPDATE de la tabla partidos solo si hay campos de esa tabla
        if campos_partidos:
            query_partidos = f"UPDATE partidos SET {', '.join(campos_partidos)} WHERE id = %s"
            valores_partidos.append(id)
            cursor.execute(query_partidos, valores_partidos)

        # 2. Manejar la actualización de goles a la tabla dependiente
        if 'goles_local' in kwargs or 'goles_visitante' in kwargs:
            cursor.execute("SELECT id, goles_local, goles_visitante FROM resultados WHERE id = %s", (id,))
            resultado_existente = cursor.fetchone()

            # Tomamos valores nuevos O dejamos los que estaban en la base
            g_loc = kwargs.get('goles_local')
            g_vis = kwargs.get('goles_visitante')

            if resultado_existente:
                if g_loc is None: g_loc = resultado_existente['goles_local']
                if g_vis is None: g_vis = resultado_existente['goles_visitante']
                
                cursor.execute(
                    "UPDATE resultados SET goles_local = %s, goles_visitante = %s, jugado = TRUE WHERE id = %s", 
                    (g_loc, g_vis, id)
                )
            else:
                if g_loc is None: g_loc = 0
                if g_vis is None: g_vis = 0
                
                cursor.execute(
                    "INSERT INTO resultados (id, goles_local, goles_visitante, jugado) VALUES (%s, %s, %s, TRUE)", 
                    (id, g_loc, g_vis)
                )

        conexion.commit()

        # 3. Devolvemos el registro plano actualizado
        query_detalle = """
           SELECT p.id, p.equipo_local, p.equipo_visitante, p.fecha, p.fase,
                  r.goles_local, r.goles_visitante
           FROM partidos p
           LEFT JOIN resultados r ON p.id = r.id
           WHERE p.id = %s
        """
        cursor.execute(query_detalle, (id,))
        partido_bd = cursor.fetchone()

        partido_actualizado = {
            "id": partido_bd["id"],
            "equipo_local": partido_bd["equipo_local"],
            "equipo_visitante": partido_bd["equipo_visitante"],
            "fecha": str(partido_bd["fecha"]),
            "fase": partido_bd["fase"],
            "goles_local": partido_bd["goles_local"],
            "goles_visitante": partido_bd["goles_visitante"]
        }

        return partido_actualizado

    except Exception as e:
        conexion.rollback()
        raise Exception(f"Error al actualizar parcialmente mediante MySQL: {str(e)}")
    finally:
        cursor.close()
        conexion.close()

# Función para eliminar un partido (DELETE)
def eliminar_partido(id):
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)

    try:
        # 1. Comprobar que existe
        cursor.execute("SELECT id FROM partidos WHERE id = %s", (id,))
        if not cursor.fetchone():
            return False

        # 2. Las relaciones deben borrarse metódicamente en el orden adecuado (Claves foráneas)
        cursor.execute("DELETE FROM predicciones WHERE partido_id = %s", (id,))
        cursor.execute("DELETE FROM resultados WHERE id = %s", (id,))
        cursor.execute("DELETE FROM partidos WHERE id = %s", (id,))
        
        conexion.commit()
        return True

    except Exception as e:
        conexion.rollback()
        raise Exception(f"Error relacional al eliminar en MySQL: {str(e)}")
    finally:
        cursor.close()
        conexion.close()