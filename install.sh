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
        sudo -n -u postgres -s -- psql -tAl | grep -q "^$1|"
        return $?
    fi
}


user_exists () {
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

ini_value () {
    echo $(sed -n "s/.*$2 *= *\([^ ]*.*\)/\1/p" < $1)
}

migrate_settings () {
    userfile=$1
    samplefile=$2
    cp $userfile $userfile.$(date +%y%m%d%H%M)
    
     grep -e '^[a-zA-Z]' $samplefile | while read line; do
         inikey=$(echo $line | sed -n 's/\([^ ]*.*\) *=.*/\1/p')
         if [ $(grep $inikey $userfile | wc -l) -eq 0 ] ;
         then
            echo "Setting $inikey was missing, add default."
            echo $line >> $userfile
         fi
    done
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

    sudo apt-get update > /dev/null
    sudo apt-get install -y python-software-properties
    sudo apt-add-repository -y ppa:ubuntugis/ubuntugis-unstable
    sudo apt-add-repository -y ppa:sharpie/postgis-stable
    sudo apt-get update > /dev/null
    sudo apt-get install -y git gettext python-virtualenv build-essential python-dev unzip
    sudo apt-get install -y libjson0 libgdal1 libgdal-dev libproj0 libgeos-c1
    sudo apt-get install -y postgresql-client postgis-bin gdal-bin

    # Default settings if not any
    mkdir -p etc/
    settingsfile=etc/settings.ini
    settingssample=caminae/conf/settings.ini.sample
    if [ ! -f $settingsfile ]; then
        if [ -f $settingssample ]; then
            cp $settingssample $settingsfile
        else
            echo "# WARNING : empty configuration ! Use model file 'settings.ini.sample'" > $settingsfile
        fi
    else
        migrate_settings $settingsfile $settingssample
    fi
    
    # Prompt user to edit/review settings
    vim -c 'startinsert' $settingsfile

    #
    # If database is local, check it !
    #----------------------------------
    dbname=$(ini_value $settingsfile dbname)
    dbhost=$(ini_value $settingsfile dbhost)
    dbpassword=$(ini_value $settingsfile dbpassword)
    
    if [ "${dbhost}" == "localhost" ] ; then
        echo "Installing postgresql server locally..."
        sudo apt-get install -y postgresql postgresql-9.1-postgis2 postgresql-server-dev-9.1
        
        # Activate PostGIS in database
        if ! database_exists ${dbname}
        then
            sudo -n -u postgres -s -- psql -c "CREATE DATABASE ${dbname};"
            sudo -n -u postgres -s -- psql -d ${dbname} -c "CREATE EXTENSION postgis;"
        fi
        
        # Create user if missing
        if ! user_exists ${dbuser}
        then
            sudo -n -u postgres -s -- psql -c "CREATE USER ${dbuser} WITH PASSWORD '${dbpassword}';"
            sudo -n -u postgres -s -- psql -c "GRANT ALL PRIVILEGES ON DATABASE ${dbname} TO ${dbuser};"
            
            # Open local and host connection for this user as md5
            sudo cat >> /etc/postgresql/9.1/main/pg_hba.conf << _EOF_
# Automatically added by Caminae installation :
local    ${dbname}    ${dbuser}        md5
host     ${dbname}    ${dbuser}        md5
_EOF_
            sudo /etc/init.d/postgresql restart
        fi
    else
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
    fi


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

    if $dev ; then
        # A postgis template is required for django tests
        if [ "${dbhost}" == "localhost" ] ; then
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
    else
        sudo apt-get install -y nginx
        sudo apt-get install -y yui-compressor

        make deploy

        sudo rm /etc/nginx/sites-enabled/default
        sudo cp etc/nginx.conf /etc/nginx/sites-enabled/default
        sudo /etc/init.d/nginx restart
        
        sudo cp etc/init/supervisor.conf /etc/init/supervisor.conf
        sudo start supervisor
    fi

    set +x

    sudo chmod 600 install.log
    echo "Output is available in 'install.log'"
    echo "Done."
}


precise=$(grep "Ubuntu 12.04" /etc/issue | wc -l)

if [ $precise -eq 1 ] ; then
    ubuntu_precise
else
    echo "Unsupported operating system. Aborted."
    exit 5
fi
