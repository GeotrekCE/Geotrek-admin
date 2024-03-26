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


Synchronization with a distant Geotrek-rando server
---------------------------------------------------

If your server hosts both Geotrek-admin and Geotrek-rando, you just have to configure Geotrek-rando so
it uses the directory chosen above. Be sure NGINX or Apache will have access rights to read these data.

If you have separated servers, you have to copy files, for example with ``rsync`` command:

::

    rsync /path/of/generated/data other-server:/path/of/generated/data
