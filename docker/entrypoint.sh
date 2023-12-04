#!/usr/bin/env bash

set -e

mkdir -p /opt/geotrek-admin/var/static \
         /opt/geotrek-admin/var/conf/extra_static \
         /opt/geotrek-admin/var/media/upload \
         /opt/geotrek-admin/var/data \
         /opt/geotrek-admin/var/cache/sessions \
         /opt/geotrek-admin/var/cache/api_v2 \
         /opt/geotrek-admin/var/cache/fat \
         /opt/geotrek-admin/var/log \
         /opt/geotrek-admin/var/conf/extra_templates \
         /opt/geotrek-admin/var/conf/extra_locale \
         /opt/geotrek-admin/var/tmp

# if not custom.py present, create it
if [ ! -f /opt/geotrek-admin/var/conf/custom.py ]; then
    cp /opt/geotrek-admin/geotrek/settings/custom.py.dist /opt/geotrek-admin/var/conf/custom.py
fi

# if not parsers.py present, create it
if [ ! -f /opt/geotrek-admin/var/conf/parsers.py ]; then
    touch /opt/geotrek-admin/var/conf/parsers.py
fi

# Activate venv
. /opt/venv/bin/activate

# Defaults POSTGRES_HOST to Docker host IP
export POSTGRES_HOST=${POSTGRES_HOST:-`ip route | grep default | sed 's/.* \([0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+\) .*/\1/'`}

# Defaults SECRET_KEY to a random value
SECRET_KEY_FILE=/opt/geotrek-admin/var/conf/secret_key
if [ -z $SECRET_KEY ]; then
    if [ ! -f $SECRET_KEY_FILE ]; then
        echo "Generate a secret key"
        dd bs=48 count=1 if=/dev/urandom 2>/dev/null | base64 > $SECRET_KEY_FILE
        chmod go-r $SECRET_KEY_FILE
    fi
    export SECRET_KEY=`cat $SECRET_KEY_FILE`
fi

# wait for postgres
until PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -p "$POSTGRES_PORT" -d "$POSTGRES_DB" -c '\q'; do
    >&2 echo "Postgres is unavailable - sleeping"
    sleep 1
done

>&2 echo "Postgres is up - executing command"

# exec
exec "$@"
