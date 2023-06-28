#!/bin/bash

validate_files(){
    renamed_file_pairs=$1
    for file_pair in $renamed_file_pairs; do
        echo "$file_pair"
        echo "--- next set --"
    done
    exit 1
}


validate_new_files(){
  created_files=$1
  for file in $created_files; do
    echo $file
    if  [[ $file == connectors* ]] && [[ $file != *.json ]] ;
    then
      echo "ERROR: new file name: $file ... should not contain space(s)"
      exit 1
    fi
  done
}



create_update_connector () {

    IFS=',' read -r -a array <<< "$file_pair" 
        echo "0 th element ${array[0]} "
        echo "1 th element ${array[1]} "


          for file in ${{ steps.changed-files.outputs.all_old_new_renamed_files }}; do
            IFS=',' read -r -a array <<< "$file" 
            if  [[ ${array[0]}  == connectors* ]] && [[ ${array[0]}  == *.json ]] && [[ ${array[1]}  == connectors* ]] && [[ ${array[1]}  == *.json ]];
            then
              . connector_deployment.sh; delete_connector ${array[0]} ${{ vars.BASE_URL }} ${{ vars.CONNECT_REST_BASIC_AUTH_USER }} ${{ secrets.CONNECT_REST_BASIC_AUTH_PASSWORD }}
              . connector_deployment.sh; create_update_connector ${array[1]} ${{ vars.BASE_URL }} ${{ vars.CONNECT_REST_BASIC_AUTH_USER }} ${{ secrets.CONNECT_REST_BASIC_AUTH_PASSWORD }} 
            fi
          done




for file_pair in $renamed_file_pairs; do
    IFS=',' read -r -a array <<< "$file_pair"
    new_file_name=${array[1]}
    echo $new_file_name
    for word in $new_file_name; do
        if  [[ $word != connectors* ]] || [[ $word != *.json ]] ;
        then
          echo "ERROR: new file name: $new_file_name ... should not contain space(s)"
          exit 1
        fi
    done
  done


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
          