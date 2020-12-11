#!/usr/bin/env bash

set -e

cd /opt/geotrek-admin

mkdir -p var/static \
         var/conf/extra_static \
         var/media/upload \
         var/data \
         var/cache \
         var/log \
         var/conf/extra_templates \
         var/conf/extra_locale \
         var/tmp

# if not custom.py present, create it
if [ ! -f var/conf/custom.py ]; then
    cp geotrek/settings/custom.py.dist var/conf/custom.py
fi

# if not parsers.py present, create it
if [ ! -f var/conf/parsers.py ]; then
    touch var/conf/parsers.py
fi

# When a volume is mounted to /app/src and venv are hidden
if [ "$ENV" = "dev" ]; then
    if [ ! -d env ]; then
        python3 -m venv env
        env/bin/pip install -U setuptools==45.2.0
        env/bin/pip install --no-cache-dir -r requirements.txt
    fi
fi

# Activate venv
. env/bin/activate

# Defaults POSTGRES_HOST to Docker host IP
export POSTGRES_HOST=${POSTGRES_HOST:-`ip route | grep default | sed 's/.* \([0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+\) .*/\1/'`}

# Defaults SECRET_KEY to a random value
SECRET_KEY_FILE=var/conf/secret_key
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
