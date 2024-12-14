# Store Procedure para la limpieza de datos.

import pandas as pd
import re

def clean_participant_name(name):
    """ Limpiar el nombre de los participantes reemplazando comas y puntos y comas. """
    return re.sub(r"[;,]", " ", name) if name else None

def transform_meeting_data(meetings_data):
    transformed_data = []

    for meeting_data in meetings_data:
        meeting = meeting_data['meeting']
        participants = meeting_data['participants']

        # Limpiar el nombre de la reunión
        topic = re.sub(r"[;,]", " ", meeting.get('topic', 'Sin título'))

        # Crear DataFrame de participantes
        df = pd.DataFrame(participants)
        df['meeting_name'] = topic

        # Limpiar nombres de los participantes
        if 'name' in df.columns:
            df['name'] = df['name'].apply(clean_participant_name)

        # Normalizar nombres para evitar errores
        cleaned_topic = re.sub(r"[:/\\|<>?*]", "_", topic)
        #cleaned_uuid = re.sub(r"[/:\\|<>?*]", "_", meeting['uuid'])
        nombre_fecha = (pd.to_datetime(df['join_time']) - pd.Timedelta(hours=5)).dt.strftime('%d-%m-%Y').iloc[0]

        # Generar nombre de archivo y agregar los datos transformados
        csv_filename = f'Reuniones_DataGrowth/{cleaned_topic}.{nombre_fecha}.csv'

        transformed_data.append({
            'filename': csv_filename,
            'dataframe': df
        })

    return transformed_data

def export_csv(transformed_data):
    for meeting in transformed_data:
        # Guardar en CSV
        meeting['dataframe'].to_csv(meeting['filename'], index=False, encoding='utf-8')
        print(f"Datos exportados a: {meeting['filename']}")
