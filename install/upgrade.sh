#!/usr/bin/env bash

export GEOTREK_VERSION=$(docker-compose run web cat VERSION)
source .env

sudo systemctl stop geotrek

export PGPASSWORD=$(echo $POSTGRES_PASSWORD)
pg_dump -Fc --no-acl --no-owner -h 127.0.0.1 -U $POSTGRES_USER $POSTGRES_DB > geotrek_$GEOTREK_VERSION.dump
docker tag geotrekce/admin:latest geotrekce/admin:$GEOTREK_VERSION
docker pull geotrekce/admin:latest

if then
docker-compose run web update.sh
# Restore
    docker rmi geotrekce/admin:latest
else
    docker tag geotrekce/admin:$GEOTREK_VERSION geotrekce/admin:latest
    docker pull geotrekce/admin:$GEOTREK_VERSION
fi
pg_dump -Fc --no-acl --no-owner -h 127.0.0.1 -U $POSTGRES_USER $POSTGRES_DB > geotrek_$GEOTREK_VERSION.dump

sudo systemctl start geotrek