===============
SYNCHRONIZATION
===============


Manual synchronization
----------------------

To create data for Geotrek-Rando (web public portal) and Geotrek-Mobile (mobile phone app),
just run this command:

::

    ./bin/django sync_rando /where/to/generate/data

The last parameter is the destination directory for synchronized data.
If Geotrek-Admin is not accessible on localhost:80, you have to use the `--url` option.
To make output less or more verbose, you can use the `--verbose` option.


Automatic synchronization
-------------------------

You can set up automatic synchronization by creating a file `/etc/crond.d/geotrek_sync` that contains:

::

    0 3 * * * root /path/to/geotrek/bin/django sync_rando /where/to/generate/data

This will automatically synchronize data a 3 am every day.


Synchronization with a distant Geotrek-Rando serveur
----------------------------------------------------

If your server hosts both Geotrek-Admin and Geotrek-Rando, you just have to configure Geotrek-Rando so
it uses the directory chosen above. Be sure nginx or apache will have access rights to read these data.

If you have to separate servers, you have to copy files, for example with `rsync` command.
