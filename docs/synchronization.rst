===============
SYNCHRONIZATION
===============


Manual synchronization
----------------------

To create data for Geotrek-Rando (web public portal) and Geotrek-Mobile (mobile phone app),
just run this command:

::

    ./bin/django sync_rando /where/to/generate/data

The parameter is the destination directory for synchronized data.
If Geotrek-Admin is not accessible on localhost:80, you have to use the ``--url`` option.
To make output less or more verbose, you can use the ``--verbose`` option.

Since version 2.4.0 of Geotrek-admin, you can also launch the command ``sync_rando`` from the web interface. You can add synchronization options with advanced configuration setting ``SYNC_RANDO_OPTIONS = {}``.

Automatic synchronization
-------------------------

You can set up automatic synchronization by creating a file ``/etc/crond.d/geotrek_sync`` that contains:

::

    0 3 * * * root /path/to/geotrek/bin/django sync_rando /where/to/generate/data

This example will automatically synchronize data a 3 am every day.


Synchronization options
-----------------------

::

    Options:
      -v VERBOSITY, --verbosity=VERBOSITY
                            Verbosity level; 0=minimal output, 1=normal output,
                            2=verbose output
      -u URL, --url=URL     Base url of Geotrek-Admin (eg. http://geotrek.myorganization.com)
      -s SOURCE, --source=SOURCE
                            Filter by source(s)
      -P PORTAL, --portal=PORTAL
                            Filter by portal(s)
      -p, --skip-pdf        Skip generation of PDF files
      -t, --skip-tiles      Skip generation of map tiles files for mobile app
      -d, --skip-dem        Skip generation of Digital Elevation Model files for 3D view
      -w, --with-touristicevents
                            include touristic events by trek in global.zip
      -c CONTENT_CATEGORIES, --with-touristiccontent-categories=CONTENT_CATEGORIES
                            include touristic contents by trek in global.zip
                            (filtered by category ID ex: --with-touristiccontent-categories="1,2,3")


Synchronization filtered by source and portal
---------------------------------------------

You can filter treks, touristic contents, touristic events and static pages by source(s). For example, if you created 3 records sources named `source A`, `source B` and `source C` and you want only export data only from `source A` and `source B` to your web public portal, you can synchronize with:

::

    ./bin/django sync_rando --source "source A,source B" dataAB

Multiple sources are separated with comas (without space before or after coma). Do not forget to add double quotes after and before the parameter if there are spaces in source names.
You can run several commands to export several sources combinations into several directories and use them to publish several distinct web portals.

You can do exactly the same with Target_Portal filed value. 


::

    ./bin/django sync_rando --portal "portal A" dataA


Synchronization filtered by touristic content categories
--------------------------------------------------------

In Geotrek-mobile, you can choose to also include touristic content per trek. You must specify ID categories :

::

    ./bin/django sync_rando --with-touristiccontent-categories="1,3"

Multiple categories are separated with comas (without space before or after coma).


Synchronization with a distant Geotrek-Rando serveur
----------------------------------------------------

If your server hosts both Geotrek-Admin and Geotrek-Rando, you just have to configure Geotrek-Rando so
it uses the directory chosen above. Be sure nginx or apache will have access rights to read these data.

If you have separated servers, you have to copy files, for example with ``rsync`` command:

::

    rsync /path/of/generated/data other-server:/path/of/generated/data
