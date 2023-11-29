#!/usr/bin/env bash

set -e

cd /opt/geotrek-admin

./manage.py loaddata minimal
./manage.py loaddata cirkwi
./manage.py loaddata basic
./manage.py loaddata licenses
./manage.py loaddata circulations

# copy media files for fixtures
for dir in `find geotrek/ -type d -name upload`; do pushd `dirname $$dir` > /dev/null && cp -R $dir/* /opt/geotrek-admin/var/media/upload/ && popd > /dev/null; done
