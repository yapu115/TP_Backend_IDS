from mysql_db import get_db_connection

def obtener_usuario_por_id(id):
    
    conexion = get_db_connection()
    # Devuelve los resultados como diccionario
    cursor = conexion.cursor(dictionary=True)   
    try:
        #consulta_sql guarda las intrucciones que van a ser enviadas a la base de datos
        consulta_sql = "SELECT id, nombre, mail FROM usuarios WHERE id = %s"
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
        consulta = 'UPDATE usuarios SET nombre = %s, mail = %s WHERE id = %s'
        
        #Se realiza la consulta a la base de datos
        cursor.execute(consulta, (nombre, mail, id))
        
        #Guarda los cambios
        conexion.commit()
        
        #Analiza si se hicieron cambios en la base de datos
        if cursor.rowcount == 0:
            return None  
        return {"id": id, "nombre": nombre, "mail": mail}
        
    finally:
        cursor.close()
        conexion.close()

    
