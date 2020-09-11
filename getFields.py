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
import main as _main
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
    """Get fields function."""

    try:
        conexion = utils.getConexion()
        data = _main.get_querys()
        utils.query_log("Obteniendo querys")

        if len(data) > 0:
            for k in data:
                utils.query_log("Tabla: {0}, activa: {1}, fields: {2}".format(k['table'], k['active'], k['fields']))

        conexion.close()

        utils.query_log("Fin \n")

    except:
        print("Failed main getFields (%s)" %
            traceback.format_exc())
        utils.error_log("Failed main getFields (%s)" %
            traceback.format_exc())


if __name__ == '__main__':
    main()
