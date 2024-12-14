# Orquestar todas las funciones.

from extract import extract_meetings
from transform import transform_meeting_data, export_csv
from load import insert_participants_into_mysql
import os

def main():
    #Crear carpeta para guardar todos los csv
    base_dir = 'Reuniones_DataGrowth'
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # Extraer los datos
    meetings_data = extract_meetings()

    if not meetings_data:
        print("No hay datos para procesar.")
        return

    # Transformar los datos
    transformed_data = transform_meeting_data(meetings_data)
    export_csv(transformed_data)

    # Cargar los datos directamente en MySQL
    insert_participants_into_mysql(meetings_data)

if __name__ == "__main__":
    main()
