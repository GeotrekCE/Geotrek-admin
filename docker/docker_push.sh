#!/usr/bin/env bash

echo "$DOCKER_PASSWORD" | docker login --username "$DOCKER_LOGIN" --password-stdin

if [[ $ACTION == deploy ]];
then
  docker tag geotrek geotrekce/admin:$GEOTREK_VERSION;
  docker push geotrekce/admin:$GEOTREK_VERSION;

  if [[ $GEOTREK_VERSION != *.dev* ]];
    then
      docker tag geotrek geotrekce/admin:latest;
      docker push geotrekce/admin:latest;
    fi
fi

