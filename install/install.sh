#!/usr/bin/env bash

if [ "$(id -u)" == "0" ]; then
   echo -e "\e[91m\e[1mThis script should NOT be run as root\e[0m" >&2
fi

cd "$(dirname "$0")"

#------------------------------------------------------------------------------

STABLE_VERSION=${STABLE_VERSION:-2.19.0}
interactive=true

usage () {
    cat >&2 <<- _EOF_
Usage: $0 project [OPTIONS]
    --noinput         do not prompt user
    -h, --help        show this help
_EOF_
    return
}

while [[ -n $1 ]]; do
    case $1 in
        --noinput )         interactive=false
                            ;;
        -h | --help )       usage
                            exit
                            ;;
        *)                  usage
                            exit
                            ;;
    esac
    shift
done

#------------------------------------------------------------------------------



#------------------------------------------------------------------------------
#
#  Helpers
#
#------------------------------------------------------------------------------

function echo_step () {
    set +x
    exec 2>&4
    echo -e "\n\e[92m\e[1m$1\e[0m" >&2
    exec 2>&1
    set -x
}


function echo_warn () {
    set +x
    exec 2>&4
    echo -e "\e[93m\e[1m$1\e[0m" >&2
    exec 2>&1
    set -x
}


function echo_error () {
    set +x
    exec 2>&4
    echo -e "\e[91m\e[1m$1\e[0m" >&2
    exec 2>&1
    set -x
}


function echo_progress () {
    set +x
    exec 2>&4
    echo -e ".\c" >&2
    exec 2>&1
    set -x
}

function exit_error () {
    code=$1
    shift
    echo_error "$@"
    echo "(More details in install.log)" >&2
    exit $code
}

function install_docker () {
    if [ $trusty -eq 1 ]; then
        sudo apt-get update linux-image-extra-$(uname -r) linux-image-extra-virtual
    fi
    sudo apt-get remove docker docker-engine docker.io
    sudo apt-get install apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo apt-key fingerprint 0EBFCD88
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    sudo apt-get update
    sudo apt-get install docker-ce
}

function geotrek_setup () {
    echo "1----"
    if [ $trusty -eq 1 -o $xenial -eq 1 -o $bionic -eq 1 ]; then
        install_docker
        sudo curl -L https://github.com/docker/compose/releases/download/1.21.2/docker-compose-$(uname -s)-$(uname -m) \
        -o /usr/local/bin/docker-compose
    else
        exit_error 5 "Unsupported operating system for Docker. Install Docker manually (ReadMe.md)"
    fi
    echo "2----"
    cd ..
    echo "Choose your instance of geotrek"
    read path_instance
    mv install $path_instance
    sudo chown -R $USER:$USER $path_instance
    cd $path_instance
    cp ./install/.env.dist .env
    nano .env
    source ../.env
    if [$POSTGRES_HOST]; then
        sed -e '3,9d;82,83d' < ./install/docker-compose.yml
    fi
    nano ./var/conf/custom.py
    # while pour verifier que les 4 sont modifiés (SRID, SPATIAL_EXTEN) ...
    docker-compose run postgres -d
    docker-compose run web initial.sh
    cp custom.py.dist ./var/conf/custom.py
    docker-compose run web ./manage.py createsuperuser
    sudo cp geotrek.service /etc/systemd/system/geotrek.service
    sudo systemctl enable geotrek
}


trusty=$(grep "Ubuntu 14.04" /etc/issue | wc -l)
xenial=$(grep "Ubuntu 16.04" /etc/issue | wc -l)
bionic=$(grep "Ubuntu 18.04" /etc/issue | wc -l)

geotrek_setup