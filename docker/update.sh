#!/usr/bin/env bash

set -e

cd /opt/geotrek-admin

./manage.py migrate --noinput
./manage.py clearsessions
./manage.py compilemessages
pushd var/conf/extra_locale && ../../../manage.py compilemessages && popd
./manage.py collectstatic --clear --noinput --verbosity=0
./manage.py sync_translation_fields --noinput
./manage.py update_translation_fields
./manage.py update_geotrek_permissions
./manage.py update_post_migration_languages
rm -rf var/tmp/*
