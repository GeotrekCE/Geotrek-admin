#!/usr/bin/env bash

# Make sure only root can run our script
if [ "$(id -u)" == "0" ]; then
   echo "This script must NOT be run as root" 1>&2
   exit 2
fi

# Go to folder of install.sh
cd "$(dirname "$0")"

# Redirect whole output to log file
exec > >(tee install.log)
exec 2>&1


#------------------------------------------------------------------------------

dev=false
tests=false
prod=false
standalone=true
settingsfile=etc/settings.ini
branch=master

usage () {
    cat <<- _EOF_
Usage: Install project [OPTIONS]
    -d, --dev         minimum dependencies for development
    -t, --tests       install testing environment
    -p, --prod        deploy a production instance
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
#
#  Helpers
#
#------------------------------------------------------------------------------

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


function echo_step () {
    set +x
    echo -e "\e[92m\e[1m$1\e[0m"
    set -x
}


function echo_error () {
    set +x
    echo -e "\e[91m\e[1m$1\e[0m"
    set -x
}



function check_postgres_connection {
    echo_step "Check postgres connexion settings..."
    # Check that database connection is correct
    dbport=$(ini_value $settingsfile dbport)
    export PGPASSWORD=$dbpassword
    psql $dbname -h $dbhost -p $dbport -U $dbuser -c "SELECT NOW();"
    result=$?
    export PGPASSWORD=
    if [ ! $result -eq 0 ]
    then
        echo_error "Failed to connect to database with settings provided in '$settingsfile'."
        echo "Check your postgres configuration (``pg_hba.conf``) : it should allow md5 identification for user '${dbuser}' on database '${dbname}'"
        exit 4
    fi
}


function geotrek_system_dependencies {
    sudo apt-get install -y -qq unzip wget python-software-properties
    sudo apt-add-repository -y ppa:git-core/ppa
    sudo apt-add-repository -y ppa:ubuntugis/ppa
    sudo apt-get update -qq
    sudo apt-get install -y -qq git gettext python-virtualenv build-essential python-dev
    sudo apt-get install -y -qq libjson0 libgdal1 libgdal-dev libproj0 libgeos-c1
    sudo apt-get install -y -qq postgresql-client gdal-bin
    sudo apt-get install -y -qq libxml2-dev libxslt-dev  # pygal lxml

    if $prod || $standalone ; then
        sudo apt-get install -y -qq ntp fail2ban
        sudo apt-get install -y -qq nginx memcached
    fi
}


function convertit_system_dependencies {
    if $standalone ; then
        echo_step "Conversion server dependencies..."
        sudo apt-get install -y -qq libreoffice unoconv inkscape
    fi
}


function screamshotter_system_dependencies {
    if $dev || $tests || $standalone ; then
        # Note: because tests require casper and phantomjs
        echo_step "Capture server dependencies..."
        arch=`uname -m`
        libpath=`pwd`/lib
        mkdir -p $libpath
        wget --quiet http://phantomjs.googlecode.com/files/phantomjs-1.8.1-linux-$arch.tar.bz2 -O phantomjs.tar.bz2
        rm -rf $libpath/*phantomjs*/
        tar -jxvf phantomjs.tar.bz2 -C $libpath/ > /dev/null
        rm phantomjs.tar.bz2
        ln -sf $libpath/*phantomjs*/bin/phantomjs `pwd`/bin/

        wget --quiet https://github.com/n1k0/casperjs/zipball/1.0.2 -O casperjs.zip
        rm -rf $libpath/*casperjs*/
        unzip -o casperjs.zip -d $libpath/ > /dev/null
        rm casperjs.zip
        ln -sf $libpath/*casperjs*/bin/casperjs `pwd`/bin/

        if ! $dev ; then
            # Install system-wide binaries
            sudo ln -sf `pwd`/bin/phantomjs /usr/local/bin/
            sudo ln -sf `pwd`/bin/casperjs /usr/local/bin/
        fi
    fi
}


function install_postgres_local {
    echo_step "Installing postgresql server locally..."
    sudo apt-get install -y -qq postgresql postgis postgresql-server-dev-9.1

    dbname=$(ini_value $settingsfile dbname)
    dbuser=$(ini_value $settingsfile dbuser)
    dbpassword=$(ini_value $settingsfile dbpassword)

    # Activate PostGIS in database
    if ! database_exists ${dbname}
    then
        echo_step "Create database ${dbname}..."
        sudo -n -u postgres -s -- psql -c "CREATE DATABASE ${dbname} ENCODING 'UTF8' TEMPLATE template0;"
        sudo -n -u postgres -s -- psql -d ${dbname} -c "CREATE EXTENSION postgis;"
    fi

    # Create user if missing
    if user_does_not_exists ${dbuser}
    then
        echo_step "Create user ${dbuser}  and configure database access rights..."
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

    if $dev || $tests ; then
        echo_step "Give all priviliges to user ${dbuser}..."
        # In development give full rights to db user
        sudo -n -u postgres -s -- psql -c "ALTER ROLE ${dbuser} SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN;"
        # A postgis template is required for django tests
        if ! database_exists template_postgis
        then
            echo_step "Create template_postgis..."
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


function backup_existing_database {
    read -p "Backup existing database ? [yN] " -n 1 -r
    echo  # new line
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        dbname=$(ini_value $settingsfile dbname)
        echo_step "Backup existing database $name..."
        sudo -n -u postgres -s -- pg_dump --format=custom $dbname > `date +%Y%m%d%H%M`-$dbname.backup
    fi
}


#------------------------------------------------------------------------------
#
#  Install scenario
#
#------------------------------------------------------------------------------

function geotrek_setup {
    set -x

    echo_step "Configure Unicode and French locales..."
    sudo apt-get update > /dev/null
    sudo apt-get install -y -qq language-pack-en-base language-pack-fr-base
    sudo locale-gen fr_FR.UTF-8

    echo_step "Install system dependencies..."
    geotrek_system_dependencies
    convertit_system_dependencies
    screamshotter_system_dependencies

    if [ ! -f Makefile ]; then
       echo_step "Downloading Geotrek latest stable version..."
       wget --quiet https://github.com/makinacorpus/Geotrek/archive/$branch.zip
       unzip $branch.zip -d /tmp > /dev/null
       rm -f /tmp/Geotrek-$branch/install.sh
       shopt -s dotglob nullglob
       mv /tmp/Geotrek-$branch/* .
    fi

    freshinstall=true
    if [ -f $settingsfile ]; then
        freshinstall=false
    fi

    # Python bootstrap
    make install

    if $freshinstall && ($prod || $standalone) ; then
      # Prompt user to edit/review settings
      editor $settingsfile
    fi

    echo_step "Install Geotrek python dependencies..."
    if $dev ; then
        make env_dev
    elif $tests ; then
        make env_test
    elif $prod ; then
        make env_prod
    elif $standalone ; then
        make env_standalone
    fi

    # If database is local, install it !
    dbhost=$(ini_value $settingsfile dbhost)
    if [ "${dbhost}" == "localhost" ] ; then
        install_postgres_local
    fi

    check_postgres_connection

    if ! $freshinstall ; then
        backup_existing_database
    fi

    if $prod || $standalone ; then

        echo_step "Generate services configuration files..."
        make deploy

        # If buildout was successful, deploy really !
        if [ -f etc/init/supervisor.conf ]; then
            sudo rm /etc/nginx/sites-enabled/default
            sudo cp etc/nginx.conf /etc/nginx/sites-available/geotrek
            sudo ln -sf /etc/nginx/sites-available/geotrek /etc/nginx/sites-enabled/geotrek

            # Nginx does not create log files !
            touch var/log/nginx-access.log
            touch var/log/nginx-error.log

            sudo /etc/init.d/nginx restart

            if [ -f /etc/init/supervisor.conf ]; then
                # Previous Geotrek naming
                sudo stop supervisor
                sudo rm -f /etc/init/supervisor.conf
            fi

            echo_step "Enable Geotrek services and start..."
            sudo cp etc/init/supervisor.conf /etc/init/geotrek.conf
            sudo stop geotrek
            sudo start geotrek
        else
            echo_error "Geotrek package could not be installed."
            exit 6
        fi
    fi

    set +x

    sudo chmod 600 install.log
    echo "Output is available in 'install.log'"
    echo_step "Done."
}


precise=$(grep "Ubuntu 12.04" /etc/issue | wc -l)

if [ $precise -eq 1 ] ; then
    geotrek_setup
else
    echo "Unsupported operating system. Aborted."
    exit 5
fi
