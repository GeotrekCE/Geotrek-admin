=============
Configuration
=============


Basic configuration update
--------------------------

To update basic configuration (server name, database connection, languages, or set workers number or timeout), run:

::

    sudo dpkg-reconfigure geotrek-admin

The basic configuration is stored in ``/opt/geotrek-admin/var/conf/env`` file, not to be changed manually.
This file also contains the PostgreSQL authentification details, if you need to access your Geotrek-admin database.


NGINX configuration
-------------------

NGINX configuration is controlled by Geotrek-admin and will be erased at each upgrade.
Do not modify ``/etc/nginx/sites-available/geotrek.conf`` or ``/etc/nginx/sites-enable/geotrek.conf``.
Modify ``/opt/geotrek-admin/var/conf/nginx.conf.in`` instead. To update ``nginx.conf``, then run:

::

    sudo dpkg-reconfigure geotrek-admin


Activate SSL / HTTPS
--------------------

To activate https, you need firstly to change custom.py and add :

::

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

After this, edit `nginx.conf.in` to add your certificate.

If you generate it with letsencrypt :
You can use certbot to add the certificate in your configuration.
But you will have to move the configuration automatically added into `nginx.conf`, to the file `nginx.conf.in`
in `/opt/geotrek-admin/var/conf/` directory

You have to move the configuration to the file `nginx.conf.in` because `nginx.conf` is automatically
changed during command `dpkg-reconfigure geotrek-admin`.


Users management
----------------

Geotrek-admin relies on Django authentication and permissions system. Users belong to
groups. Permissions can be assigned at user or group-level.

The whole configuration of users, groups and permissions is available in the *AdminSite*,
if you did not enable *External authent* (see below).

By default six groups are created:

* Readers ("Lecteurs")
* Path managers ("Référents sentiers")
* Trek managers ("Référents communication")
* Editors ("Rédacteurs")
* Geotrek-rando ("Geotrek-rando")
* Trek and management editors ("Rédacteurs rando et gestion")

Once the application is installed, it is possible to modify the default permissions
of these existing groups, create new ones etc...

If you want to allow the users to access the *AdminSite*, give them the *staff*
status using the dedicated checkbox. The *AdminSite* allows users to edit data categories such as *trek difficulty levels*, *POI types*, etc.

Permissions fall into four main types of actions:
* add
* change
* delete
* visualization

Each data type is at least associated with the four basic actions (*add*, *change*, *delete*, *read*). One data type corresponds to  a database table (*signage_signage*, *trekking_trek*...)

Here is the signification of actions allowed through permissions:
* *view*: see the data in Django *AdminSite* (for data of "category" type such as POI types, or difficulty level)
* *read*: see the data in Geotrek-admin interface (button and data list)
* *add*: adding of a new data (trek, theme...)
* *change*: modify the data
* *change_geom*: modify the data geometry
* *publish*: publish the data
* *export*: export the data thrgough Geotrek-admin interface (CSV, JSON...)


Database users
--------------

It is not safe to use the ``geotrek`` user in QGIS, or to give its password to
many collaborators.

A wise approach, is to create a *read-only* user, or with specific permissions.

With *pgAdmin*, you can create database users like this:

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


You can also create groups, etc. See PostgreSQL documentation.


Advanced Configuration
----------------------

See :ref:`advanced configuration <advanced-configuration-section>`...
