#-------------------------------------------------------------------------------
# Name:         utils
# Purpose:      Utilidades varias
#
# Author:       Fredys Barrera Artiaga <fbarrera@esri.cl>
# Created:      04-08-2020
# Copyright:    (c) fbarrera 2020
# Licence:      <your licence>
#-------------------------------------------------------------------------------

from bs4 import BeautifulSoup
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import constants as const
import xml.etree.ElementTree as et
import urllib.request as ur
import requests
import traceback
import json
import os


#-------------------------------------------------------------------------------
# Retorna un token de acceso a los servicios
#-------------------------------------------------------------------------------
def get_token():
    try:
        payload = "client_id=" + const.CLIENT_ID + "&client_secret=" + \
            const.CLIENT_SECRET + "&grant_type=" + const.GRANT_TYPE

        response = requests.request(
            "POST", const.URL_TOKEN, data=payload, headers=get_headers())
        token = json.loads(response.text)

        return token['access_token']
    except:
        print("Failed get_token (%s), (%s)" %
              traceback.format_exc(), url_rest)

#-------------------------------------------------------------------------------
# Retorna una conexion hacia Postgres
#-------------------------------------------------------------------------------
def getConexion():
    try:
        conexion = psycopg2.connect(host=const.SERVIDOR_BD, database=const.DATABASE,
                                user=const.USUARIO_BD, password=const.PASSWORD_BD)
        return conexion
    except:
        print("Failed getConexion (%s), (%s)" %
              traceback.format_exc(), url_rest)

#-------------------------------------------------------------------------------
# Permite ejecutar una consulta de tipo POST al servicio REST
#-------------------------------------------------------------------------------
def post_request(url_rest, token, where):
    try:
        data = {
            'f': 'json',
            'token': token,
            'where': where
        }
        return requests.post(url_rest, data=data, headers=get_headers())
    except:
        print("Failed post_request (%s), (%s)" %
              traceback.format_exc(), url_rest)

#-------------------------------------------------------------------------------
# Permite insertar features al servicio REST
#-------------------------------------------------------------------------------
def post_request_add(url_rest, token, features):
    try:
        data = {
            'f': 'json',
            'token': token,
            'features': features
        }
        return requests.post(url_rest, data=data, headers=get_headers())
    except:
        print("Failed post_request (%s), (%s)" %
              traceback.format_exc(), url_rest)

#-------------------------------------------------------------------------------
# Realiza una peticion http de tipo get simple
#-------------------------------------------------------------------------------
def get_request(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(response.text)
            print(response.status_code)
            return False
    except:
        print("Failed get_request (%s)" %
            traceback.format_exc())

#-------------------------------------------------------------------------------
# Realiza una peticion http de tipo POST con raw_data en formato json
#-------------------------------------------------------------------------------
def post_request_json_raw_data(url, raw_data):
    try:
        response = requests.post(url, json=raw_data)
        if response.status_code == 200:
            data = response.json()
            return data
        return False
    except:
        print("Failed post_request_payload (%s)" %
              traceback.format_exc())

#-------------------------------------------------------------------------------
# Limpia las capas de resultados
#-------------------------------------------------------------------------------
def limpiar_capas_analisis(url_rest, table, token, where):
    try:
        url = url_rest + table + '/FeatureServer/0/deleteFeatures'
        response = post_request(url, token, where)
        return response
    except:
        print("Failed limpiar_capas_analisis (%s)" % traceback.format_exc())

#-------------------------------------------------------------------------------
# Retorna los headers para los request
#-------------------------------------------------------------------------------
def get_headers():

    return {
        'content-type': "application/x-www-form-urlencoded",
        'accept': "application/json",
        'cache-control': "no-cache",
        'postman-token': "11df29d1-17d3-c58c-565f-2ca4092ddf5f"
    }

#-------------------------------------------------------------------------------
# Convert seconds into hours, minutes and seconds
#-------------------------------------------------------------------------------
def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)
