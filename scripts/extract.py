# Función para conectarnos a la API de ZOOM.

import requests
import os
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

ZOOM_ACCOUNT_ID = os.getenv('ZOOM_ACCOUNT_ID')
ZOOM_CLIENT_ID = os.getenv('ZOOM_CLIENT_ID')
ZOOM_CLIENT_SECRET = os.getenv('ZOOM_CLIENT_SECRET')

# Función para obtener el token de acceso
def get_access_token(ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET):
    data = {
        "grant_type": "account_credentials",
        "account_id": ZOOM_ACCOUNT_ID,
        "client_id": ZOOM_CLIENT_ID,
        "client_secret": ZOOM_CLIENT_SECRET
    }
    response = requests.post("https://zoom.us/oauth/token", data=data)
    return response.json().get("access_token")

# Función para obtener las reuniones del día actual
def get_historical_meetings(access_token, user_id="hBmGFN0HSIKei4Av3pqQhg"):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    today = datetime.today().strftime("%Y-%m-%d")
    url = f"https://api.zoom.us/v2/report/users/{user_id}/meetings"
    params = {
        "from": today, #"2024-12-12"
        "to": today #"2024-12-12"
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Función para obtener los participantes de una reunión por UUID
def get_participants_by_uuid(access_token, uuid):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    url = f"https://api.zoom.us/v2/past_meetings/{uuid}/participants"
    params = {
        "page_size": 400
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Función para extraer las reuniones y sus participantes
def extract_meetings():
    access_token = get_access_token(ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET)
    meetings_data = []

    # Obtener las reuniones del día actual
    meeting_response = get_historical_meetings(access_token)
    if "meetings" not in meeting_response or not meeting_response['meetings']:
        print("No se encontraron reuniones.")
        return meetings_data

    uuids = [meeting['uuid'] for meeting in meeting_response['meetings']]
    print(f"UUIDs encontrados: {uuids}")

    # Iterar sobre los UUIDs para procesar cada reunión
    for uuid, meeting in zip(uuids, meeting_response['meetings']):
        participants_response = get_participants_by_uuid(access_token, uuid)
        if 'participants' not in participants_response:
            continue

        # Recoger los datos de la reunión y los participantes
        meetings_data.append({
            'meeting': meeting,
            'participants': participants_response['participants']
        })

    return meetings_data
