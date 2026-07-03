import mysql.connector
from mysql.connector import Error
from config import *

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        if conexion.is_connected():
            print("¡Conexión exitosa a la base de datos!")
            return conexion

    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Ejemplo de uso
mi_conexion = obtener_conexion()

if mi_conexion:
    print("La conexión está lista para usarse.")
    mi_conexion.close()