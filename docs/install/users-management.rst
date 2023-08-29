Users management
================

Users management in Geotrek-admin
---------------------------------

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

With *pgAdmin*, you can create database users like this:::

    CREATE ROLE lecteur LOGIN;
    ALTER USER lecteur PASSWORD 'passfacile';
    GRANT CONNECT ON DATABASE geotrekdb TO lecteur;

And give them permissions by schema:::

    GRANT USAGE ON SCHEMA public TO lecteur;
    GRANT USAGE ON SCHEMA geotrek TO lecteur;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO lecteur;
    GRANT SELECT ON ALL TABLES IN SCHEMA geotrek TO lecteur;

You can also create groups, etc. See PostgreSQL documentation.
