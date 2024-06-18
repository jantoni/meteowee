#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Creado por José A. García-Tenorio en Mayo de 2024. Con la inestimable ayuda de la IA de Google Gemini

# Este Script envía los datos de tu estación a Meteoclimatic.
# Para ello necesitas definir 3 variables
# station_code define el código de estación de Meteoclimatic. Es preferible que indiques el nuevo código, aunque es compatible con el antiguo código de Meteoclimatic
# api_key define el ID API (o API Key) del usuario, no de la estación. Lo puedes encontrar en la sección "Perfil" de Meteoclimatic una vez identificado
# datafile define el fichero donde este script debe encontrar los datos a enviar a Meteoclimatic. Debes indicar la ruta y el nombre del fichero


# Variables a definir
api_key = "TU-ID-API-DE-METEOCLIMATIC"
station_code = "CODIGO DE ESTACION"
datafile = "/PATH/FICHERO DE LA PLANTILLA DE METEOCLIMATIC"


import requests
import json

datos={"stationCode":station_code,"rawData2":open(datafile, "r").read()}

# Cabeceras del Post
cabeceras = {"APIkey": api_key}

# Envia la petición POST
url = "https://api.meteoclimatic.com/v2/api.json/station/weather"
response = requests.post(url, headers=cabeceras, data=datos, timeout=5)

# Imprime la respuesta. Solo para test
#print(response.text)

# Comprueba que se haya aceptado (code 200)
if response.status_code == 200:
    # Convierte la respuesta JSON
    response_data = json.loads(response.text)

    # Print response data, only for tests
    #print(response_data)

    # Comprueba errores en la respuesta
    if "fault" in response_data:
        fault_code = response_data["fault"]["code"]
        fault_status = response_data["fault"]["status"]
        print(f"{fault_code} - {fault_status}")
else:
    print("Error:", response.status_code)

