import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import time

load_dotenv()


class NullCursor:
    def execute(self, *args, **kwargs):
        return None

    def fetchone(self):
        return None

    def fetchall(self):
        return []

    def close(self):
        return None


class NullConnection:
    """Objeto conexión nulo que evita que la app lance excepciones si no hay DB."""
    def cursor(self, dictionary=False):
        return NullCursor()

    def commit(self):
        return None

    def close(self):
        return None


def create_connection(retries: int = 3, delay: float = 1.0):
    """Intenta crear una conexión MySQL. Si falla, devuelve un objeto NullConnection.

    - Usa variables de entorno: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT
    - Reintenta 'retries' veces con 'delay' segundos.
    """
    host = os.getenv('DB_HOST', 'localhost')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')
    database = os.getenv('DB_NAME', 'GestionDeEstudiantes')
    port = int(os.getenv('DB_PORT', '3306'))

    last_error = None
    for attempt in range(1, retries + 1):
        try:
            connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port,
                connection_timeout=5
            )
            if connection.is_connected():
                print(f"Conectado a la base de datos MySQL en {host}:{port} (usuario={user}).")
                return connection
        except Exception as e:
            last_error = e
            print(f"Intento {attempt}/{retries} - Error al conectar a la base de datos {host}:{port}: {e}")
            time.sleep(delay)

    # Si llegamos aquí es porque no se pudo conectar
    print("No fue posible conectar a MySQL. Usando conexión nula (la aplicación funcionará en modo degradado).")
    print("Variables de conexión usadas:")
    print(f"  DB_HOST={host}")
    print(f"  DB_USER={user}")
    print(f"  DB_NAME={database}")
    print(f"  DB_PORT={port}")
    print(f"Último error: {last_error}")
    return NullConnection()