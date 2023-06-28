#!/bin/bash

validate_files(){
    echo " new files: $1"
    echo " renamed file pair: $2"
    exit 1
}

create_update_connector () {
   echo "create update function $1 $2 "
} 

test(){
    echo "$1 $2"
    if [ $1 == 3 ]
    then
        echo "t"
    else
        exit 1
    fi    
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
        echo "$(cat response.txt)"
        exit 1
    fi          
} 
          