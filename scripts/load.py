# Función para cargar data a la DB.

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
MYSQL_PORT = os.getenv('puerto')

def get_mysql_connection():
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            port=MYSQL_PORT
        )
        print("Conectado a la base de datos MySQL")
        return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def close_mysql_connection(connection):
    if connection is not None:
        connection.close()

def insert_participants_into_mysql(participants_json):
    connection = get_mysql_connection()
    if connection is None:
        return

    cursor = connection.cursor()
    tabla_db = 'tde_reuniones_zoom_test'

    # Limpiar la tabla antes de insertar nuevos datos
    truncate_query = f'TRUNCATE TABLE {tabla_db}'
    cursor.execute(truncate_query)

    # Consulta para insertar datos
    insert_query = f'''
    INSERT INTO {tabla_db} (
        meeting_name, id, user_id, name, user_email, join_time, leave_time,
        duration, registrant_id, failover, status, groupId
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''

    # Construir los datos a partir del JSON de la API
    data_list = []
    for meeting in participants_json:
        meeting_name = meeting.get('meeting', {}).get('topic', 'Sin título')
        participants = meeting.get('participants', [])
        
        for participant in participants:
            data_list.append((
                meeting_name,
                participant.get('id'),
                participant.get('user_id'),
                participant.get('name'),
                participant.get('user_email'),
                participant.get('join_time'),
                participant.get('leave_time'),
                participant.get('duration'),
                participant.get('registrant_id'),
                participant.get('failover'),
                participant.get('status'),
                participant.get('groupId')
            ))

    # Ejecutar la inserción masiva
    try:
        cursor.executemany(insert_query, data_list)
        connection.commit()
        print(f"Se insertaron {cursor.rowcount} registros en la base de datos.")
    except Error as e:
        print(f"Error al insertar datos: {e}")
    finally:
        close_mysql_connection(connection)
