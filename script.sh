#!/bin/sh
create_update_connector () {
   echo "create update function $1 $2 "
} 

delete_connector () {
    file=$1
    BASE_URL=$2
    CONNECT_REST_BASIC_AUTH_USER=$3
    CONNECT_REST_BASIC_AUTH_PASSWORD=$4
    echo '$file $BASE_URL $CONNECT_REST_BASIC_AUTH_USER $CONNECT_REST_BASIC_AUTH_PASSWORD'
} 



          