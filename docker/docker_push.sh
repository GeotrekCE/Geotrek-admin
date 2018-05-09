#!/usr/bin/env bash

docker login -u "$DOCKER_LOGIN" -p "$DOCKER_PASSWORD";
if [[ $ACTION == test ]];
then
      docker push geotrekce/admin:$GEOTREK_VERSION;
fi