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
    sudo apt-get install libjson0 libgdal1 libproj0 libgeos-c1 postgresql postgresql-client postgresql-9.1-postgis2 postgresql-server-dev-9.1
    
    # Default settings if not any
    mkdir -p etc/
    settingsfile=etc/settings.ini
    if [ ! -f $settingsfile ]; then
        cat > $settingsfile << _EOF_
#
#  Caminae Settings
#..........................
# (Note: If you edit this file out of install process, 
#  run "make deploy" to apply changes)

[settings]
dbname = caminae
dbuser = postgres
dbpassword = postgres
dbhost = localhost
dbport = 5432

rooturl = 

defaultstructure = PNE
srid = 2154
_EOF_
    fi
    # Prompt user to edit/review settings
    editor $settingsfile
    
    # Activate PostGIS in database
    dbname=$(sed -n 's/.*dbname *= *\([^ ]*.*\)/\1/p' < $settingsfile)
    sudo -n -u postgres -s -- psql -c "CREATE DATABASE ${dbname};"
    sudo -n -u postgres -s -- psql -d ${dbname} -c "CREATE EXTENSION postgis;"
    
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
        sudo -n -u postgres -s -- createdb template_postgis
        sudo -n -u postgres -s -- psql -d template_postgis -c "CREATE EXTENSION postgis"
        sudo -n -u postgres -s -- psql -d template_postgis -c "VACUUM FREEZE"
        sudo -n -u postgres -s -- psql -c "UPDATE pg_database SET datistemplate = TRUE WHERE datname = 'template_postgis'"
        sudo -n -u postgres -s -- psql -c "UPDATE pg_database SET datallowconn = FALSE WHERE datname = 'template_postgis'"
        
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
