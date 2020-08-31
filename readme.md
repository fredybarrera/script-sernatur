# Script Sernatur

Proyecto desarrollado en Python 3.6

## Propósito

Script que obtiene información desde una base de datos postgres, alojada en Sernatur

La información a obtener, está configurada en el archivo "config.json"

El script se encarga de leer la configuración, generar consultas SQL dinámicamente y obtener la data

La información obtenida, es formateada y cargada en capas de arcgis online

## Instalación

Descargar el proyecto y descomprimir en una ubicación dentro del disco C:

Se recomienda la instalación dentro de un entorno virtual de [miniconda](https://docs.conda.io/en/latest/miniconda.html).

Instalar miniconda en el sistema operativo y crear un entorno virtual con Python 3.6:
```bash
conda create -n nombre_entorno python==3.8
```
Activar al entorno virtual:
```bash
activate nombre_entorno 
```
Navegar hasta la ubicación del proyecto e instalar las dependencias:

```bash
pip install -r requirements.txt
```

Crear un archivo **.env** en la raiz del proyecto, tomando como referencia el archivo **.env_example** y completar los valores correspondientes para las variables:
```bash
DB_HOST=""
DB_NAME=""
DB_USER=""
DB_PASSWORD=""

TOKEN_CLIENT_ID=""
TOKEN_CLIENT_SECRET=""
GRANT_TYPE=""

URL_BASE_AGOL=""
```

## Uso

Ejecutar el archivo **main.py**
```bash
cd C:\Miniconda3\envs\nombre_entorno\
python.exe C:\Users\user_1\script\main.py
```
