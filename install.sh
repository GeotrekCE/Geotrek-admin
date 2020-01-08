#!/usr/bin/env bash

if [ "$(id -u)" == "0" ]; then
   echo -e "\e[91m\e[1mThis script should NOT be run as root\e[0m" >&2
fi

# Go to folder of install.sh
cd "$(dirname "$0")"

#------------------------------------------------------------------------------

STABLE_VERSION=${STABLE_VERSION:-2.32.1}
dev=false
prod=false
standalone=true
interactive=true


usage () {
    cat >&2 <<- _EOF_
Usage: $0 project [OPTIONS]
    -d, --dev         minimum dependencies for development
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
                            exit 1
                            ;;
    esac
    shift
done

#------------------------------------------------------------------------------

# Redirect whole output to log file
touch install.log
chmod 600 install.log
exec 3>&1 4>&2
if $interactive ; then
    exec 1>> install.log 2>&1
else
    exec 1>> >( tee --append install.log) 2>&1
fi

echo '------------------------------------------------------------------------------'
date --rfc-2822

# Debug
set -o errtrace
set -ex

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


function error_handler () {
    echo_error "An unexpected error occured (more details in install.log)"
}

trap error_handler ERR

function echo_header () {
    if $interactive; then
        set +x
        exec 2>&4
        echo -e "\n\n" >&2
        cat docs/logo.ans >&2
        exec 2>&1
        set -x
    fi
    version=$(cat VERSION)
    echo_step      "... install $version" >&2
    if [ ! -z $1 ] ; then
        echo_warn "... upgrade $1" >&2
        if [ "`echo -e "$1\n2.33.0" | sort -V | head -n1`" != "2.33.0" ]; then
            if [ ! -f var/conf/custom.py ]; then
                exit_error 1 "Migration from 2.32.3 or less. Please read https://geotrek.readthedocs.io/en/master/installation.html#software-update-from-2.32.3-or-less-to-2.33.0-or-more"
            fi
        fi
    fi
    echo_step      "(details in install.log)" >&2
}


function existing_version {
    existing=`cat /etc/supervisor/conf.d/supervisor-geotrek.conf | grep directory | sed "s;^directory=\(.*\)$;\1/VERSION;"`
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


function check_postgres_connection {
    echo_step "Check postgres connection settings..."
    # Check that database connection is correct
    POSTGRES_USER=`echo "from django.conf import settings; print(settings.DATABASES['default']['USER'])" | ./manage.py shell`
    POSTGRES_DB=`echo "from django.conf import settings; print(settings.DATABASES['default']['NAME'])" | ./manage.py shell`
    if [ ! `echo "SELECT 1" | ./env/bin/python manage.py dbshell` ]; then
        echo_error "Failed to connect to database with settings provided in 'var/conf/custom.py'."
        exit_error 4 "Check your postgres configuration (``pg_hba.conf``) : it should allow md5 identification for user '${POSTGRES_USER}' on database '${POSTGRES_DB}'"
    fi
}


function minimum_system_dependencies {
    sudo apt-get update -qq
    echo_progress
    sudo apt-get install -y -qq \
        python3 python3-venv unzip wget software-properties-common \
        git gettext build-essential python3-dev dialog
    echo_progress
}


function geotrek_system_dependencies {
    sudo apt-get install -y -qq --no-upgrade gdal-bin libgdal-dev libssl-dev binutils libproj-dev \
        fonts-dejavu-core fonts-liberation \
        postgresql-client-$psql_version postgresql-server-dev-$psql_version \
        libxml2-dev libxslt-dev \
        python3-lxml libcairo2 libpango1.0-0 libgdk-pixbuf2.0-dev libffi-dev shared-mime-info libfreetype6-dev \
        redis-server
    echo_progress

    if $prod || $standalone ; then
        sudo apt-get install -y -qq ntp nginx memcached supervisor
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
    libpath=`pwd`/env/lib
    binpath=`pwd`/env/bin
    if [ -x $binpath/phantomjs -a -x $binpath/casperjs ]; then
        echo_step "Skip capture server dependencies..."
        return
    fi
    if $dev || $standalone ; then
        # Note: because tests require casper and phantomjs
        echo_step "Capture server dependencies..."
        arch=`uname -m`
        mkdir -p $libpath
        mkdir -p $binpath

        wget --quiet https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-$arch.tar.bz2 -O phantomjs.tar.bz2
        if [ ! $? -eq 0 ]; then exit_error 8 "Failed to download phantomjs"; fi
        rm -rf $libpath/*phantomjs*/
        tar -jxvf phantomjs.tar.bz2 -C $libpath/ > /dev/null
        rm phantomjs.tar.bz2
        ln -sf $libpath/*phantomjs*/bin/phantomjs $binpath/phantomjs
        echo_progress

        wget --quiet https://github.com/n1k0/casperjs/archive/1.1.4-2.zip -O casperjs.zip
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

    POSTGRES_DB=`echo "from django.conf import settings; print(settings.DATABASES['default']['NAME'])" | ./manage.py shell`
    POSTGRES_USER=`echo "from django.conf import settings; print(settings.DATABASES['default']['USER'])" | ./manage.py shell`
    POSTGRES_PASSWORD=`echo "from django.conf import settings; print(settings.DATABASES['default']['PASSWORD'])" | ./manage.py shell`

    # Create user if missing
    if user_does_not_exists ${POSTGRES_USER}
    then
        echo_step "Create user ${POSTGRES_USER} and configure database access rights..."
        sudo -n -u postgres -s -- psql -c "CREATE USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';"
        echo_progress

        # Open local and host connection for this user as md5
        sudo sed -i "/DISABLE/a \
# Automatically added by Geotrek installation :\
local    ${POSTGRES_DB}    ${POSTGRES_USER}                 md5" /etc/postgresql/*/main/pg_hba.conf

        cat << _EOF_ | sudo tee -a /etc/postgresql/*/main/pg_hba.conf
# Automatically added by Geotrek installation :
local    ${POSTGRES_DB}     ${POSTGRES_USER}                   md5
host     ${POSTGRES_DB}     ${POSTGRES_USER}     0.0.0.0/0     md5
_EOF_
        sudo /etc/init.d/postgresql restart
        echo_progress
    fi

    # Create database and activate PostGIS in database
    if ! database_exists ${POSTGRES_DB}
    then
        echo_step "Create database ${POSTGRES_DB}..."
        sudo -n -u postgres -s -- psql -c "CREATE DATABASE ${POSTGRES_DB} ENCODING 'UTF8' TEMPLATE template0 OWNER ${POSTGRES_USER};"
        sudo -n -u postgres -s -- psql -d ${POSTGRES_DB} -c "CREATE EXTENSION postgis;"
        sudo -n -u postgres -s -- psql -c "GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER};"
        sudo -n -u postgres -s -- psql -d ${POSTGRES_DB} -c "GRANT ALL ON spatial_ref_sys, geometry_columns, raster_columns TO ${POSTGRES_USER};"
    fi
}


function backup_existing_database {
    if $interactive ; then
        set +x
        exec 2>&4
        read -p "Backup existing database ? [yN] " -n 1 -r
        echo  # new line
        exec 2>&1
        set -x
    else
        REPLY=N;
    fi
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        echo_step "Backup existing database $name..."
        POSTGRES_DB=`echo "from django.conf import settings; print(settings.DATABASES['default']['NAME'])" | ./manage.py shell`
        sudo -n -u postgres -s -- pg_dump --format=custom $POSTGRES_DB > `date +%Y%m%d%H%M`-$POSTGRES_DB.backup
    fi
}


#------------------------------------------------------------------------------
#
#  Install scenario
#
#------------------------------------------------------------------------------

function geotrek_setup {
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

    if ! $freshinstall ; then
        backup_existing_database
    fi

    # Config
    echo_progress
    mkdir -p \
        var/static \
        var/conf/extra_static \
        var/media/upload \
        var/data \
        var/cache \
        var/log \
        var/conf/extra_templates \
        var/conf/extra_locale \
        var/tmp \
        var/pid
    echo_progress
    if [ ! -f var/conf/custom.py ]; then
        if $interactive ; then
            allowed_hosts=$(dialog --title "Geotrek installation" --inputbox "Domain name(s) separated with spaces" 10 60 `hostname -f` 2>&1 1>&3)
            pg_host=$(dialog --title "Geotrek installation" --inputbox "PostgreSQL host. If you set it to localhost, Geotrek will configure database for you, otherwise you have to configure it yourself before proceeding." 10 60 localhost 2>&1 1>&3)
            pg_port=$(dialog --title "Geotrek installation" --inputbox "PostgreSQL port" 10 60 5432 2>&1 1>&3)
            pg_db=$(dialog --title "Geotrek installation" --inputbox "PostgreSQL database" 10 60 geotrekdb 2>&1 1>&3)
            pg_user=$(dialog --title "Geotrek installation" --inputbox "PostgreSQL user" 10 60 geotrek 2>&1 1>&3)
            pg_pwd=$(dialog --title "Geotrek installation" --inputbox "PostgreSQL password" 10 60 `dd bs=12 count=1 if=/dev/urandom 2>/dev/null | base64` 2>&1 1>&3)
            srid=$(dialog --title "Geotrek installation" --inputbox "Projection (SRID)" 10 60 2154 2>&1 1>&3)
            default_structure=$(dialog --title "Geotrek installation" --inputbox "Your organization name (short)" 10 60 Organisme 2>&1 1>&3)
            spatial_extent=$(dialog --title "Geotrek installation" --inputbox "Spatial extent (xmin ymin xmax ymax)" 10 60 "105000 6150000 1100000 7150000" 2>&1 1>&3)
            languages=$(dialog --title "Geotrek installation" --inputbox "Languages (2-letters codes separated by a space)" 10 60 "fr en" 2>&1 1>&3)
            default_language=$(dialog --title "Geotrek installation" --inputbox "Default language (2-letters code)" 10 60 `echo "$languages" | sed 's/^\([a-z][a-z]\).*$/\1/'` 2>&1 1>&3)
            time_zone=$(dialog --title "Geotrek installation" --inputbox "Time zone (from ICANN database)" 10 60 "Europe/Paris" 2>&1 1>&3)
            admin_email=$(dialog --title "Geotrek installation" --inputbox "Admin email to send technical error reports" 10 60 $USER@localhost 2>&1 1>&3)
            manager_email=$(dialog --title "Geotrek installation" --inputbox "Manager email to send user reports" 10 60 $admin_email 2>&1 1>&3)
            cp geotrek/settings/custom.py.dist var/conf/custom.py
            chmod -f 600 var/conf/custom.py
            sed -i "s%^ALLOWED_HOSTS *=.*%ALLOWED_HOSTS = ('`echo $allowed_hosts | sed \"s% \+%', '%g\"`')%" var/conf/custom.py
            sed -i "s%^DATABASES\['default'\]\['HOST'\] *=.*%DATABASES['default']['HOST'] = '$pg_host'%" var/conf/custom.py
            sed -i "s%^DATABASES\['default'\]\['PORT'\] *=.*%DATABASES['default']['PORT'] = '$pg_port'%" var/conf/custom.py
            sed -i "s%^DATABASES\['default'\]\['NAME'\] *=.*%DATABASES['default']['NAME'] = '$pg_db'%" var/conf/custom.py
            sed -i "s%^DATABASES\['default'\]\['USER'\] *=.*%DATABASES['default']['USER'] = '$pg_user'%" var/conf/custom.py
            sed -i "s%^DATABASES\['default'\]\['PASSWORD'\] *=.*%DATABASES['default']['PASSWORD'] = '$pg_pwd'%" var/conf/custom.py
            sed -i "s%^SRID *=.*%SRID = $srid%" var/conf/custom.py
            sed -i "s%^DEFAULT_STRUCTURE_NAME *=.*%DEFAULT_STRUCTURE_NAME = '$default_structure'%" var/conf/custom.py
            sed -i "s%^SPATIAL_EXTENT *=.*%SPATIAL_EXTENT = (`echo $spatial_extent | sed 's% \+%, %g'`)%" var/conf/custom.py
            sed -i "s%^MODELTRANSLATION_LANGUAGES *=.*%MODELTRANSLATION_LANGUAGES = ('`echo $languages | sed \"s% \+%', '%g\"`')%" var/conf/custom.py
            sed -i "s%^LANGUAGE_CODE *=.*%LANGUAGE_CODE = '$default_language'%" var/conf/custom.py
            sed -i "s%^TIME_ZONE *=.*%TIME_ZONE = '$time_zone'%" var/conf/custom.py
            sed -i "s%^ADMINS *=.*%ADMINS = (('admin', '$admin_email'), )%" var/conf/custom.py
            sed -i "s%^MANAGERS *=.*%MANAGERS = (('manager', '$manager_email'), )%" var/conf/custom.py
        fi
    fi
    echo_progress
    SECRET_KEY_FILE=var/conf/secret_key
    if [ ! -f $SECRET_KEY_FILE ]; then
        dd bs=48 count=1 if=/dev/urandom 2>/dev/null | base64 > $SECRET_KEY_FILE
        chmod go-r $SECRET_KEY_FILE
    fi

    echo_header $existing

    echo_step "Install system minimum components..."
    minimum_system_dependencies

    echo_step "Configure Unicode and French locales..."
    echo_progress
    sudo apt-get install -y -qq language-pack-en-base language-pack-fr-base
    sudo locale-gen fr_FR.UTF-8
    echo_progress

    echo_step "Install Geotrek system dependencies..."
    geotrek_system_dependencies
    convertit_system_dependencies
    screamshotter_system_dependencies

    # Python bootstrap
    if [ ! -x env/bin/python ]; then
        python3 -m venv env
        success=$?
        if [ $success -ne 0 ]; then
            exit_error 2 "Could not setup virtualenv !"
        fi
        ./env/bin/pip install --upgrade pip==19.3.1
    fi
    echo_progress

    echo_step "Install Geotrek python dependencies..."

    if [ $xenial -eq 1 ]; then
        ./env/bin/pip install GDAL==1.11.2 --global-option=build_ext --global-option="-I/usr/include/gdal/"
    fi
    if [ $bionic -eq 1 ]; then
        ./env/bin/pip install GDAL==2.2.4 --global-option=build_ext --global-option="-I/usr/include/gdal/"
    fi
    success=$?
    if [ $success -ne 0 ]; then
        exit_error 3 "Could not setup python GDAL !"
    fi

    ./env/bin/pip install -r requirements.txt
    success=$?
    if [ $success -ne 0 ]; then
        exit_error 3 "Could not setup python environment !"
    fi

    # If database is local, install it !
    POSTGRES_HOST=`echo "from django.conf import settings; print(settings.DATABASES['default']['HOST'])" | ./manage.py shell`
    if [ "${POSTGRES_HOST}" == "localhost" ] ; then
        install_postgres_local
    fi

    # as internal or external database, some commands needs postgis scripts
    sudo apt-get --no-install-recommends install postgis -y

    check_postgres_connection

    if $prod ; then
        ./manage.py generate_conf --user $UID
    elif $standalone ; then
        ./env/bin/pip install -r requirements-standalone.txt
        ./manage.py generate_conf --user $UID --standalone
    fi

    echo_step "Updating data..."
    make update
    if [ $? -ne 0 ]; then
        exit_error 11 "Could not update data !"
    fi
    echo_progress

    if $prod || $standalone ; then
        echo_step "Generate services configuration files..."

        # restart supervisor in case of xenial before 'make deploy'
        sudo service supervisor start
        if [ $? -ne 0 ]; then
            exit_error 10 "Could not start supervisord !"
        fi

        echo_progress

        # If buildout was successful, deploy really !
        if [ -f /etc/supervisor/supervisord.conf ]; then
            sudo rm -f /etc/nginx/sites-enabled/default
            sudo cp var/conf/nginx.conf /etc/nginx/sites-available/geotrek
            sudo ln -sf /etc/nginx/sites-available/geotrek /etc/nginx/sites-enabled/geotrek

            # Nginx does not create log files !
            # touch var/log/nginx-access.log
            # touch var/log/nginx-error.log

            sudo service nginx restart

            if [ -f /etc/init/supervisor.conf ]; then
                # Previous Geotrek naming
                sudo stop supervisor
                sudo rm -f /etc/init/supervisor.conf
            fi

            sudo cp var/conf/logrotate.conf /etc/logrotate.d/geotrek

            echo_step "Enable Geotrek services and start..."

            if [ -f /etc/init/geotrek.conf ]; then
                # Previous Geotrek naming
                sudo stop geotrek
                sudo rm -f /etc/init/geotrek.conf
            fi

            sudo chgrp www-data -R ./var/static
            sudo chmod g+r -R ./var/static
            sudo chgrp www-data -R ./var/media/upload

            sudo cp var/conf/supervisor-geotrek.conf /etc/supervisor/conf.d/
            sudo cp var/conf/supervisor-geotrek-api.conf /etc/supervisor/conf.d/
            sudo cp var/conf/supervisor-geotrek-celery.conf /etc/supervisor/conf.d/

            if $standalone ; then
                sudo cp var/conf/supervisor-convertit.conf /etc/supervisor/conf.d/
                sudo cp var/conf/supervisor-screamshotter.conf /etc/supervisor/conf.d/
            fi

            sudo supervisorctl reread
            sudo supervisorctl reload

            echo_progress
        else
            exit_error 6 "Geotrek package could not be installed."
        fi
    fi

    echo_step "Done."
}

precise=$(grep "Ubuntu 12.04" /etc/issue | wc -l)
trusty=$(grep "Ubuntu 14.04" /etc/issue | wc -l)
xenial=$(grep "Ubuntu 16.04" /etc/issue | wc -l)
bionic=$(grep "Ubuntu 18.04" /etc/issue | wc -l)

if [ $xenial -eq 1 ]; then
    psql_version=9.5
    pgis_version=2.2
elif [ $bionic -eq 1 ]; then
    psql_version=10
    pgis_version=2.4
fi

if [ $xenial -eq 1 -o $bionic -eq 1 ] ; then
    geotrek_setup
elif [ $precise -eq 1 ] ; then
    exit_error 5 "Support for Ubuntu Precise 12.04 was dropped. Upgrade your server first. Aborted."
elif [ $trusty -eq 1 ] ; then
    exit_error 5 "Support for Ubuntu Trusty 14.04 was dropped. Upgrade your server first. Aborted."
else
    exit_error 5 "Unsupported operating system. Aborted."
fi
