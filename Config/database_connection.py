import mysql.connector
from mysql.connector import Error

def create_connection():
    """Crea y devuelve una conexión a la base de datos."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  
            password='', 
            database='GestionDeEstudiantes'  
        )
        return connection
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None