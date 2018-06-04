#!/usr/bin/env bash

with_version=false

usage () {
    cat >&2 <<- _EOF_
Usage: $0 project [OPTIONS]
    -v                dump the database with version name
    -h, --help        show this help
_EOF_
    return
}

while [[ -n $1 ]]; do
    case $1 in
        -v )         with_version=true
                            ;;
        -h | --help )       usage
                            exit
                            ;;
        *)                  usage
                            exit
                            ;;
    esac
    shift
done


export GEOTREK_VERSION=$(docker run web cat VERSION)
source .env

sudo systemctl stop geotrek

export PGPASSWORD=$(echo $POSTGRES_PASSWORD)
if with_version=false; then
    pg_dump -Fc --no-acl --no-owner -h 127.0.0.1 -U $POSTGRES_USER $POSTGRES_DB > geotrek_`date +\%Y-\%m-\%d_\%H:\%M`.dump
else
    pg_dump -Fc --no-acl --no-owner -h 127.0.0.1 -U $POSTGRES_USER $POSTGRES_DB > geotrek_$GEOTREK_VERSION.dump
fi
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

if with_version=true; then
    pg_restore -F --no-acl --no-owner -h 127.0.0.1 -U $POSTGRES_USER $POSTGRES_DB geotrek_`date +\%Y-\%m-\%d_\%H:\%M`.dump
else
    pg_dump -Fc --no-acl --no-owner -h 127.0.0.1 -U $POSTGRES_USER $POSTGRES_DB > geotrek_$GEOTREK_VERSION.dump
fi
sudo systemctl start geotrek