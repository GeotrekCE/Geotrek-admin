===========
MAINTENANCE
===========


Operating system updates
------------------------

.. code-block:: bash

    sudo apt-get update
    sudo apt-get dist-upgrade


Application backup
------------------

Give postgresql the right to write files in application folder :

.. code-block:: bash

    sudo adduser postgres `whoami`

Database

.. code-block:: bash

    sudo su postgres
    pg_dump -Fc geotrekdb > /home/sentiers/`date +%Y%m%d%H%M`-database.backup
    exit

Media files

.. code-block:: bash

    cd Geotrek-vX.Y.Z/
    tar -zcvf /home/sentiers/`date +%Y%m%d%H%M`-media.tar.gz var/media/


Configuration

.. code-block:: bash

    # Folder Geotrek-vX.Y.Z/
    tar -zcvf /home/sentiers/`date +%Y%m%d%H%M`-conf.tar.gz etc/ geotrek/settings/custom.py



Application restore
-------------------

Create empty database :

.. code-block:: bash

    sudo su postgres

    psql -c "CREATE DATABASE ${dbname} ENCODING 'UTF8' TEMPLATE template0;"
    psql -d geotrekdb -c "CREATE EXTENSION postgis;"


Restore backup :

.. code-block:: bash

    pg_restore -d geotrekdb 20140610-geotrekdb.backup
    exit


Extract media and configuration files :

.. code-block:: bash

    cd Geotrek-vX.Y.Z/
    tar -zxvf 20140610-media.tar.gz
    tar -zxvf 20140610-conf.tar.gz

Re-run ``./install.sh``.


PostgreSQL optimization
-----------------------

* Increase ``shared_buffers`` and ``work_mem`` according to your RAM

* `Log long queries <http://wiki.postgresql.org/wiki/Logging_Difficult_Queries>`_

* Use `pg activity <https://github.com/julmon/pg_activity#readme>`_ for monitoring


Access your database securely on your local machine (QGis)
----------------------------------------------------------

Instead of opening your database to the world (by opening the port 5432 for
example), you can use `SSH tunnels <http://www.postgresql.org/docs/9.3/static/ssh-tunnels.html>`_.
