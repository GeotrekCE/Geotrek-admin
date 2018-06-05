#!/usr/bin/env bash

export GEOTREK_VERSION=$(docker-compose run web cat VERSION | tr -d '\r')
echo $GEOTREK_VERSION
source .env

sudo systemctl stop geotrek

export PGPASSWORD=$(echo $POSTGRES_PASSWORD)
docker-compose run web bash -c "PGPASSWORD=$POSTGRES_PASSWORD pg_dump -Fc --no-acl --no-owner -h postgres -w -U $POSTGRES_USER $POSTGRES_DB > /app/src/var/geotrek_$GEOTREK_VERSION.dump"

docker tag geotrekce/admin:latest geotrekce/admin:$GEOTREK_VERSION

if docker-compose run web update.sh; then
# Restore
    docker rmi geotrekce/admin:latest
else
    docker tag geotrekce/admin:$GEOTREK_VERSION geotrekce/admin:latest
    docker pull geotrekce/admin:$GEOTREK_VERSION
fi
docker-compose run web bash -c "PGPASSWORD=$POSTGRES_PASSWORD pg_restore -Fc --no-owner -h postgres -w -U $POSTGRES_USER --dbname=$POSTGRES_DB /app/src/var/geotrek_$GEOTREK_VERSION.dump"

sudo systemctl start geotrek