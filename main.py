#-------------------------------------------------------------------------------
# Name:         main
# Purpose:      Script que obtiene información desde una base de datos postgres, alojada en Sernatur
#               La información a obtener, está configurada en el archivo "config.json"
#               El script se encarga de leer la configuración, generar consultas SQL dinámicamente y obtener la data
#               La información obtenida, es formateada y cargada en capas de arcgis online
#               
#
# Author:       Fredys Barrera Artiaga <fbarrera@esri.cl>
# Created:      04-08-2020
# Copyright:    (c) fbarrera 2020
# Licence:      <your licence>
#-------------------------------------------------------------------------------

# Set the ArcGIS Desktop Basic product by importing the arcview module.
import utils
import constants as const
import requests
import xml.etree.ElementTree as et
import urllib.request as ur
import traceback
import os
import time
import json
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor


def main():
    """Main function."""

    timeStart = time.time()
    print("Proceso iniciado... {0}".format(str(datetime.now())))
    utils.log("Proceso iniciado")

    conexion = utils.getConexion()

    data = get_querys()
    utils.log("Obteniendo querys")


    print("Obteniendo token... ")
    token = utils.get_token()

    if len(data) > 0:
        for k in data:
            active = k['active']
            cantidad_paginas = get_cantidad_paginas(conexion, k['table'])
            clear_table(k['table'], cantidad_paginas, token)
            if active:
                utils.log("Insertando en tabla: {}".format(k['table']))
                for num in range(0, cantidad_paginas):
                    print('Actualizando {0}, pagina {1} de {2}'.format(
                        k['table'], str(num), str(cantidad_paginas)))
                    query = k['query'] + str(1000*num) + \
                        " ROWS FETCH NEXT " + \
                        str(1000) + " ROWS ONLY"
                    # query = k['query'] + "limit 10"
                    cursor = execute_querys(conexion, query)
                    insert_data = format_data(cursor, k['fields'])
                    # print('insert_data: ', insert_data)
                    insert_service(insert_data, k['table'], token)


    timeEnd = time.time()
    timeElapsed = timeEnd - timeStart
    print("Proceso finalizado... {0}".format(str(datetime.now())))
    print("Tiempo de ejecución: {0}".format(str(utils.convert_seconds(timeElapsed))))
    utils.log("Tiempo de ejecución: {0}".format(
        str(utils.convert_seconds(timeElapsed))))
    utils.log("Proceso finalizado\n")


    conexion.close()


def clear_table(table, cantidad_paginas, token):
    """Permite eliminar la data existente de una tabla."""

    try:
        print('Limpiando tabla {0}'.format(table))
        utils.log("Limpiando tabla {0}".format(table))

        url = const.URL_BASE + table + '/FeatureServer/0/query'
        params = {
            'f': 'json',
            'token': token,
            'where': '1=1',
            'outFields': '*',
            'returnCountOnly': 'true'
        }
        params_2 = {
            'f': 'json',
            'token': token,
            'where': '1=1',
            'outFields': '*'
        }

        response = requests.get(
            url, params=params, headers=utils.get_headers())
        response_json = json.loads(response.text)
        cantidad_registros = response_json['count']
        print('cantidad_registros: ', cantidad_registros)
        if cantidad_registros > 0:
            cantidad_paginas = get_cantidad_por_pagina(cantidad_registros, 1000)
            print('cantidad_paginas: ', cantidad_paginas)
            for num in range(0, cantidad_paginas):
                response = requests.get(
                    url, params=params_2, headers=utils.get_headers())
                response_json = json.loads(response.text)
                arr_ids_eliminar = []
                for registro in response_json['features']:
                    arr_ids_eliminar.append(registro['attributes']['ObjectId'])
                datosPeticion = {
                    'deletes': arr_ids_eliminar,
                    'f': 'json',
                    'token': token
                }
                url_apply = const.URL_BASE + table + '/FeatureServer/0/applyEdits'
                response = requests.post(
                    url_apply, data=datosPeticion, headers=utils.get_headers())
                print('Eliminando data tabla {0}, {1} de {2}: '.format(
                      table, num, cantidad_paginas))

    except:
        print("Failed clear_table (%s)" %
            traceback.format_exc())
        utils.error_log("Failed clear_table (%s)" %
            traceback.format_exc())

def insert_service(data, table, token):
    """Realizada el insert de los datos de la tabla en el servicio rest."""

    try:
        if len(data) > 0:
            url = const.URL_BASE + table + '/FeatureServer/0/addFeatures'
            # utils.log("Insertando regitros en {0}".format(url))
            # print('insert_service: ', url)
            # print('json.dumps(data): ', len(data))
            response = utils.post_request_add(
                url, token, json.dumps(data))
            print('response: ', response)

    except:
        print("Failed insert_service (%s)" %
            traceback.format_exc())
        utils.error_log("Failed insert_service (%s)" %
            traceback.format_exc())

def get_cantidad_paginas(conexion, table):
    """Retorna la cantidad de paginas para una tabla determinada."""
    
    try:
        query = "SELECT COUNT(1) AS cantidad_registros FROM {0}".format(table)
        cursor = execute_querys(conexion, query)
        for row in cursor.fetchall():
            cantidad = row['cantidad_registros']
        datos_pagina = 1000
        cantidad_paginas = get_cantidad_por_pagina(
            cantidad, datos_pagina)
        return cantidad_paginas

    except:
        print("Failed get_cantidad_paginas (%s)" %
            traceback.format_exc())
        utils.error_log("Failed get_cantidad_paginas (%s)" %
            traceback.format_exc())

def get_cantidad_por_pagina(cantidad, datos_pagina):
    try:
        page = divmod(cantidad, datos_pagina)
        cantidad_paginas = page[0]
        if page[0] == 0:
            cantidad_paginas = 1
        if page[1] != 0:
            cantidad_paginas = cantidad_paginas + 1
        return cantidad_paginas

    except:
        print("Failed get_cantidad_por_pagina (%s)" %
            traceback.format_exc())
        utils.error_log("Failed get_cantidad_por_pagina (%s)" %
            traceback.format_exc())

def get_querys():
    """Permite generar consultas SQL diámicas desde un archivo .json de configuración."""

    try:
        query = ""
        order = ""
        # limit = "limit 2000"
        limit = ""
        fields = []
        fields_table = []
        data_querys = []
        with open('config.json') as json_file:
            data = json.load(json_file)
            for p in data['tables']:
                query = ""
                joins = ""
                fields = []
                fields_table = []
                table = p['table']
                active = p['active']
                # order = "order by {}.id".format(table)
                order = "order by ID OFFSET"
                if "attributes" in p:
                    for a in p['attributes']:
                        attr = "{0}.{1}".format(table, a)
                        fields.append(attr)
                        fields_table.append(a)
                if "relations" in p:
                    for k in p['relations']:
                        table_relationship = k['table']
                        table_relationship_aux = k['table']
                        if ' as ' in table_relationship:
                            x = table_relationship.split()
                            table_relationship = "{0} {1}".format(x[0], x[2])
                            table_relationship_aux = x[2]
                        type_relationship = k['type']
                        field_from = k['field_from']
                        field_to = k['field_to']
                        joins += "{0} {1} on {2}.{3} = {4}.{5} ".format(
                            type_relationship, table_relationship, table, field_from, table_relationship_aux, field_to)
                        if "fields" in k:
                            for f in k['fields']:
                                attr = "{0}.{1} as {0}_{1}".format(
                                    table_relationship_aux, f)
                                fields.append(attr)
                                as_str = "{0}_{1}".format(
                                    table_relationship_aux, f)
                                fields_table.append(as_str)
                str_fields = ', '.join(fields)
                query += "select {0} from {1} {2} {3} {4}".format(
                    str_fields, table, joins, order, limit)
                data_querys.append(
                    {'table': table, 'query': query, 'fields': fields_table, 'active': active})
        return data_querys

    except:
        print("Failed get_querys (%s)" %
            traceback.format_exc())
        utils.error_log("Failed get_querys (%s)" %
            traceback.format_exc())


def execute_querys(conexion, query):
    """Permite ejecutar consultas SQL, en la base de datos de sernatur."""

    try:
        cursorSQL = conexion.cursor(cursor_factory=RealDictCursor)
        cursorSQL.execute(query)
        return cursorSQL
    
    except:
        print("Failed execute_querys (%s)" %
            traceback.format_exc())
        utils.error_log("Failed execute_querys (%s)" %
            traceback.format_exc())
    
def format_data(cursor, fields):
    """Formatea la data obtenida desde la consulta SQL dinámica."""
    try:
        data = []
        attributes = {}
        for row in cursor.fetchall():
            attributes = {}
            for field in fields:
                key = "{0}".format(field)
                value = row[field]
                attributes[key] = str(value)
            data.append({
                'attributes': attributes
            })
        return data

    except:
        print("Failed format_data (%s)" %
            traceback.format_exc())
        utils.error_log("Failed format_data (%s)" %
            traceback.format_exc())


if __name__ == '__main__':
    main()
