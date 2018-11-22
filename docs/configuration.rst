=============
CONFIGURATION
=============


Configuration update
--------------------

After editing ``.env``, refresh the running instance with :

::

    sudo systemctl restart geotrek


There a few cases where running ``install.sh`` would be necessary. If you
change the ``DOMAIN_NAME`` or other parameters that affect *nginx* site configuration.


Spatial extents
---------------

In order to check your configuration of spatial extents, a small tool
is available at http://server/tools/extents/.

:notes:

    Administrator privileges are required.


Custom spatial reference
------------------------

*Geotrek* comes with a few projection systems included (*EPSG:2154*, *EPSG:32600*,
*EPSG:32620*, *EPSG:32632*)

In order to use a specific projection system :

* Make sure the SRID is present in the ``spatial_ref_sys`` table. See PostGIS
  documentation to add new ones
* Download the JavaScript *proj4js* definition from `http://spatialreference.org`_
  and save it to `Geotrek/static/proj4js/<SRID>.js`

Using the command-line :

::

    curl "http://spatialreference.org/ref/epsg/<SRID>/proj4js/" > Geotrek/var/conf/extra_static/proj4js/<SRID>.js


:note:

    *Geotrek* won't run if the spatial reference has not a metric unit.

It's possible to store your data using a specific SRID, and use a classic
Google Maps projection (3857) in the Web interface (useful for *WMTS* or *OpenStreetMap* layers).
See :ref:`advanced configuration <advanced-configuration-section>`...


Users management
----------------

Geotrek relies on Django authentication and permissions system : Users belong to
groups and permissions can be assigned at user or group-level.

The whole configuration of user, groups and permissions is available in the *AdminSite*,
if you did not enable *External authent* (see below).

By default four groups are created :

* Readers
* Path managers
* Trek managers
* Editor

Once the application is installed, it is possible to modify the default permissions
of these existing groups, create new ones etc...

If you want to allow the users to access the *AdminSite*, give them the *staff*
status using the dedicated checkbox.


Database users
--------------

It is not safe to use the ``geotrek`` user in QGis, or to give its password to
many collaborators.

A wise approach, is to create a *read-only* user, or with specific permissions.

With *pgAdmin*, you can create database users like this :

::


    CREATE ROLE lecteur LOGIN;
    ALTER USER lecteur PASSWORD 'passfacile';
    GRANT CONNECT ON DATABASE geotrekdb TO lecteur;

And give them permissions by schema :

::

    GRANT USAGE ON SCHEMA public TO lecteur;
    GRANT USAGE ON SCHEMA geotrek TO lecteur;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO lecteur;
    GRANT SELECT ON ALL TABLES IN SCHEMA geotrek TO lecteur;


You can also create groups, etc. See postgresql documentation.


Email settings
--------------

Geotrek will send emails :

* to administrators when internal errors occur
* to managers when a feedback report is created

Email configuration takes place in ``var/conf/custom.py``, where you control
recipients emails (``ADMINS``, ``MAIL_MANAGERS``) and email server configuration.

Database server parameters and domain name take place in .env file

You can test you configuration with the following command. A fake email will
be sent to the managers :

::

    docker-compose run web ./manage.py test_managers_emails


Advanced Configuration
----------------------

See :ref:`advanced configuration <advanced-configuration-section>`...
