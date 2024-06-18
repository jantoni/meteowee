#!/bin/bash

# Creado por Jose A. García-Tenorio en Mayo de 2024


# Debes indicar 3 datos.
# METEOCLIMATIC_COD define el código de estación de Meteoclimatic. Es preferible que indiques el nuevo código, aunque es compatible con el antiguo código de Meteoclimatic
# METEOCLIMATIC_KEY define el ID API (o API Key) del usuario, no de la estación. Lo puedes encontrar en la sección "Perfil" de Meteoclimatic una vez identificado
# METEOCLIMATIC_FILE define el fichero donde este script debe encontrar los datos a enviar a Meteoclimatic. Debes indicar la ruta y el nombre del fichero


# VARIABLES A DEFINIR
METEOCLIMATIC_COD="NUMERO DE ESTACION"
METEOCLIMATIC_KEY="TU-API-KEY-DE-METEOCLIMATIC"
METEOCLIMATIC_FILE="/PATH/FICHERO DE LA PLANTILLA DE METEOCLIMATIC"


# Invoca a curl con una petición POST pasando la cabecera indicada por -H y los datos en --data-urlencode
METEOCLIMATIC_URL="https://api.meteoclimatic.com/v2/api.json/station/weather"
curl --data-urlencode "stationCode=$METEOCLIMATIC_COD" \
     --data-urlencode "rawData2@$METEOCLIMATIC_FILE" \
      -H "APIkey: $METEOCLIMATIC_KEY" \
      -X POST $METEOCLIMATIC_URL



# Aquí habría que definir alguna instrucción para detectar errores. Mañana