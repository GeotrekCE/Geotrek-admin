.. _synchronization-section:

===============
Synchronization
===============

.. contents::
   :local:
   :depth: 2


Geotrek-mobile app v3
---------------------

The Geotrek-mobile app v3 has its own API and synchronization command called ``sync_mobile``.

::

    geotrek sync_mobile [-h] [--languages LANGUAGES] [--portal PORTAL]
                        [--skip-tiles] [--url URL] [--indent INDENT]
                        [--version] [-v {0,1,2,3}] [--settings SETTINGS]
                        [--pythonpath PYTHONPATH] [--traceback]
                        [--no-color] [--force-color]
                        path

Automatic synchronization
-------------------------

You can set up automatic synchronization by creating a file ``/etc/cron.d/geotrek_sync`` that contains:

::

    0 3 * * * root /usr/sbin/geotrek sync_mobile /opt/geotrek-admin/var/data

This example will automatically synchronize data a 3 am every day.

Note: it is required to give the full path to the geotrek command since cron set the PATH only to `bin:/usr/bin`.
