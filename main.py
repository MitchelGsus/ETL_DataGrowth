import os
from dotenv import load_dotenv
import pandas as pd
from zoom import ZoomClient
load_dotenv()

ZOOM_ACCOUNT_ID = os.getenv('ZOOM_ACCOUNT_ID')
ZOOM_CLIENT_ID = os.getenv('ZOOM_CLIENT_ID')
ZOOM_CLIENT_SECRET = os.getenv('ZOOM_CLIENT_SECRET')


client = ZoomClient(account_id=ZOOM_ACCOUNT_ID, client_id=ZOOM_CLIENT_ID, client_secret=ZOOM_CLIENT_SECRET)

""" #--------------------------> OBTENER LA LISTA DE PARTICIPANTES DE LA ÚLTIMA REUNIÓN <--------------------------
# Obtener info de la última reunión.
rq_last_meeting = client.get_last_meeting()
# Obtener la ID de la reunión.
meeting_id = ', '.join([str(meeting['id']) for meeting in rq_last_meeting['meetings']])
# Obtener los participantes de la última reunión.
rq_participantes = client.get_meetings_by_id(meetingId=meeting_id)
# Convertir json a DataFrame.
df = pd.DataFrame(rq_participantes['participants'])
df.to_csv('testeo.csv', index=False) """
client.get_participants_last_meeting(nombre_archivo='testeo.csv')