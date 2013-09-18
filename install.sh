#!/usr/bin/env bash

# Make sure only root can run our script
if [ "$(id -u)" == "0" ]; then
   echo "This script must NOT be run as root" 1>&2
   exit 2
fi

# Make sure script runs from source root
if [ ! -f Makefile ]; then
   echo "This script must be run from source folder (c.f. README)" 1>&2
   exit 3
fi

#
# Redirect whole output to log file
#----------------------------------
exec > >(tee install.log)
exec 2>&1

#
#  Install system dependencies
#.............................

dev=false
settingsfile=etc/settings.ini

usage () {
    cat <<- _EOF_
Usage: Install project [OPTIONS]
    -d, --dev    install development environment
    -h, --help   show this help
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


function database_exists () {
    # /!\ Will return false if psql can't list database. Edit your pg_hba.conf
    # as appropriate.
    if [ -z $1 ]
    then
        # Argument is null
        return 0
    else
        # Grep db name in the list of database
        sudo -n -u postgres -s -- psql -tAl | grep -q "^$1|"
        return $?
    fi
}


function user_does_not_exists () {
    # /!\ Will return false if psql can't list database. Edit your pg_hba.conf
    # as appropriate.
    if [ -z $1 ]
    then
        # Argument is null
        return 0
    else
        exists=`sudo -n -u postgres -s -- psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$1'" | wc -l`
        return $exists
    fi
}


function ini_value () {
    echo $(sed -n "s/^\s*$2 *= *\([^ ]*.*\)/\1/p" < $1)
}


function geotrek_system_dependencies {
    sudo apt-get install -y python-software-properties
    sudo apt-add-repository -y ppa:git-core/ppa
    sudo apt-add-repository -y ppa:ubuntugis/ppa
    sudo apt-get update > /dev/null
    sudo apt-get install -y git gettext python-virtualenv build-essential python-dev unzip
    sudo apt-get install -y libjson0 libgdal1 libgdal-dev libproj0 libgeos-c1
    sudo apt-get install -y postgresql-client gdal-bin
    sudo apt-get install -y libxml2-dev libxslt-dev  # pygal lxml

    if ! $dev ; then
        sudo apt-get install -y ntp fail2ban
        sudo apt-get install -y nginx memcached
    if
}

function convertit_system_dependencies {
    if ! $dev ; then
        sudo apt-get install -y libreoffice unoconv inkscape
    if
}


function screamshotter_system_dependencies {
    arch=`uname -m`
    libpath=`pwd`/lib
    mkdir -p $libpath
    wget http://phantomjs.googlecode.com/files/phantomjs-1.8.1-linux-$arch.tar.bz2 -O phantomjs.tar.bz2
    rm -rf $libpath/*phantomjs*/
    tar -jxvf phantomjs.tar.bz2 -C $libpath/
    rm phantomjs.tar.bz2
    ln -sf $libpath/*phantomjs*/bin/phantomjs `pwd`/bin/

    wget https://github.com/n1k0/casperjs/zipball/1.0.2 -O casperjs.zip
    rm -rf $libpath/*casperjs*/
    unzip -o casperjs.zip -d $libpath/ > /dev/null
    rm casperjs.zip
    ln -sf $libpath/*casperjs*/bin/casperjs `pwd`/bin/

    if ! $dev ; then
        # Install system-wide binaries
        sudo ln -sf `pwd`/bin/phantomjs /usr/local/bin/
        sudo ln -sf `pwd`/bin/casperjs /usr/local/bin/
    fi
}


function install_postgres_local {
    echo "Installing postgresql server locally..."
    sudo apt-get install -y postgresql postgis postgresql-server-dev-9.1
    
    dbname=$(ini_value $settingsfile dbname)
    dbuser=$(ini_value $settingsfile dbuser)
    dbpassword=$(ini_value $settingsfile dbpassword)
    
    # Activate PostGIS in database
    if ! database_exists ${dbname}
    then
        sudo -n -u postgres -s -- psql -c "CREATE DATABASE ${dbname} ENCODING 'UTF8';"
        sudo -n -u postgres -s -- psql -d ${dbname} -c "CREATE EXTENSION postgis;"
    fi
    
    # Create user if missing
    if user_does_not_exists ${dbuser}
    then
        sudo -n -u postgres -s -- psql -c "CREATE USER ${dbuser} WITH PASSWORD '${dbpassword}';"
        sudo -n -u postgres -s -- psql -c "GRANT ALL PRIVILEGES ON DATABASE ${dbname} TO ${dbuser};"
        sudo -n -u postgres -s -- psql -d ${dbname} -c "GRANT ALL ON spatial_ref_sys, geometry_columns, raster_columns TO ${dbuser};" 
        
        # Open local and host connection for this user as md5
        sudo sed -i "/DISABLE/a \
# Automatically added by Geotrek installation :\
local    ${dbname}    ${dbuser}                 md5" /etc/postgresql/9.1/main/pg_hba.conf

        cat << _EOF_ | sudo tee -a /etc/postgresql/9.1/main/pg_hba.conf
# Automatically added by Geotrek installation :
local    ${dbname}     ${dbuser}                   md5
host     ${dbname}     ${dbuser}     0.0.0.0/0     md5
_EOF_
        sudo /etc/init.d/postgresql restart
    fi

    if $dev ; then
        # In development give full rights to db user
        sudo -n -u postgres -s -- psql -c "ALTER ROLE ${dbuser} SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN;"
        # A postgis template is required for django tests
        if ! database_exists template_postgis
        then
            sudo -n -u postgres -s -- createdb template_postgis
            sudo -n -u postgres -s -- psql -d template_postgis -c "CREATE EXTENSION postgis"
            sudo -n -u postgres -s -- psql -d template_postgis -c "VACUUM FREEZE"
            sudo -n -u postgres -s -- psql -c "UPDATE pg_database SET datistemplate = TRUE WHERE datname = 'template_postgis'"
            sudo -n -u postgres -s -- psql -c "UPDATE pg_database SET datallowconn = FALSE WHERE datname = 'template_postgis'"
            
            # Listen to all network interfaces (useful for VM etc.)
            listen="'*'"
            sudo sed -i "s/^#listen_addresses.*$/listen_addresses = $listen/" /etc/postgresql/9.1/main/postgresql.conf
            sudo /etc/init.d/postgresql restart
        fi
    fi
}


function check_postgres_connection {
    # Check that database connection is correct
    dbport=$(ini_value $settingsfile dbport)
    export PGPASSWORD=$dbpassword
    psql $dbname -h $dbhost -p $dbport -U $dbuser -c "SELECT NOW();"
    result=$?
    export PGPASSWORD=
    if [ ! $result -eq 0 ]
    then
        echo "Failed to connect to database with settings provided in '$settingsfile'."
        echo "Check your postgres configuration (``pg_hba.conf``) : it should allow md5 identification for user '${dbuser}' on database '${dbname}'"
        exit 4
    fi
}


function geotrek_setup {
    set -x

    sudo locale-gen fr_FR.UTF-8
    sudo dpkg-reconfigure locales
    sudo apt-get update > /dev/null

    geotrek_system_dependencies
    convertit_system_dependencies
    screamshotter_system_dependencies

    # Basic python dependencies
    make install

    if ! $dev ; then
      # Prompt user to edit/review settings
      editor $settingsfile
    fi

    dbhost=$(ini_value $settingsfile dbhost)

    # If database is local, install it !
    if [ "${dbhost}" == "localhost" ] ; then
        install_postgres_local
    fi

    check_postgres_connection

    if ! $dev ; then

        make env_standalone deploy

        # If buildout was successful, deploy really !
        if [ -f etc/nginx.conf ]; then
            sudo rm /etc/nginx/sites-enabled/default
            sudo cp etc/nginx.conf /etc/nginx/sites-available/geotrek
            sudo ln -sf /etc/nginx/sites-available/geotrek /etc/nginx/sites-enabled/geotrek
            sudo /etc/init.d/nginx restart

            if [ -f /etc/init/supervisor.conf ]; then
                # Previous Geotrek naming
                sudo stop supervisor
                sudo rm -f /etc/init/supervisor.conf
            fi

            sudo cp etc/init/supervisor.conf /etc/init/geotrek.conf
            sudo stop geotrek
            sudo start geotrek
        else
            echo "Geotrek package could not be installed."
            exit 6
        fi
    fi

    set +x

    sudo chmod 600 install.log
    echo "Output is available in 'install.log'"
    echo "Done."
}


precise=$(grep "Ubuntu 12.04" /etc/issue | wc -l)

if [ $precise -eq 1 ] ; then
    geotrek_setup
else
    echo "Unsupported operating system. Aborted."
    exit 5
fi
