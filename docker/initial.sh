#!/usr/bin/env bash

cd /app/src

/usr/local/bin/update.sh

./manage.py loaddata minimal
./manage.py loaddata cirkwi
./manage.py loaddata basic

# copy media files for fixtures
for dir in `find geotrek/ -type d -name upload`; do pushd `dirname $$dir` > /dev/null; cp -R $dir/* /app/src/var/media/upload/ ; popd > /dev/null; done