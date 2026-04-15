import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'test',
    'database': 'prode'    
}

# db_config = {
#     'host': 'localhost',
#     'port': 3307,          
#     'user': 'root',
#     'password': '',        
#     'database': 'prode',    
#     'use_pure': True  
# }

def get_db_connection():
    #iniciar conexion con base de datos
    conn = mysql.connector.connect(**db_config)
    return conn

def execute(query):
    conexion = get_db_connection()
    cursor = conexion.cursor(dictionary=True)#devuelve diccionarios en vez de tuplas
    try:
        cursor.execute(query)
        resultados = cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()
    
    return resultados

def init_db(sql_file_path='initds_db.sql'):
    """
    Lee un archivo .sql y ejecuta cada una de las sentencias en la base de datos.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_script = file.read()
            
        for statement in sql_script.split(';'):
            if statement.strip():
                cursor.execute(statement)
                conn.commit()
                
        print("Base de datos inicializada correctamente.")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
    finally:
        cursor.close()
        conn.close()