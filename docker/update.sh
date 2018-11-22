#!/usr/bin/env bash

cd /app/src

./manage.py migrate --noinput
./manage.py compilemessages
./manage.py collectstatic --clear --noinput --verbosity=0
./manage.py sync_translation_fields --noinput
./manage.py update_translation_fields
./manage.py update_geotrek_permissions