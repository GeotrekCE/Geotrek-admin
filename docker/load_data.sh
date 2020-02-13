#!/usr/bin/env bash

cd /opt/geotrek-admin

./manage.py loaddata minimal
./manage.py loaddata cirkwi
./manage.py loaddata basic

# copy media files for fixtures
for dir in `find geotrek/ -type d -name upload`; do pushd `dirname $$dir` > /dev/null; cp -R $dir/* /opt/geotrek-admin/var/media/upload/ ; popd > /dev/null; done