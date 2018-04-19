#!/usr/bin/env bash

if [ "$(id -u)" == "0" ]; then
   echo -e "\e[91m\e[1mThis script should NOT be run as root\e[0m" >&2
fi

cd "$(dirname "$0")"

virtualenv -p /usr/bin/python3 .
bin/pip install invoke

dev=false
tests=false
prod=false
standalone=true
interactive=true

usage () {
    cat >&2 <<- _EOF_
Usage: $0 project [OPTIONS]
    -d, --dev         minimum dependencies for development
    -t, --tests       install testing environment
    -p, --prod        deploy a production instance
    --noinput         do not prompt user
    -s, --standalone  deploy a single-server production instance (Default)
    -h, --help        show this help
_EOF_
    return
}

while [[ -n $1 ]]; do
    case $1 in
        -d | --dev )        dev=true
                            standalone=false
                            ;;
        -t | --tests )      tests=true
                            standalone=false
                            ;;
        -p | --prod )       prod=true
                            standalone=false
                            ;;
        -s | --standalone ) ;;
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

bin/python install.py $dev $tests $prod $standalone $interactive