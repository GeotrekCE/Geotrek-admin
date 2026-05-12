#!/bin/bash

# This script is used to install Geotrek-admin >= 2.33

set -e

if lsb_release -d | grep 'Ubuntu 24.04' || lsb_release -d | grep 'Ubuntu 22.04' > /dev/null; then
	echo "Either, Ubuntu 24.04, 22.04 found"
else
	echo "ERROR! Neither Ubuntu 24.04, Ubuntu 22.04 found."
	exit 1
fi

if [ "$(locale charmap)" != "UTF-8" ]; then
	echo "ERROR! Your user locale charmap is not UTF-8"
	exit 1
fi

if ! `localectl status | grep -q "System Locale: LANG=.*UTF-8"`; then
	echo "ERROR! Your system locale charmap is not UTF-8"
	exit 1
fi

if [ "$NODB" == "true" ]; then
	postgis_and_routing=""
else
	postgis_and_routing="postgresql-pgrouting"
fi

sudo apt update
sudo apt install -y $postgis_and_routing curl ca-certificates software-properties-common
sudo install -d /usr/share/geotrek
sudo curl -o /usr/share/geotrek/apt.geotrek.org.key --fail https://packages.geotrek.fr/geotrek.gpg.key
sudo rm -f /etc/apt/sources.list.d/geotrek.list
echo "deb [signed-by=/usr/share/geotrek/apt.geotrek.org.key] https://packages.geotrek.fr/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/geotrek.list
sudo apt update
sudo apt install --no-install-recommends -y postgis  # force install postgis scripts only to use loaddem command, even if script does not manage database installation
sudo apt install --no-install-recommends -y geotrek-admin