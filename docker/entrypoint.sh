#!/usr/bin/env bash
cd /app/src

. /app/venv/bin/activate

mkdir -p /app/src/var/static \
         /app/src/var/extra_static \
         /app/src/var/media/upload \
         /app/src/var/data \
         /app/src/var/cache \
         /app/src/var/log \
         /app/src/var/extra_templates \
         /app/src/var/extra_locale

# if not custom.py present, create it
if [ ! -f /app/src/var/custom.py ]; then
    cp /app/src/geotrek/settings/custom.py /app/src/var/custom.py
fi

# fix rights
chown django:django -R ./var

exec gosu django "$@"

exec "$@"