
#-------------------------------------------------------------------------------
# Name:         constants
# Purpose:      Constantes del script
#
# Author:       Fredys Barrera Artiaga <fbarrera@esri.cl>
# Created:      04-08-2020
# Copyright:    (c) fbarrera 2020
# Licence:      <your licence>
#-------------------------------------------------------------------------------

from decouple import config

# **********************************************************************************************
# Datos conexión
SERVIDOR_BD = config('DB_HOST', default='')
DATABASE = config('DB_NAME', default='')
USUARIO_BD = config('DB_USER', default='')
PASSWORD_BD = config('DB_PASSWORD', default='')
# **********************************************************************************************

# **********************************************************************************************
# Credenciales para obtener token
CLIENT_ID = config('TOKEN_CLIENT_ID')
CLIENT_SECRET = config('TOKEN_CLIENT_SECRET')
GRANT_TYPE = 'client_credentials'
URL_TOKEN = 'https://www.arcgis.com/sharing/rest/oauth2/token'
# **********************************************************************************************

# **********************************************************************************************
# URL Servicios REST

# Url Base
URL_BASE = config('URL_BASE_AGOL')

# Keys capas
