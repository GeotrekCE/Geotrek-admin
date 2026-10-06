#!/bin/bash

# This script is used to install Geotrek-admin >= 2.33

set -e

if lsb_release -d | grep 'Ubuntu 26.04' || lsb_release -d | grep 'Ubuntu 24.04' || lsb_release -d | grep 'Ubuntu 22.04' > /dev/null; then
	echo "Either, Ubuntu 26.04, 24.04, 22.04 found"
else
	echo "Warning! You install this package on untested system. Continue ? [y/n]"
  read answer
  if [ "$answer" != "${answer#[Yy]}" ] ;then
    echo "Continue installation"
  else
    echo "Installation aborted"
    exit 1
  fi
fi

if [ "$(locale charmap)" != "UTF-8" ]; then
	echo "ERROR! Your user locale charmap is not UTF-8"
	exit 1
fi

if ! `echo $LANG | grep -q ".*UTF-8"`; then
	echo "ERROR! Your system locale charmap is not UTF-8"
	exit 1
fi

if [ "$NODB" == "true" ]; then
	postgis_and_routing=""
else
	postgis_and_routing="postgresql-pgrouting"
fi

sudo apt update
sudo apt install -y $postgis_and_routing curl ca-certificates
sudo curl -o /etc/apt/sources.list.d/geotrek.sources https://raw.githubusercontent.com/GeotrekCE/Geotrek-admin/master/debian/geotrek.sources
sudo curl -o /etc/apt/keyrings/apt.geotrek.gpg --fail https://raw.githubusercontent.com/GeotrekCE/Geotrek-admin/master/debian/apt.geotrek.gpg
sudo apt update
sudo apt install --no-install-recommends -y postgis  # force install postgis scripts only to use loaddem command, even if script does not manage database installation
sudo apt install --no-install-recommends -y geotrek-admin