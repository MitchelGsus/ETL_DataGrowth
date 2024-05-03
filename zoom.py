import requests
import os
from dotenv import load_dotenv
import pandas as pd

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
        #tkn = 'eyJzdiI6IjAwMDAwMSIsImFsZyI6IkhTNTEyIiwidiI6IjIuMCIsImtpZCI6ImZkMDFmYmQ0LWYxZjMtNDFmNy1iYmFkLThlZGZkMWZlMjdmMyJ9.eyJhdWQiOiJodHRwczovL29hdXRoLnpvb20udXMiLCJ1aWQiOiJoQm1HRk4wSFNJS2VpNEF2M3BxUWhnIiwidmVyIjo5LCJhdWlkIjoiZWIwYzkzNmQ3Yjc4NGRkMmVhZGFlNDM2Y2Q4YjE3M2QiLCJuYmYiOjE3MTQ3NDU0MzIsImNvZGUiOiJpMlR6OWVfTlRNS0ZqUTIzUTltZDJ3OEtnM3R2R0paTjAiLCJpc3MiOiJ6bTpjaWQ6bEs4STNyWXRSVGFSRnM1ZURVZmhHZyIsImdubyI6MCwiZXhwIjoxNzE0NzQ5MDMyLCJ0eXBlIjozLCJpYXQiOjE3MTQ3NDU0MzIsImFpZCI6Ikk5ZGlrbWxRUkUtVnkyTUlJX00yelEifQ.D6Ry0oGEpZuDPi1TAnuC0FhRS2b9nILUkMm-cKaSqIqRhat68VIZ7wGEKQBbZkL72WHDbirGZ1y55hPjJ2vLAw'
        self.access_token = self.get_access_token()
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
    
    def __str__(self):
        return f"ZoomClient(account_id={self.account_id}, client_id={self.client_id}, client_secret={self.client_secret}, access_token={self.access_token})"

    def get_name_meetings(self, from_date=None, to_date=None):
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        url = f"https://api.zoom.us/v2/users/me/recordings"

        if from_date and to_date:
            url += f"?from={from_date}&to={to_date}"
        elif from_date:
            url += f"?from={from_date}"
        elif to_date:
            url += f"?to={to_date}"

        return requests.get(url, headers=headers).json()
    
    # Obtener última reunión
    def get_last_meeting(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        url = f"https://api.zoom.us/v2/users/me/meetings?type=past&page_size=1&sort_by=start_time&sort_order=desc"
        return requests.get(url, headers=headers).json()
    
    # Obtener todas las reuniones pasadas y futuras(que se hayan programado) | Aún falta validar la paginación
    def get_meetings_hist(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        url = f"https://api.zoom.us/v2/users/me/meetings"

        return requests.get(url, headers=headers).json()
    
    # Obtener todas las reuniones pasadas
    def get_meetings_hist_past(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        url = f"https://api.zoom.us/v2/users/me/meetings?type=past"
        return requests.get(url, headers=headers).json()
    
    # Obtener lista de participantes de una reunión por ID
    def get_meetings_by_id(self, meetingId):
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        url = f"https://api.zoom.us/v2/past_meetings/{meetingId}/participants"
        params = {
        "page_size": 300
    }
        return requests.get(url, headers=headers, params=params).json()



# client = ZoomClient(account_id=ZOOM_ACCOUNT_ID, client_id=ZOOM_CLIENT_ID, client_secret=ZOOM_CLIENT_SECRET)
#rq = client.get_name_meetings(from_date="2024-05-03", to_date="2024-05-03")
#rq = client.get_last_meeting()
#rq = client.get_meetings_by_id('85975843619')
# rq = client.get_last_meeting()
# print(rq['id'])
""" df = pd.DataFrame(rq['participants'])
print(df) """