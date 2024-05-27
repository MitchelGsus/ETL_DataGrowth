import requests
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta
import re

## Token is = 
load_dotenv()

ZOOM_ACCOUNT_ID = os.getenv('ZOOM_ACCOUNT_ID')
ZOOM_CLIENT_ID = os.getenv('ZOOM_CLIENT_ID')
ZOOM_CLIENT_SECRET = os.getenv('ZOOM_CLIENT_SECRET')

class ZoomClient:
        

    def __init__(self, account_id, client_id, client_secret) -> None:
        self.account_id = account_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = self.get_access_token()
        self.base_dir = "MedallionArchitecture"
        # Nombres de las carpetas
        self.folders = ["Bronze", "Silver", "Gold"]
        if not os.path.exists(self.base_dir):
            for folder in self.folders:
                path = os.path.join(self.base_dir, folder)
                # Comprobar si la carpeta ya existe
                if not os.path.exists(path):
                    os.makedirs(path)

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
    
#------------------------------------------> ENDPOINTS PARA UTILIZAR <------------------------------------------
    
#--------------------------> OBTENER LA LISTA DE PARTICIPANTES MEDIANTE EL ID DE UNA REUNIÓN <--------------------------
    def get_participants_by_id(self, meetingId):
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        url = f"https://api.zoom.us/v2/past_meetings/{meetingId}/participants"
        params = {
        "page_size": 400
        }
        return requests.get(url, headers=headers, params=params).json()

#--------------------------> OBTENER INFORMACIÓN DE LA ÚLTIMA REUNIÓN <--------------------------

    # Esta es la real que me da la última reunión
    def get_last_meeting(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        url = f'https://api.zoom.us/v2/report/users/datagrowth.community@gmail.com/meetings'
        return requests.get(url, headers=headers).json()
    
    def test2(self, meetingId):
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        params = {
            "page_size": 400
            }
        url = f'https://api.zoom.us/v2/report/meetings/{meetingId}/participants'
        return print(requests.get(url, headers=headers, params=params).json())
    

#------------------------------------------> FUNCIONES PARA UTILIZAR <------------------------------------------
#--------------------------> OBTENER LA LISTA DE PARTICIPANTES DE LA ÚLTIMA REUNIÓN <--------------------------
    def fun_get_participants_last_meeting(self):
        # Obtener la información de la última reunión
        rq_last_meeting = self.get_last_meeting()
        # Obtener la ID de la última reunión
        topic = rq_last_meeting['meetings'][0]['topic']
        meeting_id = rq_last_meeting['meetings'][0]['id']
        # Obtener los participantes de la última reunión
        rq_participantes = self.get_participants_by_id(meetingId=meeting_id)
        # Convertir el JSON a un DataFrame
        df = pd.DataFrame(rq_participantes['participants'])
        df.insert(0, 'meeting_name', topic)
        nombre_fecha = str((pd.to_datetime(df['join_time']) - pd.Timedelta(hours=5)).dt.date.iloc[0])
        # Exportar a CSV si es necesario
        self.bronze_layer(data = df, topic = topic, nombre_fecha= nombre_fecha)
        self.silver_layer(topic = topic, nombre_fecha= nombre_fecha)
        self.gold_layer(topic = topic, nombre_fecha= nombre_fecha)
        return df
    
#---------------------> OBTENER LA LISTA DE PARTICIPANTES MEDIANTE EL ID DE UNA REUNIÓN <---------------------
    def fun_get_participants_by_meeting_id(self, meetingId):
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        url = f"https://api.zoom.us/v2/past_meetings/{meetingId}/participants"
        params = {
        "page_size": 400
    }
        rq_participantes = requests.get(url, headers=headers, params=params).json()
        # Convertir el JSON a un DataFrame
        rq_topic_meeting = self.get_info_meeting(meetingId)
        topic = rq_topic_meeting['topic']
        df = pd.DataFrame(rq_participantes['participants'])
        df.insert(0, 'meeting_name', topic)
        nombre_fecha = str((pd.to_datetime(df['join_time']) - pd.Timedelta(hours=5)).dt.date.iloc[0])
        self.bronze_layer(data = df, topic = topic, nombre_fecha= nombre_fecha)
        self.silver_layer(topic = topic, nombre_fecha= nombre_fecha)
        self.gold_layer(topic = topic, nombre_fecha= nombre_fecha)
        return df

    def limpiar_texto(self, texto):
        texto = re.sub(r'\s+', ' ', texto) 
        texto = re.sub(r'[^\w\sáéíóúü]', '', texto)
        return texto.strip()  
#----------------------------------------> MEDALLION ARCHITECTURE <----------------------------------------
#----------------------------------------> BRONZE LAYER <----------------------------------------
    def bronze_layer(self, data, topic = None, nombre_fecha = None):
        df = pd.DataFrame(data)
        ruta_bronze = f'{self.base_dir}/{self.folders[0]}'
        # No quitar esa mmdota.
        topic = topic.replace(': ', '_')
        df = df.to_csv(f'{ruta_bronze}/{topic}_{nombre_fecha}.csv', index=False, encoding='utf-8')
        return df #print(f'{ruta_bronze}/{topic}_{nombre_fecha}.csv')

#----------------------------------------> SILVER LAYER <----------------------------------------    
    def silver_layer(self, topic = None, nombre_fecha = None):
        ruta_bronze = f'{self.base_dir}/{self.folders[0]}'
        ruta_silver = f'{self.base_dir}/{self.folders[1]}'
        topic = topic.replace(': ', '_') 
        df = pd.read_csv(f'{ruta_bronze}/{topic}_{nombre_fecha}.csv', encoding='utf-8')
        df_final = df[['meeting_name', 'name', 'user_email', 'join_time', 'leave_time', 'duration']]
        df_final = df_final.rename(columns={'meeting_name': 'nombre_reunion', 'name': 'nombre', 'user_email': 'correo_electronico', 'join_time': 'tiempo_ingreso', 'leave_time': 'tiempo_salio', 'duration': 'duracion_segundos'})
        df_final.astype(str)
        # Convertir a formato datetime
        df_final['tiempo_ingreso'] = pd.to_datetime(df_final['tiempo_ingreso'])
        df_final['tiempo_salio'] = pd.to_datetime(df_final['tiempo_salio'])
        # A
        df_final['tiempo_ingreso'] = df_final['tiempo_ingreso'] - pd.Timedelta(hours=5)
        df_final['tiempo_salio'] = df_final['tiempo_salio'] - pd.Timedelta(hours=5)
        # B
        df_final['tiempo_ingreso'] = df_final['tiempo_ingreso'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        df_final['tiempo_salio'] = df_final['tiempo_salio'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        # B.2
        df_final['tiempo_ingreso'] = pd.to_datetime(df_final['tiempo_ingreso'])
        df_final['tiempo_salio'] = pd.to_datetime(df_final['tiempo_salio'])
        # C
        df_final['fecha_ingreso'] = df_final['tiempo_ingreso'].dt.date
        df_final['hora_ingreso'] = df_final['tiempo_ingreso'].dt.time
        df_final['fecha_salio'] = df_final['tiempo_salio'].dt.date
        df_final['hora_salio'] = df_final['tiempo_salio'].dt.time
        # D
        df_final['tiempo_ingreso'] = pd.to_datetime(df_final['tiempo_ingreso']).dt.tz_localize(None)
        df_final['tiempo_salio'] = pd.to_datetime(df_final['tiempo_salio']).dt.tz_localize(None)
        # F
        # df_final['hora_ingreso'] = pd.to_datetime(df_final['hora_ingreso'], format='%H:%M:%S')
        # df_final['hora_ingreso'] = df_final['hora_ingreso'] - timedelta(hours=5)
        # df_final['hora_ingreso'] = df_final['hora_ingreso'].dt.strftime('%H:%M:%S')
        df_final[['hora_ingreso', 'hora_salio']] = df_final[['hora_ingreso', 'hora_salio']].apply(lambda x: pd.to_datetime(x, format='%H:%M:%S') - timedelta(hours=5))
        df_final[['hora_ingreso', 'hora_salio']] = df_final[['hora_ingreso', 'hora_salio']].apply(lambda x: x.dt.strftime('%H:%M:%S'))
        # G
        df_final['nombre'] = df_final['nombre'].str.lower()
        df_final['nombre'] = df_final['nombre'].apply(self.limpiar_texto)
        df_final = df_final[['nombre_reunion', 'nombre', 'correo_electronico', 'fecha_ingreso', 'hora_ingreso', 'fecha_salio', 'hora_salio', 'duracion_segundos']]

        df_final.to_csv(f'{ruta_silver}/{topic}_{nombre_fecha}.csv', index=False, encoding='utf-8')
        return df_final
#----------------------------------------> GOLD LAYER <----------------------------------------   
    
    def gold_layer(self, topic = None, nombre_fecha = None):
        ruta_silver = f'{self.base_dir}/{self.folders[1]}'
        ruta_gold = f'{self.base_dir}/{self.folders[2]}'
        topic = topic.replace(': ', '_')
        df = pd.read_csv(f'{ruta_silver}/{topic}_{nombre_fecha}.csv', encoding='utf-8')
        df_final = df.groupby('correo_electronico').agg({
        'nombre': 'first',
        'fecha_ingreso': 'min',
        'fecha_salio': 'max',
        'hora_ingreso': 'min',
        'hora_salio': 'max',
        'duracion_segundos': 'sum',
        'nombre_reunion': 'first'}).reset_index()

        df_final['duracion_segundos'] = df_final['duracion_segundos'].astype(int)  # Convertir a entero
        df_final['duracion_minutos'] = df_final['duracion_segundos'].apply(lambda x: x // 60)
        df_final['duracion_horas'] = df_final['duracion_segundos'].apply(lambda x: str((datetime(1900, 1, 1) + timedelta(seconds=x)).time()))
        df_final = df_final[['nombre_reunion', 'nombre', 'correo_electronico', 'fecha_ingreso', 'hora_ingreso', 'fecha_salio', 'hora_salio', 'duracion_segundos', 'duracion_minutos', 'duracion_horas']]
        df_final.astype(str)

        df_final.to_csv(f'{ruta_gold}/{topic}_{nombre_fecha}.csv', index=False, encoding='utf-8')
        return df_final