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
#client.fun_get_participants_last_meeting()

#client.fun_get_participants_last_meeting()
#client.get_participants_by_id('83285264309')
client.fun_get_participants_by_meeting_id('83285264309')
