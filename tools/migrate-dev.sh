#!/bin/bash

# This script is used to migrate Geotrek-admin
# from versions <= 2.32 to superior, installed
# via apt, for dev installations

set -e

# Disclaimer

echo "WARNING! You run this script at your own risk."
echo "You should backup your database before."
read -p "Are you sure to continue (y/n)? " -n 1 -r < /dev/tty
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo
    echo "Abort"
    exit 1
fi
echo

# Disable old conf
sudo rm -f /etc/nginx/sites-enabled/geotrek
sudo rm -f /etc/nginx/sites-available/geotrek
sudo rm -f /etc/supervisor/conf.d/supervisor-convertit.conf
sudo rm -f /etc/supervisor/conf.d/supervisor-geotrek-api.conf
sudo rm -f /etc/supervisor/conf.d/supervisor-geotrek-celery.conf
sudo rm -f /etc/supervisor/conf.d/supervisor-geotrek.conf
sudo rm -f /etc/supervisor/conf.d/supervisor-screamshotter.conf

# Stop services
sudo supervisorctl reload

# Copy media
sudo mkdir -p /opt/geotrek-admin/var/media
sudo cp -r --preserve=mode,timestamp var/media/* /opt/geotrek-admin/var/media/

# Copy conf
sudo mkdir -p /opt/geotrek-admin/var/conf/extra_locale /opt/geotrek-admin/var/conf/extra_templates
if [ -f geotrek/settings/custom.py ] ; then
	sudo cp geotrek/settings/custom.py /opt/geotrek-admin/var/conf/
	sudo sed -i 's/^from \.prod import \*$/# from .prod import */' /opt/geotrek-admin/var/conf/custom.py
fi
[ -f bulkimport/parsers.py ] && sudo cp bulkimport/parsers.py /opt/geotrek-admin/var/conf/
[ -d geotrek/locale ] && sudo cp -r geotrek/locale/* /opt/geotrek-admin/var/conf/extra_locale/
[ -d var/media/templates ] && sudo cp -r var/media/templates/* /opt/geotrek-admin/var/conf/extra_templates/

# Set debconf values
cat << EOF | sudo debconf-set-selections
geotrek-admin geotrek-admin/MANAGE_DB boolean false
geotrek-admin geotrek-admin/POSTGRES_HOST string `./bin/django shell -c "from django.conf import settings; print(settings.DATABASES['default']['HOST'])"`
geotrek-admin geotrek-admin/POSTGRES_PORT string `./bin/django shell -c "from django.conf import settings; print(settings.DATABASES['default']['PORT'])"`
geotrek-admin geotrek-admin/POSTGRES_USER string `./bin/django shell -c "from django.conf import settings; print(settings.DATABASES['default']['USER'])"`
geotrek-admin geotrek-admin/POSTGRES_PASSWORD password `./bin/django shell -c "from django.conf import settings; print(settings.DATABASES['default']['PASSWORD'])"`
geotrek-admin geotrek-admin/POSTGRES_DB string `./bin/django shell -c "from django.conf import settings; print(settings.DATABASES['default']['NAME'])"`
geotrek-admin geotrek-admin/SERVER_NAME string `./bin/django shell -c "from django.conf import settings; print(' '.join(['_' if h == '*' else h for h in settings.ALLOWED_HOSTS]))"`
geotrek-admin geotrek-admin/RANDO_SERVER_NAME string `./bin/django shell -c "from geotrek.settings import EnvIniReader; print(EnvIniReader('etc/settings.ini').get('cors', '*'))"`
geotrek-admin geotrek-admin/DEFAULT_STRUCTURE string `./bin/django shell -c "from django.conf import settings; print(settings.DEFAULT_STRUCTURE_NAME)"`
geotrek-admin geotrek-admin/LANGUAGES string `./bin/django shell -c "from django.conf import settings; l = settings.MODELTRANSLATION_LANGUAGES[:]; l.remove(settings.MODELTRANSLATION_DEFAULT_LANGUAGE); l.insert(0, settings.MODELTRANSLATION_DEFAULT_LANGUAGE); print(' '.join(l))"`
geotrek-admin geotrek-admin/SRID string `./bin/django shell -c "from django.conf import settings; print(settings.SRID)"`
geotrek-admin geotrek-admin/TIME_ZONE string `./bin/django shell -c "from django.conf import settings; print(settings.TIME_ZONE)"`
EOF

# Install deb package
if [ "`./bin/django shell -c "from django.conf import settings; print(settings.DATABASES['default']['HOST'])"`" == "localhost" ]; then
	curl https://packages.geotrek.fr/install-dev.sh | bash
else
	curl https://packages.geotrek.fr/install-dev.sh | bash -s - --nodb
fi
