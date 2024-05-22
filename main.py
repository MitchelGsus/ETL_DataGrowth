import os
from dotenv import load_dotenv
import pandas as pd
from zoom import ZoomClient
load_dotenv()

ZOOM_ACCOUNT_ID = os.getenv('ZOOM_ACCOUNT_ID')
ZOOM_CLIENT_ID = os.getenv('ZOOM_CLIENT_ID')
ZOOM_CLIENT_SECRET = os.getenv('ZOOM_CLIENT_SECRET')


client = ZoomClient(account_id=ZOOM_ACCOUNT_ID, client_id=ZOOM_CLIENT_ID, client_secret=ZOOM_CLIENT_SECRET)

#--------------------------> OBTENER LA LISTA DE PARTICIPANTES DE LA ÚLTIMA REUNIÓN <--------------------------
client.fun_get_participants_last_meeting()
#--------------------------> OBTENER LA LISTA DE PARTICIPANTES MEDIANTE LA ID DE UNA REUNIÓN <--------------------------
#client.fun_get_participants_by_meeting_id(meetingId='86546157951')
#85136892185
#client.fun_get_participants_by_meeting_id(meetingId='81514348118')
