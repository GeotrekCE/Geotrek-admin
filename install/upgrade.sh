#!/usr/bin/env bash

export GEOTREK_VERSION=$(docker-compose run web cat VERSION | tr -d '\r')
echo $GEOTREK_VERSION
source .env

echo "stopping geotrek service"
sudo systemctl stop geotrek

echo "backup your database"
export PGPASSWORD=$(echo $POSTGRES_PASSWORD)
sudo docker-compose run web bash -c "PGPASSWORD=$POSTGRES_PASSWORD pg_dump -Fc --no-acl --no-owner -h postgres -w -U $POSTGRES_USER $POSTGRES_DB > /app/src/var/geotrek_$GEOTREK_VERSION.dump"

echo "pulling new geotrek docker image"
sudo docker pull geotrekce/admin:latest
sudo docker tag geotrekce/admin:latest geotrekce/admin:$GEOTREK_VERSION

if ! docker-compose run web update.sh; then
    echo "an error occured. try to restore old configuration and version"
    sudo docker rmi geotrekce/admin:latest
    sudo docker tag geotrekce/admin:$GEOTREK_VERSION geotrekce/admin:latest
    sudo docker-compose run web bash -c "PGPASSWORD=$POSTGRES_PASSWORD pg_restore -c -Fc --no-owner -h postgres -w -U $POSTGRES_USER --dbname=$POSTGRES_DB /app/src/var/geotrek_$GEOTREK_VERSION.dump"
    echo "restore is ok. Please run docker-compose run web update.sh in order to make available again"
fi

sudo systemctl start geotrek