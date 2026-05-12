.. _maintenance:

===========
Maintenance
===========

This section covers the periodic tasks required to ensure the system remains healthy and performs optimally.

These tasks include :

* Enabling maintenance mode when necessary
* Cleaning up attachments
* Clearing caches

Regular execution of these actions helps maintain system stability, performance, and data integrity.

Maintenance mode
================

If you want to block access to your application while you are performing maintenance tasks, you can activate the maintenance mode.
This will display a message to users indicating that the application is temporarily unavailable.

.. md-tab-set::
    :name: maintenance-mode

    .. md-tab-item:: With Debian

            .. code-block:: bash

                sudo geotrek maintenance_mode on # activate maintenance mode
                sudo geotrek maintenance_mode off # deactivate maintenance mode

    .. md-tab-item:: With Docker

         .. code-block:: bash

                docker compose run --rm web ./manage.py maintenance_mode on # activate maintenance mode
                docker compose run --rm web ./manage.py maintenance_mode off # deactivate maintenance mode

.. _postgresql-optimization:

PostgreSQL optimization
=======================

* Increase ``shared_buffers`` and ``work_mem`` according to your RAM

* `Log long queries <http://wiki.postgresql.org/wiki/Logging_Difficult_Queries>`_

* Use `pg activity <https://github.com/julmon/pg_activity#readme>`_ for monitoring

.. _access-your-database-securely-on-your-local-machine-qgis:

Access your database securely on your local machine (QGIS)
==========================================================

Instead of opening your database to the world (by opening the 5432 port for
example), you can use `SSH tunnels <https://www.postgresql.org/docs/current/ssh-tunnels.html>`_. Follow `this tutorial <https://makina-corpus.com/devops/acceder-base-donnees-postgresql-depuis-qgis-pgadmin-securisee>`_ for more information (in french).

.. _manage-cache:

Manage Cache
============

You can purge application cache :

- with command line :

.. md-tab-set::
    :name: purge-cache-tabs

    .. md-tab-item:: With Debian

         .. code-block:: bash

            sudo geotrek clearcache 

    .. md-tab-item:: With Docker

         .. code-block:: python
    
          docker compose run --rm web ./manage.py clearcache 

- in Geotrek-admin interface : ``https://<server_url>/admin/clearcache/``