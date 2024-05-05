import requests
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

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
        self.base_dir = "etl-dg/MedallionArchitecture"
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
    
#------------------------------------------------------------------------------------------------------------------------> 
    # Obtener última reunión
    def get_last_meeting(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        url = f"https://api.zoom.us/v2/users/me/meetings"
        params = {
        "type": "past",
        "page_size": 9,
        "sort_by": "start_time",
        "sort_order": "asc"
        }
        response = requests.get(url, headers=headers, params=params).json()
        meetings = response.get("meetings", [])
        if meetings:
            last_meeting = meetings[-1]
            return last_meeting
        else:
            return None
        #return print(requests.get(url, headers=headers, params=params).json())


#------------------------> Obtener reunión mediante una fecha de inicio y fecha de fin. <------------------------
    def get_last_meeting_date(self, from_date=None, to_date=None):
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        url = "https://api.zoom.us/v2/users/me/meetings"
        if from_date is not None or to_date is not None:
            url += "?"
            if from_date is not None:
                url += f"from={from_date}"
            if to_date is not None:
                url += f"&to={to_date}"
        return print(requests.get(url, headers=headers).json())
    
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
#--------------------------> OBTENER INFORMACIÓN REUNIÓN MEDIANTE EL ID <--------------------------
    def get_info_meeting(self, meetingId):
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        url = f"https://api.zoom.us/v2/past_meetings/{meetingId}"
        return requests.get(url, headers=headers).json()







#------------------------------------------> FUNCIONES PARA UTILIZAR <------------------------------------------
#--------------------------> OBTENER LA LISTA DE PARTICIPANTES DE LA ÚLTIMA REUNIÓN <--------------------------
    def fun_get_participants_last_meeting(self):
        # Obtener la información de la última reunión
        rq_last_meeting = self.get_last_meeting()
        # Obtener la ID de la última reunión
        topic = rq_last_meeting['topic']
        meeting_id = rq_last_meeting['id']
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
    
#----------------------------------------> MEDALLION ARCHITECTURE <----------------------------------------
#----------------------------------------> BRONZE LAYER <----------------------------------------
    def bronze_layer(self, data, topic = None, nombre_fecha = None):
        df = pd.DataFrame(data)
        ruta_bronze = f'{self.base_dir}/{self.folders[0]}'
        ruta_silver = f'{self.base_dir}/{self.folders[1]}'
        # No quitar esa mmdota.
        topic = topic.replace(': ', '_')
        df = df.to_csv(f'{ruta_bronze}/{topic}_{nombre_fecha}.csv', index=False, encoding='latin-1')
        return df
#----------------------------------------> SILVER LAYER <----------------------------------------    
    def silver_layer(self, topic = None, nombre_fecha = None):
        ruta_bronze = f'{self.base_dir}/{self.folders[0]}'
        ruta_silver = f'{self.base_dir}/{self.folders[1]}'
        topic = topic.replace(': ', '_') 
        df = pd.read_csv(f'{ruta_bronze}/{topic}_{nombre_fecha}.csv', encoding='latin-1')
        df.to_csv(f'{ruta_silver}/{topic}_{nombre_fecha}.csv', index=False, encoding='latin-1')
        return df
    
    def gold_layer(self, topic = None, nombre_fecha = None):
        ruta_bronze = f'{self.base_dir}/{self.folders[0]}'
        ruta_silver = f'{self.base_dir}/{self.folders[1]}'
        ruta_gold = f'{self.base_dir}/{self.folders[2]}'
        topic = topic.replace(': ', '_')
        df = pd.read_csv(f'{ruta_silver}/{topic}_{nombre_fecha}.csv', encoding='latin-1')
        df.to_csv(f'{ruta_gold}/{topic}_{nombre_fecha}.csv', index=False, encoding='latin-1')
        return df