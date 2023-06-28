#!/bin/sh
create_update_connector () {
   echo "create update function $1 $2 "
} 

delete_connector () {
    file=$1
    BASE_URL=$2
    CONNECT_REST_BASIC_AUTH_USER=$3
    CONNECT_REST_BASIC_AUTH_PASSWORD=$4
    CONNECTOR_NAME=`echo $file | rev |  cut -d/ -f1 | rev | cut -d. -f1`
    DELETE_URL=`echo ${BASE_URL}/connectors/${CONNECTOR_NAME}`
    response=$(curl --write-out '%{http_code}' --silent --output response.txt -u ${CONNECT_REST_BASIC_AUTH_USER}:${CONNECT_REST_BASIC_AUTH_PASSWORD} -s -X DELETE $DELETE_URL)
    if [ $response == 204 ]
    then
        echo "Deleted: $CONNECTOR_NAME"
    else
        cat response.txt
    fi          
} 
          