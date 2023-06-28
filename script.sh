#!/bin/sh
create_update_connector () {
   echo "create update function $1 $2 "
} 

delete_connector () {
    file=$1
    BASE_URL=$2
    CONNECT_REST_BASIC_AUTH_USER=$3
    CONNECT_REST_BASIC_AUTH_PASSWORD=$4
    echo '$1 $2 $3 $4'
} 



          