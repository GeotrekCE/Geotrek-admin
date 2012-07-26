#!/usr/bin/env bash

#
#  Install system dependencies
#.............................

dev=false

usage () {
    cat <<- _EOF_
Usage: Install project [OPTIONS]
    -d, --dev    install dev tools
    -h, --help    show this help
_EOF_
    return
}

database_exists () {
    # /!\ Will return false if psql can't list database. Edit your pg_hba.conf
    # as appropriate.
    if [ -z $1 ]
    then
        # Argument is null
        return 0
    else
        # Grep db name in the list of database
        psql -tAl | grep -q "^$1|"
        return $?
    fi
}

while [[ -n $1 ]]; do
    case $1 in
        -d | --dev )        dev=true
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

function ubuntu_precise {
    set -x

    sudo apt-get install python-software-properties
    sudo apt-add-repository -y ppa:ubuntugis/ubuntugis-unstable
    sudo apt-add-repository -y ppa:sharpie/postgis-stable 
    sudo apt-get update > /dev/null
    sudo apt-get install python-virtualenv build-essential python-dev unzip
    sudo apt-get install libjson0 libgdal1 libgdal-dev libproj0 libgeos-c1 postgresql postgresql-client postgresql-9.1-postgis2 postgresql-server-dev-9.1
    sudo apt-get install gettext

    # Default settings if not any
    mkdir -p etc/
    settingsfile=etc/settings.ini
    if [ ! -f $settingsfile ]; then
        cat > $settingsfile << _EOF_
#
#  Caminae Settings
#..........................
# (Note: If you edit this file out of install process, 
#  run "make deploy" to apply changes, or "make serve" in development)

[settings]
dbname = caminae
dbuser = postgres
dbpassword = postgres
dbhost = localhost
dbport = 5432

# URL prefix, leave empty if dedicated server. (example: /ecrins)
rooturl = 
# Cache duration in seconds
cachetimeout = 60 * 60

# Default structure for newly created users
defaultstructure = PNE
# EPSG code of the coordinate system to use
srid = 2154
# (minx, miny, maxx, maxy) expressed in the coordinate system above
spatial_extent = (898000, 6360000, 1013000, 6476000)
_EOF_
    fi
    # Prompt user to edit/review settings
    editor $settingsfile

    # Activate PostGIS in database
    dbname=$(sed -n 's/.*dbname *= *\([^ ]*.*\)/\1/p' < $settingsfile)
    if ! database_exists ${dbname}
    then
        sudo -n -u postgres -s -- psql -c "CREATE DATABASE ${dbname};"
        sudo -n -u postgres -s -- psql -d ${dbname} -c "CREATE EXTENSION postgis;"
    fi

    if $dev ; then
        mkdir -p lib/
        cd lib/

        wget http://phantomjs.googlecode.com/files/phantomjs-1.6.0-linux-x86_64-dynamic.tar.bz2 -O phantomjs.tar.bz2
        tar -jxvf phantomjs.tar.bz2
        rm phantomjs.tar.bz2
        cd *phantomjs*
        sudo ln -sf `pwd`/bin/phantomjs /usr/local/bin/phantomjs
        cd ..

        wget https://github.com/n1k0/casperjs/zipball/0.6.10 -O casperjs.zip
        unzip -o casperjs.zip > /dev/null
        rm casperjs.zip
        cd *casperjs*
        sudo ln -sf `pwd`/bin/casperjs /usr/local/bin/casperjs
        cd ..

        cd ..

        # A postgis template is required for django tests
        if ! database_exists template_postgis
        then
            sudo -n -u postgres -s -- createdb template_postgis
            sudo -n -u postgres -s -- psql -d template_postgis -c "CREATE EXTENSION postgis"
            sudo -n -u postgres -s -- psql -d template_postgis -c "VACUUM FREEZE"
            sudo -n -u postgres -s -- psql -c "UPDATE pg_database SET datistemplate = TRUE WHERE datname = 'template_postgis'"
            sudo -n -u postgres -s -- psql -c "UPDATE pg_database SET datallowconn = FALSE WHERE datname = 'template_postgis'"
        fi

    else
        sudo apt-get install nginx

        make deploy

        sudo rm /etc/nginx/sites-enabled/default
        sudo ln -sf etc/nginx.conf /etc/nginx/sites-enabled/default
        sudo /etc/init.d/nginx restart
    fi

    set +x

    echo "Done."
}


printf "Target operating system [precise]: "
while read options; do
  case "$options" in
    "")         ubuntu_precise
                exit
                ;;
    precise)    ubuntu_precise
                exit
                ;;
    *) printf "Incorrect value option!\nPlease enter the correct value: " ;;
  esac
done
