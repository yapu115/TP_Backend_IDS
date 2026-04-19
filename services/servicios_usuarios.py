from mysql_db import get_db_connection

def crear_usuario(nombre, email):
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)
    try:
        #Consulta para insertar valores del nuevo usuario a la base de datos
        consulta = "INSERT INTO usuarios (nombre,email) VALUES (%s, %s)"
        
        #Ejecuta la consulta con los valores de datos (parametro)
        cursor.execute(consulta,(nombre, email))
        
        #Guarda los cambios
        conexion.commit()

        #toma el id autogenerado por la base de datos para el nnuevo usuario
        nuevo_id = cursor.lastrowid
        
        return {"id": nuevo_id, "nombre": nombre, "email": email}
    finally:
        cursor.close()
        conexion.close()

def mostrar_usuarios():
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)
    try:
        consulta = "SELECT * FROM usuarios"
        cursor.execute(consulta)
        usuarios = cursor.fetchall()

        return usuarios
    finally:
        cursor.close()
        conexion.close()


def obtener_usuario_por_id(id):
    
    conexion = get_db_connection()
    # Devuelve los resultados como diccionario
    cursor = conexion.cursor(dictionary=True)   
    try:
        #consulta_sql guarda las intrucciones que van a ser enviadas a la base de datos
        consulta_sql = "SELECT id, nombre, email FROM usuarios WHERE id = %s"
        #Envia las intrucciones a la base de datos
        cursor.execute(consulta_sql, (id,))
        #Guarda la fila correspondiente a ese usuario
        usuario = cursor.fetchone()
        
        return usuario  
    finally:
        cursor.close()
        conexion.close()

def actualizar_usuario(id, nombre, mail):
    
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)
    
    try:
        consulta = 'UPDATE usuarios SET nombre = %s, email = %s WHERE id = %s'
        
        #Se realiza la consulta a la base de datos
        cursor.execute(consulta, (nombre, mail, id))
        
        #Guarda los cambios
        conexion.commit()
        
        #Analiza si se hicieron cambios en la base de datos
        if cursor.rowcount == 0:
            return None  
        return {"id": id, "nombre": nombre, "email": mail}
        
    finally:
        cursor.close()
        conexion.close()

    
#Eliminar usuario a través del ID
def eliminar_usuario(id_usuario):
    print("ID RECIBIDO: ", id_usuario)

    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)

    try:
        #Verifica que el usuario exista
        query_buscar = """
            SELECT id, nombre, email
            FROM usuarios
            WHERE id = %s
        """
        print("Ejecutando busqueda en usuarios..")


        cursor.execute(query_buscar, (id_usuario,))
        usuario = cursor.fetchone()
        print("Usuario encontrado:", usuario)

        if not usuario:
           return None

        query_borrar_usuario = """
           DELETE FROM usuarios
           WHERE id = %s 
        """
        cursor.execute(query_borrar_usuario, (id_usuario,))
        conexion.commit()

        return usuario

    except Exception as e:
        conexion.rollback() 
        mensaje = str(e).lower()

        if "foreign key constraint fails" in mensaje:
           raise ValueError("No se puede eliminar el usuario porque tiene predicciones asociadas")
 
        raise Exception(f"Error al eliminar usuario: {str(e)}")

def obtener_ranking():
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)
    
    try:
        # Obtenemos usuarios con sus predicciones y los resultados de los partidos ya jugados
        query = """
            SELECT 
                u.id as usuario_id, 
                u.nombre, 
                p.goles_local as pred_local, 
                p.goles_visitante as pred_visitante,
                r.goles_local as res_local, 
                r.goles_visitante as res_visitante
            FROM usuarios u
            LEFT JOIN predicciones p ON u.id = p.usuario_id
            LEFT JOIN resultados r ON p.partido_id = r.id AND r.jugado = TRUE
        """
        cursor.execute(query)
        filas = cursor.fetchall()
        
        ranking = {}
        for fila in filas:
            usuario_id = fila['usuario_id']
            if usuario_id not in ranking:
                ranking[usuario_id] = {
                    "id_usuario": usuario_id,
                    "puntos": 0
                }
            
            # Solo calculamos si hay prediccion y el partido ya se jugó (tiene resultado)
            if fila['pred_local'] is not None and fila['res_local'] is not None:
                p_local = fila['pred_local']
                p_vis = fila['pred_visitante']
                r_local = fila['res_local']
                r_vis = fila['res_visitante']
                
                # Acierto exacto: 3 puntos
                if p_local == r_local and p_vis == r_vis:
                    ranking[usuario_id]["puntos"] += 3
                # Acierto de ganador/empate: 1 punto
                else:
                    dif_pred = p_local - p_vis
                    dif_res = r_local - r_vis
                    if (dif_pred > 0 and dif_res > 0) or \
                       (dif_pred < 0 and dif_res < 0) or \
                       (dif_pred == 0 and dif_res == 0):
                        ranking[usuario_id]["puntos"] += 1
                        
        # Convertimos a lista y ordenamos de mayor a menor puntaje
        ranking_lista = list(ranking.values())
        ranking_lista.sort(key=lambda x: x["puntos"], reverse=True)
        
        return ranking_lista
    finally:
        cursor.close()
        conexion.close()

