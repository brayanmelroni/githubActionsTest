#!/bin/sh
create_update_connector () {
   echo "create update function $1 $2 "
} 

delete_connector () {
    echo "delete connector function $1"
    file=$1
    BASE_URL=$2
    CONNECT_REST_BASIC_AUTH_USER=$3
    CONNECT_REST_BASIC_AUTH_PASSWORD=$4
    echo "$file"
    echo "$BASE_URL"
    echo "$CONNECT_REST_BASIC_AUTH_USER"
    echo "$CONNECT_REST_BASIC_AUTH_PASSWORD"
   
} 



          