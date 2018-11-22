#!/usr/bin/env bash
cd /app/src

mkdir -p /app/src/var/static \
         /app/src/var/conf/extra_static \
         /app/src/var/media/upload \
         /app/src/var/data \
         /app/src/var/cache \
         /app/src/var/log \
         /app/src/var/conf/extra_templates \
         /app/src/var/conf/extra_locale

# if not custom.py present, create it
if [ ! -f /app/src/var/conf/custom.py ]; then
    cp /app/src/geotrek/settings/custom.py.dist /app/src/var/conf/custom.py
fi
if [ ! -f /app/src/geotrek/settings/custom.py ]; then
    ln -s /app/src/var/conf/custom.py /app/src/geotrek/settings/custom.py
fi
# if not parsers.py present, create it
if [ ! -f /app/src/var/conf/parsers.py ]; then
    touch /app/src/var/conf/parsers.py
fi
if [ ! -f /app/src/bulkimport/parsers.py ]; then
    ln -s /app/src/var/conf/parsers.py /app/src/bulkimport/parsers.py
fi

# fix rights
chown django:django -R ./var

exec gosu django "$@"

exec "$@"