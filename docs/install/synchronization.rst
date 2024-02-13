.. _synchronization-section:

===============
Synchronization
===============

Manual synchronization
----------------------

To create data for Geotrek-rando (public web portal) and Geotrek-mobile (mobile phone app),
just run this command:

::

    sudo geotrek sync_rando /opt/geotrek-admin/var/data

The parameter is the destination directory for synchronized data.
If you choose another directory, make sure the parent of this directory is writable by geotrek user.
Otherwise you will get a PermissionError message.

If Geotrek-admin is not accessible on localhost:80, you have to use the ``--url`` option.
To make output less or more verbose, you can use the ``--verbose`` option.

Since version 2.4.0 of Geotrek-admin, you can also launch the command ``sync_rando`` from the web interface. 
You can add synchronization options with advanced configuration setting ``SYNC_RANDO_OPTIONS = {}``.

For example, if you add this line in ``/opt/geotrek-admin/var/conf/custom.py`` you will skip generation of map tiles files during the synchronisation :
``SYNC_RANDO_OPTIONS = {'skip_tiles': True}``


Automatic synchronization
-------------------------

You can set up automatic synchronization by creating a file ``/etc/cron.d/geotrek_sync`` that contains:

::

    0 3 * * * root /usr/sbin/geotrek sync_rando /opt/geotrek-admin/var/data

This example will automatically synchronize data a 3 am every day.

Note: it is required to give the full path to the geotrek command since cron set the PATH only to `bin:/usr/bin`.

Synchronization options
-----------------------

::

    Options:
      -v VERBOSITY, --verbosity=VERBOSITY
                            Verbosity level; 0=minimal output, 1=normal output,
                            2=verbose output
      -u URL, --url=URL     Base URL of Geotrek-admin (eg. http://geotrek.myorganization.com)
      -r URL, --rando-url=URL
                            Base URL of public Geotrek-rando website, used for static html versions of objects pages
                            generated for Facebook in meta folder of data API
      -s SOURCE, --source=SOURCE
                            Filter by source(s)
      -P PORTAL, --portal=PORTAL
                            Filter by portal(s)
      -p, --skip-pdf        Skip generation of PDF files
      -t, --skip-tiles      Skip generation of map tiles files for Geotrek-mobile app v2
      -d, --skip-dem        Skip generation of Digital Elevation Model files for 3D view
      -e, --skip-profile-png
                            Skip generation of PNG elevation profile
      -w, --with-touristicevents
                            Include touristic events by trek in global.zip for Geotrek-mobile v2
      -c CONTENT_CATEGORIES, --with-touristiccontent-categories=CONTENT_CATEGORIES
                            Include touristic contents by trek in global.zip for Geotrek-mobile v2
                            (filtered by category ID ex: --with-touristiccontent-categories="1,2,3")
      -g, --with-signages   Include published signages
      -i, --with-infrastructures
                            Include published infrastructures

Geotrek-mobile v3 uses its own synchronization command (see below). 
If you are not using Geotrek-mobile v2 anymore, it is recommanded to use ``-t`` option to don't generate big offline tiles directories, 
not used elsewhere than in Geotrek-mobile v2. Same for ``-w`` and ``-c`` option, only used for Geotrek-mobile v2.


Synchronization filtered by source and portal
---------------------------------------------

You can filter treks, touristic contents, touristic events and static pages by source(s). 
For example, if you created 3 sources records named ``source A``, ``source B`` and ``source C`` 
and you want to only export data from ``source A`` and ``source B`` to your web public portal, you can synchronize with:

::

    sudo geotrek sync_rando --source "source A,source B" dataAB

Multiple sources are separated with comas (without space before or after coma). Do not forget to add double quotes after and before the parameter 
if there are spaces in source names.
You can run several commands to export several sources combinations into several directories and use them to publish several distinct web portals.

You can do exactly the same with ``Target_Portal`` field value. It will include objects associated to the selected portal + those without portal.

::

    sudo geotrek sync_rando --portal "portal A" dataA


Synchronization filtered by touristic content categories
--------------------------------------------------------

In Geotrek-mobile v2, you can choose to also include touristic content per trek. You must specify ID categories :

::

    sudo geotrek sync_rando --with-touristiccontent-categories="1,3"

Multiple categories are separated with comas (without space before or after coma).


Synchronization with a distant Geotrek-rando server
---------------------------------------------------

If your server hosts both Geotrek-admin and Geotrek-rando, you just have to configure Geotrek-rando so
it uses the directory chosen above. Be sure NGINX or Apache will have access rights to read these data.

If you have separated servers, you have to copy files, for example with ``rsync`` command:

::

    rsync /path/of/generated/data other-server:/path/of/generated/data


Geotrek-mobile app v3
---------------------

The Geotrek-mobile app v3 has its own API and synchronization command called ``sync_mobile``.

It has similar parameters as ``sync_rando``:

::

    sudo geotrek sync_mobile [-h] [--languages LANGUAGES] [--portal PORTAL]
                           [--skip-tiles] [--url URL] [--indent INDENT]
                           [--version] [-v {0,1,2,3}] [--settings SETTINGS]
                           [--pythonpath PYTHONPATH] [--traceback]
                           [--no-color] [--force-color]
                           path
