import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def create_connection():
    """Crea y devuelve una conexión a la base de datos."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),  
            password=os.getenv('DB_PASSWORD', ''), 
            database=os.getenv('DB_NAME', 'GestionDeEstudiantes'),
            port=int(os.getenv('DB_PORT', '3306'))
        )
        return connection
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None