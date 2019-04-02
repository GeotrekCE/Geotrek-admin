================
Server Migration
================

The commands below are examples to adapt to your actual configuration
(server names, database configuration).

Backup settings, media files and database on the old server:

::

    cd Geotrek
    sudo -u postgres pg_dump -Fc geotrekdb > geotrekdb.backup
    tar cvzf data.tgz geotrekdb.backup bulkimport/parsers.py var/static/ var/media/paperclip/ var/media/upload/ var/media/templates/ etc/settings.ini geotrek/settings/custom.py

Good example to know how to use pg_dump and pg_restore https://devcenter.heroku.com/articles/heroku-postgres-import-export

Get and unzip Geotrek sources on the new server:

::

    wget https://github.com/GeotrekCE/Geotrek-admin/archive/2.0.0.zip
    unzip 2.0.0.zip
    mv Geotrek-2.0.0 Geotrek
    cd Geotrek

Restore files on the new server:

::

    scp old_server:Geotrek/data.tgz .
    tar xvzf data.tgz

Then edit `etc/settings.ini` to update host variable and `geotrek/settings/custom.py`
to update IGN key.

Install Geotrek on the new server:

::

    ./install.sh

Restore database on the new server:

::

    sudo supervisorctl stop all
    sudo -u postgres psql -c "drop database geotrekdb;"
    sudo -u postgres psql -c "create database geotrekdb owner geotrek;"
    sudo -u postgres pg_restore -d geotrekdb geotrekdb.backup
    make update
    sudo supervisorctl start all