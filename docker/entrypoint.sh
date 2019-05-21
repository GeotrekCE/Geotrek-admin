#!/usr/bin/env bash
cd /app/src

mkdir -p /app/src/var/static \
         /app/src/var/conf/extra_static \
         /app/src/var/media/upload \
         /app/src/var/data \
         /app/src/var/cache \
         /app/src/var/log \
         /app/src/var/conf/extra_templates \
         /app/src/var/conf/extra_locale \
         /app/src/var/tmp

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

# wait for postgres
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -p "$PGPORT" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

# exec
exec gosu django "$@"
