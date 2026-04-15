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