#!/usr/bin/env bash

cd /app

./manage.py loaddata minimal
./manage.py loaddata cirkwi
./manage.py loaddata basic
