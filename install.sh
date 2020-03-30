#!/bin/bash

set -e

if lsb_release -d | grep 'Ubuntu 18.04' > /dev/null; then
	echo "Found Ubuntu 18.04"
else
	echo "ERROR ! Ubuntu 18.04 not found."
	exit 1
fi

if [ "$*" == "--nodb" ]; then
	postgis=""
elif [ -n "$*" ]; then
	echo "Usage: $0 [--nodb]"
	exit 1
else
	postgis="postgis"
fi

sudo apt update
sudo apt install -y $postgis wget software-properties-common
echo "deb https://packages.geotrek.fr/ubuntu bionic main" | sudo tee /etc/apt/sources.list.d/geotrek.list
wget -O- "https://packages.geotrek.fr/geotrek.gpg.key" | sudo apt-key add -
sudo apt update
sudo apt install -y geotrek-admin
