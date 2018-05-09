#!/usr/bin/env bash

/app/manage.py migrate --noinput
/app/manage.py compilemessages
/app/manage.py collectstatic --noinput
cd /app
/app/venv/bin/gunicorn geotrek.wsgi:application --bind 0.0.0.0:8000