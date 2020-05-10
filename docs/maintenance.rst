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

Database

.. code-block:: bash

    sudo -u postgres pg_dump -Fc geotrekdb > `date +%Y%m%d%H%M`-database.backup

Media files

.. code-block:: bash

    tar -zcvf `date +%Y%m%d%H%M`-media.tar.gz /opt/geotrek-admin/var/media/

Configuration

.. code-block:: bash

    tar -zcvf `date +%Y%m%d%H%M`-conf.tar.gz /opt/geotrek-admin/var/conf/


Application restore
-------------------

Create empty database:

.. code-block:: bash

    sudo -u postgres psql -c "CREATE DATABASE geotrekdb ENCODING 'UTF8' TEMPLATE template0;"
    sudo -u psql -d geotrekdb -c "CREATE EXTENSION postgis;"


Restore backup:

.. code-block:: bash

    sudo -u postgres pg_restore -d geotrekdb 20140610-geotrekdb.backup


Extract media and configuration files:

.. code-block:: bash

    tar -zxvf 20140610-media.tar.gz
    tar -zxvf 20140610-conf.tar.gz

Follow fresh installation method. Choose to manage database by yourself.


PostgreSQL optimization
-----------------------

* Increase ``shared_buffers`` and ``work_mem`` according to your RAM

* `Log long queries <http://wiki.postgresql.org/wiki/Logging_Difficult_Queries>`_

* Use `pg activity <https://github.com/julmon/pg_activity#readme>`_ for monitoring


Access your database securely on your local machine (QGIS)
----------------------------------------------------------

Instead of opening your database to the world (by opening the 5432 port for
example), you can use `SSH tunnels <http://www.postgresql.org/docs/9.3/static/ssh-tunnels.html>`_.
