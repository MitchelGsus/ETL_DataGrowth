##  DESCARGA Y CONFIGURACIÓN
-  Clone el repositorio.
	```sh
	git clone https://github.com/MitchelGsus/ETL_DataGrowth.git
	```
-  Vaya al directorio del proyecto.
	```sh
	cd ETL_DataGrowth
	```
-  Cree un entorno virtual.
	```sh
	 python -m venv venv
	```
-  Active el entorno virtual.
	```sh
	 venv\Scripts\activate.ps1
	```
-  Instale las dependencias del proyecto
	```sh
	 pip install -r requirements.txt
	```
-  En el archivo **.env** pegar tus credenciales según corresponda.
	```sh
	 ZOOM_ACCOUNT_ID = 'pega_tus_credenciales_aquí' 
	 ZOOM_CLIENT_ID = 'pega_tus_credenciales_aquí'
	 ZOOM_CLIENT_SECRET = 'pega_tus_credenciales_aquí'
	 
     MYSQL_HOST = 'localhost'
     MYSQL_USER = 'usuario_mysql'
     MYSQL_PASSWORD = 'contraseña_mysql'
     MYSQL_DATABASE = 'base_de_datos_mysql'
     MYSQL_PORT = 'puerto'
	```
-  Ejecutar el archivo **main.py**
    ```sh
	 python main.py
	```