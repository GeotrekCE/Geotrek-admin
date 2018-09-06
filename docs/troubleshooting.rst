.. _troubleshooting-section:

===============
TROUBLESHOOTING
===============

Installation outputs a lot of database FATAL ERROR
--------------------------------------------------

Data schema migrations code do not inspect the database before executing commands.
When appropriate, errors are skipped in python code, but PostgreSQL error output still
remains.

http://south.aeracode.org/ticket/1247

Installation script hangs on syncdb --migrate
---------------------------------------------

This command is in charge of changing the database schema [1].

Make sure you close every *pgADMIN* session on the database while upgrading.

[1] http://south.aeracode.org/ticket/209


No paths in list, where table contains records
----------------------------------------------

Check that the projection of your data is correct.

Check that the extent of the map covers your data, using the extents tool
at *http://server/tools/extents/*.


No background tiles
-------------------

Check the values of your WMS settings (server name should end with ``?``, layers names should exist on server).


Error at loading DEM
--------------------

Check that your extent (``spatial_extent``) is completely contained in your DEM.


502 Bad Gateway
---------------

If the application does not show up (``502 Bad Gateway``), make sure the Geotrek
services run with the following commands :

::

    sudo systemctl status

You may want to force their restart :

::

    sudo systemctl restart geotrek


If they don't stay alive, check the log files in the ``var/log/`` folder.
It might come from a configuration problem.
