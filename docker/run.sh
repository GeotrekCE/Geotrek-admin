#!/usr/bin/env bash

cd /app

./manage.py migrate --noinput
./manage.py compilemessages
./manage.py collectstatic --clear --noinput --verbosity=0
./manage.py sync_translation_fields --noinput
./manage.py update_translation_fields
./manage.py update_geotrek_permissions
./manage.py compilemessages
./venv/bin/gunicorn geotrek.wsgi:application --bind 0.0.0.0:8000