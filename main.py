import requests
import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta
import re

load_dotenv()

ZOOM_ACCOUNT_ID = os.getenv('ZOOM_ACCOUNT_ID')
ZOOM_CLIENT_ID = os.getenv('ZOOM_CLIENT_ID')
ZOOM_CLIENT_SECRET = os.getenv('ZOOM_CLIENT_SECRET')

POSTGRE_HOST = os.getenv('POSTGRE_HOST')
POSTGRE_USER = os.getenv('POSTGRE_USER')
POSTGRE_PASSWORD = os.getenv('POSTGRE_PASSWORD')
POSTGRE_DATABASE = os.getenv('POSTGRE_DATABASE')

class ZoomClient: 

    def __init__(self, account_id, client_id, client_secret) -> None:
        self.account_id = account_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = self.get_access_token()
        self.base_dir = "Reuniones_DataGrowth"
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    # Obtener token de acceso
    def get_access_token(self):
        data = {
            "grant_type": "account_credentials",
            "account_id": self.account_id,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.post("https://zoom.us/oauth/token", data=data)
        return response.json()["access_token"]
    
    # Conectar a PostgreSQL
    def get_postgre_connection(self):
        try:
            connection = psycopg2.connect(
                host=POSTGRE_HOST,
                user=POSTGRE_USER,
                password=POSTGRE_PASSWORD,
                database=POSTGRE_DATABASE
            )
            print("Connected to PostgreSQL database")
            return connection
        except Error as e:
            print(f"Error connecting to PostgreSQL: {e}")
            return None
        
    def close_postgre_connection(self, connection):
        if connection is not None:
            connection.close()
#------------------------------------------> ENDPOINTS PARA UTILIZAR <------------------------------------------
 #--------------------------> OBTENER INFORMACIÓN REUNIÓN MEDIANTE EL ID <--------------------------
    def get_info_meeting(self, meetingId):
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        url = f"https://api.zoom.us/v2/past_meetings/{meetingId}"
        return requests.get(url, headers=headers).json()
       
#--------------------------> OBTENER LISTA DE PARTICIPANTES MEDIANTE EL ID DE UNA REUNIÓN <--------------------------
    def get_participants_by_id(self, meetingId):
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        url = f"https://api.zoom.us/v2/past_meetings/{meetingId}/participants"
        params = {
        "page_size": 400
        }
        return requests.get(url, headers=headers, params=params).json()

#--------------------------> OBTENER INFORMACIÓN DE LA ÚLTIMA REUNIÓN QUE ENTRÓ DG DEL DÍA <--------------------------

    # Esta es la real que me da la última reunión
    def get_last_meeting(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        url = f'https://api.zoom.us/v2/report/users/datagrowth.community@gmail.com/meetings'
        return requests.get(url, headers=headers).json()
    
#------------------------------------------> FUNCIONES PARA UTILIZAR <------------------------------------------
# FALTA VALIDAR ESTA MRD
#--------------------------> OBTENER LA LISTA DE PARTICIPANTES DE LA ÚLTIMA REUNIÓN <--------------------------
    def fun_get_participants_last_meeting(self):
        # Obtener la información de la última reunión
        rq_last_meeting = self.get_last_meeting()
        # Obtener la ID de la última reunión
        topic = rq_last_meeting['meetings'][0]['topic']
        meeting_id = rq_last_meeting['meetings'][0]['id']
        # Obtener los participantes de la última reunión
        rq_participantes = self.get_participants_by_id(meetingId=meeting_id)
        df = pd.DataFrame(rq_participantes['participants'])
        df.insert(0, 'meeting_name', topic)
        for participant in rq_participantes['participants']:
            participant['meeting_name'] = topic
        # Convertir el JSON a un DataFrame
        nombre_fecha = str((pd.to_datetime(df['join_time']) - pd.Timedelta(hours=5)).dt.date.iloc[0])
        df = df.to_csv(f'{self.base_dir}/{re.sub(r"[:/]", "_", topic)}_{nombre_fecha}.csv', index=False, encoding='utf-8')
        # Exportar a CSV si es necesario
        return self.insert_participants_into_postgre(rq_participantes)
    
#---------------------> OBTENER LA LISTA DE PARTICIPANTES MEDIANTE EL ID DE UNA REUNIÓN <---------------------
    def fun_get_participants_by_meeting_id(self, meetingId):
        rq_participantes = self.get_participants_by_id(meetingId)
        # Convertir el JSON a un DataFrame
        rq_topic_meeting = self.get_info_meeting(meetingId)
        topic = rq_topic_meeting['topic']
        df = pd.DataFrame(rq_participantes['participants'])
        df.insert(0, 'meeting_name', topic)
        for participant in rq_participantes['participants']:
            participant['meeting_name'] = topic
        nombre_fecha = str((pd.to_datetime(df['join_time']) - pd.Timedelta(hours=5)).dt.date.iloc[0])
        df = df.to_csv(f'{self.base_dir}/{re.sub(r"[:/]", "_", topic)}_{nombre_fecha}.csv', index=False, encoding='utf-8')
        return self.insert_participants_into_postgre(rq_participantes)
    
    def insert_participants_into_postgre(self, participants_json):
        connection = self.get_postgre_connection()
        if connection is None:
            return

        cursor = connection.cursor()
        
        truncate_query = 'TRUNCATE TABLE test'
        cursor.execute(truncate_query)
        
        insert_query  = '''INSERT INTO test(meeting_name, id, user_id, name, user_email, join_time, leave_time,
                                            duration, registrant_id, failover, status, groupId)
                                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''

        data_list = [
            (
                participant.get('meeting_name'),
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
            )
            for participant in participants_json['participants']
        ]
        
        cursor.executemany(insert_query, data_list)
        connection.commit()
        self.close_postgre_connection(connection)

client = ZoomClient(account_id=ZOOM_ACCOUNT_ID, client_id=ZOOM_CLIENT_ID, client_secret=ZOOM_CLIENT_SECRET)
#client.fun_get_participants_last_meeting()
client.fun_get_participants_by_meeting_id('86754030805')