#!/usr/bin/env bash

echo "$DOCKER_PASSWORD" | docker login --username "$DOCKER_LOGIN" --password-stdin

docker tag geotrekce/admin:latest geotrekce/admin:$GEOTREK_VERSION;
docker push geotrekce/admin:$GEOTREK_VERSION;

if [[ $GEOTREK_VERSION != *.dev* ]];
then
     docker push geotrekce/admin:latest;
fi