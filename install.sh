#!/usr/bin/env bash

if [ "$(id -u)" == "0" ]; then
   echo -e "\e[91m\e[1mThis script should NOT be run as root\e[0m" >&2
fi

# Go to folder of install.sh
cd "$(dirname "$0")"

#------------------------------------------------------------------------------

# Redirect whole output to log file
rm -f install.log
touch install.log
chmod 600 install.log

exec 3>&1 4>&2
exec 1> install.log 2>&1

#------------------------------------------------------------------------------

STABLE_VERSION=${STABLE_VERSION:-2.11.3}
dev=false
tests=false
prod=false
standalone=true
interactive=true
settingsfile=etc/settings.ini


usage () {
    exec 2>&4
    cat >&2 <<- _EOF_
Usage: Install project [OPTIONS]
    -d, --dev         minimum dependencies for development
    -t, --tests       install testing environment
    -p, --prod        deploy a production instance
    --noinput         do not prompt user
    -s, --standalone  deploy a single-server production instance (Default)
    -h, --help        show this help
_EOF_
    exec 2>&1
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


function echo_header () {
    set +x
    exec 2>&4
    cat docs/logo.ans >&2
    exec 2>&1
    set -x
    version=$(cat VERSION)
    echo_step      "... install $version" >&2
    if [ ! -z $1 ] ; then
        echo_warn "... upgrade $1" >&2
    fi
    echo_step      "(details in install.log)" >&2
    echo_step >&2
}


function existing_version {
    existing=`cat /etc/supervisor/conf.d/supervisor-geotrek.conf | grep directory | sed "s/^directory=\(.*\)etc$/\1VERSION/"`
    if [ ! -z $existing ]; then
        version=`cat $existing`
    fi
    echo $version
}


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


function check_postgres_connection {
    echo_step "Check postgres connection settings..."
    # Check that database connection is correct
    dbname=$(ini_value $settingsfile dbname)
    dbhost=$(ini_value $settingsfile dbhost)
    dbport=$(ini_value $settingsfile dbport)
    dbuser=$(ini_value $settingsfile dbuser)
    dbpassword=$(ini_value $settingsfile dbpassword)

    export PGPASSWORD=$dbpassword
    psql $dbname -h $dbhost -p $dbport -U $dbuser -c "SELECT PostGIS_full_version();"
    result=$?
    export PGPASSWORD=
    if [ ! $result -eq 0 ]
    then
        echo_error "Failed to connect to database with settings provided in '$settingsfile'."
        exit_error 4 "Check your postgres configuration (``pg_hba.conf``) : it should allow md5 identification for user '${dbuser}' on database '${dbname}'"
    fi
}


function minimum_system_dependencies {
    sudo apt-get update -qq
    echo_progress
    sudo apt-get install -y -qq python unzip wget python-software-properties
    echo_progress
    if [ $precise -eq 1 ]; then
        sudo apt-add-repository -y ppa:git-core/ppa
        sudo apt-add-repository -y ppa:ubuntugis/ppa
        sudo apt-get update -qq
        echo_progress
    fi

    sudo apt-get install -y -qq git gettext python-virtualenv build-essential python-dev
    echo_progress
}


function geotrek_system_dependencies {
    sudo apt-get install -y -q --no-upgrade libjson0 gdal-bin libgdal-dev
    
    if [ $xenial -eq 1 ]; then
        sudo apt-get install libgeos-c1v5 libproj9
    else
        sudo apt-get install libgeos-c1 libproj0
    fi
    
    echo_progress
    # PostgreSQL client and headers
    sudo apt-get install -y -q --no-upgrade postgresql-client-$psql_version postgresql-server-dev-$psql_version
    echo_progress
    sudo apt-get install -y -qq libxml2-dev libxslt-dev  # pygal lxml
    echo_progress
    # Necessary for MapEntity Weasyprint
    sudo apt-get install -y -qq python-dev python-lxml libcairo2 libpango1.0-0 libgdk-pixbuf2.0-dev libffi-dev shared-mime-info
    echo_progress
    # Redis for async imports and tasks management
    sudo apt-get install -y -qq redis-server
    echo_progress

    if $prod || $standalone ; then
        sudo apt-get install -y -qq ntp fail2ban
        echo_progress
        sudo apt-get install -y -qq nginx memcached supervisor
        echo_progress
    fi
}


function convertit_system_dependencies {
    if $standalone ; then
        echo_step "Conversion server dependencies..."
        sudo apt-get install -y -qq libreoffice unoconv inkscape
        echo_progress
    fi
}


function screamshotter_system_dependencies {
    if $dev || $tests || $standalone ; then
        # Note: because tests require casper and phantomjs
        echo_step "Capture server dependencies..."
        arch=`uname -m`
        libpath=`pwd`/lib
        binpath=`pwd`/bin
        mkdir -p $libpath
        mkdir -p $binpath

        wget --quiet https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.7-linux-$arch.tar.bz2 -O phantomjs.tar.bz2
        if [ ! $? -eq 0 ]; then exit_error 8 "Failed to download phantomjs"; fi
        rm -rf $libpath/*phantomjs*/
        tar -jxvf phantomjs.tar.bz2 -C $libpath/ > /dev/null
        rm phantomjs.tar.bz2
        ln -sf $libpath/*phantomjs*/bin/phantomjs $binpath/phantomjs
        echo_progress

        wget --quiet https://github.com/n1k0/casperjs/archive/1.1-beta3.zip -O casperjs.zip
        if [ ! $? -eq 0 ]; then exit_error 9 "Failed to download casperjs"; fi
        rm -rf $libpath/*casperjs*/
        unzip -o casperjs.zip -d $libpath/ > /dev/null
        rm casperjs.zip
        ln -sf $libpath/*casperjs*/bin/casperjs $binpath/casperjs
        echo_progress

        if ! $dev ; then
            # Install system-wide binaries
            sudo ln -sf $binpath/phantomjs /usr/local/bin/phantomjs
            sudo ln -sf $binpath/casperjs /usr/local/bin/casperjs
        fi
    fi
}


function install_postgres_local {
    echo_step "Installing postgresql server locally..."
    sudo apt-get install -y -q postgresql-$psql_version postgresql-$psql_version-postgis-$pgis_version
    sudo /etc/init.d/postgresql restart
    echo_progress

    dbname=$(ini_value $settingsfile dbname)
    dbuser=$(ini_value $settingsfile dbuser)
    dbpassword=$(ini_value $settingsfile dbpassword)

    # Create user if missing
    if user_does_not_exists ${dbuser}
    then
        echo_step "Create user ${dbuser}  and configure database access rights..."
        sudo -n -u postgres -s -- psql -c "CREATE USER ${dbuser} WITH PASSWORD '${dbpassword}';"
        echo_progress

        # Open local and host connection for this user as md5
        sudo sed -i "/DISABLE/a \
# Automatically added by Geotrek installation :\
local    ${dbname}    ${dbuser}                 md5" /etc/postgresql/*/main/pg_hba.conf

        cat << _EOF_ | sudo tee -a /etc/postgresql/*/main/pg_hba.conf
# Automatically added by Geotrek installation :
local    ${dbname}     ${dbuser}                   md5
host     ${dbname}     ${dbuser}     0.0.0.0/0     md5
_EOF_
        sudo /etc/init.d/postgresql restart
        echo_progress
    fi

    # Create database and activate PostGIS in database
    if ! database_exists ${dbname}
    then
        echo_step "Create database ${dbname}..."
        sudo -n -u postgres -s -- psql -c "CREATE DATABASE ${dbname} ENCODING 'UTF8' TEMPLATE template0 OWNER ${dbuser};"
        sudo -n -u postgres -s -- psql -d ${dbname} -c "CREATE EXTENSION postgis;"
        sudo -n -u postgres -s -- psql -c "GRANT ALL PRIVILEGES ON DATABASE ${dbname} TO ${dbuser};"
        sudo -n -u postgres -s -- psql -d ${dbname} -c "GRANT ALL ON spatial_ref_sys, geometry_columns, raster_columns TO ${dbuser};"
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
            sudo sed -i "s/^#listen_addresses.*$/listen_addresses = $listen/" /etc/postgresql/*/main/postgresql.conf
            sudo sed -i "s/^client_min_messages.*$/client_min_messages = log/" /etc/postgresql/*/main/postgresql.conf
            sudo /etc/init.d/postgresql restart
        fi
    fi
}


function backup_existing_database {
    set +x
    if $interactive ; then
        exec 2>&4
        read -p "Backup existing database ? [yN] " -n 1 -r
        echo  # new line
        exec 2>&1
    else
        REPLY=N;
    fi
    set -x
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

    existing=$(existing_version)
    freshinstall=true
    if [ ! -z $existing ] ; then
        freshinstall=false
        if [ $existing \< "0.22" ]; then
            echo_warn "Geotrek $existing was detected."
            echo_error "Geotrek 0.22+ is required."
            exit 7
        fi
    fi

    echo_header $existing

    echo_step "Install system minimum components..."
    minimum_system_dependencies

    if [ ! -f Makefile ]; then
       echo_step "Downloading Geotrek latest stable version..."
       echo "wget --quiet https://github.com/makinacorpus/Geotrek/archive/$STABLE_VERSION.zip"
       wget --quiet https://github.com/makinacorpus/Geotrek/archive/$STABLE_VERSION.zip
       unzip $STABLE_VERSION.zip -d /tmp > /dev/null
       rm -f /tmp/Geotrek-$STABLE_VERSION/install.sh
       shopt -s dotglob nullglob
       mv /tmp/Geotrek-$STABLE_VERSION/* .
    fi

    if ! $freshinstall ; then
        backup_existing_database

        # Python should be fresh
        make clean
    fi

    # Python bootstrap
    make install
    echo_progress

    if $freshinstall && $interactive && ($prod || $standalone) ; then
        # Prompt user to edit/review settings
        exec 1>&3
        editor $settingsfile
        exec 1> install.log 2>&1
    fi

    echo_step "Configure Unicode and French locales..."
    #sudo apt-get update > /dev/null
    echo_progress
    sudo apt-get install -y -qq language-pack-en-base language-pack-fr-base
    sudo locale-gen fr_FR.UTF-8
    echo_progress

    echo_step "Install Geotrek system dependencies..."
    geotrek_system_dependencies
    convertit_system_dependencies
    screamshotter_system_dependencies

    # If database is local, install it !
    dbhost=$(ini_value $settingsfile dbhost)
    if [ "${dbhost}" == "localhost" ] ; then
        install_postgres_local
    fi

    check_postgres_connection
	
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
    success=$?
    if [ $success -ne 0 ]; then
        exit_error 3 "Could not setup python environment !"
    fi

    if $dev ; then
        echo_step "Initializing data..."
        make update
        echo_progress
    fi

    if $tests ; then
        # XXX: Why Django tests require the main database :( ?
        bin/django syncdb --noinput
        bin/django collectstatic --clear --noinput --verbosity=0
    fi

    if $prod || $standalone ; then

        echo_step "Generate services configuration files..."
        
        # restart supervisor in case of xenial before 'make deploy'
        sudo service supervisor force-stop && sudo service supervisor stop && sudo service supervisor start
        if [ $? -ne 0 ]; then
            exit_error 10 "Could not restart supervisor !"
        fi
        make update
        if [ $? -ne 0 ]; then
            exit_error 11 "Could not update data !"
        fi
        sudo service supervisor force-stop && sudo service supervisor stop && sudo service supervisor start
        if [ $? -ne 0 ]; then
            exit_error 12 "Could not restart supervisor !"
        fi
        echo_progress

        # If buildout was successful, deploy really !
        if [ -f /etc/supervisor/supervisord.conf ]; then
            sudo rm /etc/nginx/sites-enabled/default
            sudo cp etc/nginx.conf /etc/nginx/sites-available/geotrek
            sudo ln -sf /etc/nginx/sites-available/geotrek /etc/nginx/sites-enabled/geotrek

            # Nginx does not create log files !
            # touch var/log/nginx-access.log
            # touch var/log/nginx-error.log
			
			# if 15.04 or higher
			if [ $vivid -eq 1 -o $xenial -eq 1 ]; then
                sudo systemctl restart nginx
            else
                sudo /etc/init.d/nginx restart
            fi

            if [ -f /etc/init/supervisor.conf ]; then
                # Previous Geotrek naming
                sudo stop supervisor
                sudo rm -f /etc/init/supervisor.conf
            fi

            sudo cp etc/logrotate.conf /etc/logrotate.d/geotrek

            echo_step "Enable Geotrek services and start..."
            
            if [ -f /etc/init/geotrek.conf ]; then
                # Previous Geotrek naming
                sudo stop geotrek
                sudo rm -f /etc/init/geotrek.conf
            fi
            
            sudo chgrp www-data -R ./var/static
            sudo chmod g+r -R ./var/static
            sudo chgrp www-data -R ./var/media/upload
            
            sudo cp etc/supervisor-geotrek.conf /etc/supervisor/conf.d/
            sudo cp etc/supervisor-geotrek-api.conf /etc/supervisor/conf.d/
            sudo cp etc/supervisor-geotrek-celery.conf /etc/supervisor/conf.d/
            sudo cp etc/supervisor-tilecache.conf /etc/supervisor/conf.d/
            
            if $standalone ; then
                sudo cp etc/supervisor-convertit.conf /etc/supervisor/conf.d/
                sudo cp etc/supervisor-screamshotter.conf /etc/supervisor/conf.d/
            fi
            
            sudo supervisorctl reread
            sudo supervisorctl reload
            
            echo_progress
        else
            exit_error 6 "Geotrek package could not be installed."
        fi
    fi

    set +x

    echo_step "Done."
}

precise=$(grep "Ubuntu 12.04" /etc/issue | wc -l)
trusty=$(grep "Ubuntu 14.04" /etc/issue | wc -l)
vivid=$(grep "Ubuntu 15.04" /etc/issue | wc -l)
xenial=$(grep "Ubuntu 16.04" /etc/issue | wc -l)

if [ $precise -eq 1 ]; then
    psql_version=9.1
    pgis_version=2.0
elif [ $trusty -eq 1 ]; then
    psql_version=9.3
    pgis_version=2.1
elif [ $vivid -eq 1 ]; then
    psql_version=9.4
    pgis_version=2.1
elif [ $xenial -eq 1 ]; then
    psql_version=9.5
    pgis_version=2.2
fi

if [ $precise -eq 1 -o $trusty -eq 1 -o $vivid -eq 1 -o $xenial -eq 1 ] ; then
    geotrek_setup
else
    exit_error 5 "Unsupported operating system. Aborted."
fi
