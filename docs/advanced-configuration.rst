.. _advanced-configuration-section:

======================
ADVANCED CONFIGURATION
======================

Custom setting file (no-docker)
-------------------------------

Geotrek basic configuration is currently restricted to values present in ``etc/settings.ini``.

However, it is possible to write a custom Django setting file to override all default values from ``geotrek/settings/base.py`` file.

* Create your a file in *geotrek/settings/custom.py* with the following content :

.. code-block :: python

    # coding: utf8

    from .prod import *

    # My custom value
    HIDDEN_OPTION = 3.14

* Add this ``etc/settings.ini`` to specify the newly created setting :

.. code-block :: ini

    [django]
    settings = settings.custom

* As for any change in ``etc/settings.ini``, re-run ``make env_standalone deploy``. To apply changes in ``geotrek/settings/custom.py``, you can just restart the application with ``sudo supervisorctl restart all``.

Custom setting file (docker)
----------------------------

* Modify your file *var/conf/custom.py* with the following content :

* Re-run ``docker-compose run --rm web update.sh``. To apply changes in ``var/conf/custom.py``, you can just restart the application with ``sudo systemctl restart geotrek``.


Disable modules and components
------------------------------

In order to disable a full set of features, in the custom settings file,
add the following code:

.. code-block :: python

    # Disable infrastructure and maintenance
    _INSTALLED_APPS = list(INSTALLED_APPS)
    _INSTALLED_APPS.remove('geotrek.infrastructure')
    _INSTALLED_APPS.remove('geotrek.maintenance')
    INSTALLED_APPS = _INSTALLED_APPS

In order to remove notion of trails:

.. code-block :: python

    TRAIL_MODEL_ENABLED = False

In order to remove zoning combo-boxes on list map:

.. code-block :: python

    LAND_BBOX_CITIES_ENABLED = True
    LAND_BBOX_DISTRICTS_ENABLED = True
    LAND_BBOX_AREAS_ENABLED = False

:notes:

    By doing so, some software upgrades may not be as smooth as usual.
    Never forget to mention this customization if you ask for community support.


Sensitive areas
----------------------


In order to enable sensitivity module, in the custom settings file,
add the following code:

.. code-block :: python

    # Enable sensitivity module
    INSTALLED_APPS += ('geotrek.sensitivity', )

The following settings are related to sensitive areas:

.. code-block :: python

    # Default radius of sensitivity bubbles when not specified for species
    SENSITIVITY_DEFAULT_RADIUS = 100  # meters

    # Buffer around treks to intersects sensitive areas
    SENSITIVE_AREA_INTERSECTION_MARGIN = 500  # meters


Diving
------

In order to enable diving module, in the custom settings file,
add the following code:

.. code-block :: python

    # Enable diving module
    INSTALLED_APPS += ('geotrek.diving', )


WYSIWYG editor configuration
----------------------------

Text form fields are enhanced using `TinyMCE <http://tinymce.com>`_.

Its configuration can be customized using advanced settings (see above paragraph).

For example, in order to control which buttons are to be shown, and which tags
are to be kept when cleaning-up, add this bloc :

.. code-block :: python

    TINYMCE_DEFAULT_CONFIG = {
        'theme_advanced_buttons1': 'bold,italic,forecolor,separator,code',
        'valid_elements': "img,p,a,em/i,strong/b",
    }

This will apply to all text fields.

For more information on configuration entries available, please refer to the
official documentation of *TinyMCE version 3*.


View attachments in the browser
-------------------------------

Attached files are downloaded by default by browser, with the following line,
files will be opened in the browser :

.. code-block :: python

    MAPENTITY_CONFIG['SERVE_MEDIA_AS_ATTACHMENT'] = False


Change or add WMTS tiles layers (IGN, OSM, Mapbox...)
-----------------------------------------------------

By default, you have 2 basemaps layers in your Geotrek-admin (OSM and OSM black and white). 

You can change or add more basemaps layers.

Specify the tiles URLs this way in your custom Django setting file:

.. code-block :: python

    LEAFLET_CONFIG['TILES'] = [
        ('OSM', 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', u'© OpenStreetMap Contributors'),
        ('OpenTopoMap', 'http://a.tile.opentopomap.org/{z}/{x}/{y}.png', u'Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)'),
    ]

Example with IGN and OSM basemaps : 

.. code-block :: python

    LEAFLET_CONFIG['TILES'] = [
        ('IGN Scan', '//wxs.ign.fr/YOURAPIKEY/wmts?LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS&EXCEPTIONS=text/xml&FORMAT=image/jpeg&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}', u'© IGN Geoportail'),
        ('IGN Scan Express', '//wxs.ign.fr/YOURAPIKEY/wmts?LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN-EXPRESS.STANDARD&EXCEPTIONS=text/xml&FORMAT=image/jpeg&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}', u'© IGN Geoportail'),
        ('IGN Ortho', '//wxs.ign.fr/YOURAPIKEY/wmts?LAYER=ORTHOIMAGERY.ORTHOPHOTOS&EXCEPTIONS=text/xml&FORMAT=image/jpeg&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}', u'© IGN Geoportail'),
        ('IGN Cadastre', '//wxs.ign.fr/YOURAPIKEY/wmts?LAYER=CADASTRALPARCELS.PARCELS&EXCEPTIONS=text/xml&FORMAT=image/png&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=bdparcellaire_o&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}', u'© IGN Geoportail'),
        ('OSM', 'https//{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', u'© OpenStreetMap contributors'),
        ('OSM Stamen Terrain', '//tile.stamen.com/terrain/{z}/{x}/{y}.jpg', u'© OpenStreetMap contributors / Stamen Design'),
        ('OpenTopoMap', 'https//a.tile.opentopomap.org/{z}/{x}/{y}.png', u'Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)')
    ]

To use IGN Geoportail WMTS tiles API, you need an API key with subscribing on http://professionnels.ign.fr/visualisation. Choose WebMercator WMTS tiles.

External authent
----------------

You can authenticate user against a remote database table or view. 

To enable this feature, fill *authent_dbname* and other fields in ``etc/settings.ini``.

Expected columns in table/view are :

* username : string (*unique*)
* first_name : string
* last_name : string
* password : string (simple md5 encoded, or full hashed and salted password)
* email : string
* level : integer (1: readonly, 2: redactor, 3: path manager, 4: trekking manager, 6: administrator)
* structure : string
* lang : string (language code)

:notes:

    The schema used in ``authent_tablename`` must be in the user search_path (``ALTER USER $geotrek_db_user SET search_path=public,userschema;``)
    
    User management will be disabled from Administration backoffice.

    In order to disable remote login, just remove *authent_dbname* value in settings
    file, and update instance (see paragraph above).

    Geotrek can support many types of users authentication (LDAP, oauth, ...), contact us
    for more details.


Map layers colors and style
---------------------------

All layers colors can be customized from the settings.
See `Leaflet reference <http://leafletjs.com/reference.html#path>`_ for vectorial
layer style.

* To apply these style changes, re-run ``sudo supervisorctl restart all``.

.. code-block :: python

    MAP_STYLES['path'] = {'color': 'red', 'weight': 5}

Or change just one parameter (the opacity for example) :

.. code-block :: python

    MAP_STYLES['city']['opacity'] = 0.8


Regarding colors that depend from database content, such as land layers
(physical types, work management...) or restricted areas. We use a specific
setting that receives a list of colors :

.. code-block :: python

    COLORS_POOL['restrictedarea'] = ['#ff00ff', 'red', '#ddddd'...]


See the default values in ``geotrek/settings/base.py`` for the complete list
of available styles.

**Restart** the application for changes to take effect.


External raster layers
----------------------

It is possible to add overlay tiles layer on maps. For example, it can be useful to:

* Get the cadastral parcels on top of satellite images
* Home made layers (*with Tilemill or QGisMapserver for example*).
  Like the park center borders, traffic maps, IGN BDTopo® or even the Geotrek paths
  that are marked as invisible in the database!

In ``custom.py``, just add the following lines:

.. code-block :: python

    LEAFLET_CONFIG['OVERLAYS'] = [
        ('Coeur de parc', 'http://serveur/coeur-parc/{z}/{x}/{y}.png', '&copy; PNF'),
    ]


Expected properties
~~~~~~~~~~~~~~~~~~~

For ``GeoJSON`` files, you can provide the following properties :

* ``title``: string
* ``description``: string
* ``website``: string
* ``phone``: string
* ``pictures``: list of objects with ``url`` and ``copyright`` attributes
* ``category``: object with ``id`` and ``label`` attributes


Disable darker map backgrounds
------------------------------

Since IGN map backgrounds are very dense and colourful, a dark opacity is
applied. In order to disable, change this MapEntity setting :

.. code-block:: python

    MAPENTITY_CONFIG['MAP_BACKGROUND_FOGGED'] = False

  
Override translations
---------------------------------

**Without Docker**

You can override default translation files available in each module (for example those from trekking module available in ``<geotrek-admin-folder>/geotrek/trekking/locale/fr/LC_MESSAGES/django.po``).

Don't edit these default files, use them to find which words you want to override.

Create the custom translations destination folder:

::

     cd  <geotrek-admin-folder>/geotrek/
     mkdir -p locale/en/LC_MESSAGES

Then create a ``django.po`` file in this directory. You can do one folder and one ``django.po`` file for each language (example  ``<geotrek-admin-folder>/geotrek/locale/fr/LC_MESSAGES/django.po`` for French translation overriding)

**With Docker**

Override translations by creating a destination folder:

::

    mkdir -p var/conf/extra_locale/en/LC_MESSAGES
    editor var/conf/extra_locale/en/LC_MESSAGES/django.po

**With and without Docker**

Override the translations that you want in these files.

Example of content for the French translation overriding:

::

    # MY FRENCH CUSTOM TRANSLATION
    # Copyright (C) YEAR THE PACKAGE'S COPYRIGHT HOLDER
    # This file is distributed under the same license as the PACKAGE package.
    # FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
    #
    msgid ""
    msgstr ""
    "Report-Msgid-Bugs-To: \n"
    "POT-Creation-Date: 2018-11-15 15:32+0200\n"
    "PO-Revision-Date: 2018-11-15 15:33+0100\n"
    "Last-Translator: \n"
    "Language-Team: LANGUAGE <LL@li.org>\n"
    "MIME-Version: 1.0\n"
    "Content-Type: text/plain; charset=UTF-8\n"
    "Content-Transfer-Encoding: 8bit\n"
    "Project-Id-Verésion: PACKAGE VERSION\n"
    "Plural-Forms: nplurals=2; plural=(n > 1);\n"
    "Project-Id-Version: \n"
    "X-Generator: Poedit 1.5.4\n"
      
    msgid "City"
    msgstr "Région"

    msgid "District"
    msgstr "Pays"


**Without Docker**

Apply changes : 

::

    cd <geotrek-admin-folder>
    make env_standalone deploy

**With Docker**

Apply changes :

::

    cd <geotrek-admin-folder>
    docker-compose run --rm web update.sh


Override public pdf templates
-----------------------------



PDF are generated from html printed, using [Django templating](https://docs.djangoproject.com/en/1.11/ref/templates/).
Trekkings, touristic contents and events can be exported in pdf files.

- Treks : ``geotrek/trekking/templates/trekking/trek_public_pdf.html``
- touristic contents : ``geotrek/tourism/templates/tourism/touristiccontent_public_pdf.html``
- touristic events : ``geotrek/tourism/templates/tourism/touristiccontent_public_pdf.html``

**Without Docker**

Overriden templates have to be located in ``var/media/templates/<appname>``, with appname = trekking or tourism.
To override trekking pdf for example, copy the file ``geotrek/trekking/templates/trekking/trek_public_pdf.html``
to ``var/media/templates/trekking/trek_public_pdf.html``.

**Without Docker**
Override templates

- Treks : ``var/conf/extra_templates/trekking/trek_public_pdf.html``
- touristic contents : ``var/conf/extra_templates/tourism/touristiccontent_public_pdf.html``
- touristic events : ``var/conf/extra_templates/tourism/touristiccontent_public_pdf.html``

For any examples :  https://github.com/GeotrekCE/Geotrek-admin/tree/master/geotrek/<app>/templates/<app>


These templates derive from base templates, which content is organized in blocks.
To override for example the description block of trek pdf, copy and change the ``{% block description }…{% endblock description %}``
in your ``var/media/templates/trekking/trek_public_pdf.html``.

It is also possible to use color defined for practice for pictogram by adding in your
``geotrek/trekking/templates/trekking/trek_public_pdf.html`` file :

::

    {% block picto_attr %}style="background-color: {{ object.practice.color }};"{% endblock picto_attr %}

CSS can be overriden like html templates : copy them to ``var/media/templates/trekking/`` or ``var/media/templates/tourism/`` folder

.. note ::

    The default template may change in the future versions. You will be
    in charge of porting the modification to your copy.

Test your modifications by exporting a trek or a content to pdf from Geotrek-admin application.
To get your modifications available for Rando application, launch the ``sync_rando`` command.


Custom font in public document template
----------------------------------------

In order to use custom fonts in trek PDF, it is necessary to install the
font files on the server.

*Microsoft* fonts like *Arial* and *Verdana* can be installed via the package
manager ::

    sudo apt-get install ttf-mscorefonts-installer

For specific fonts, copy the ``.ttf`` (or ``.otf``) files into the folder
``/usr/local/share/fonts/custom/`` as root, and run the following command ::

    fc-cache

For more information, check out Ubuntu documentation.


Custom colors in public document template
-----------------------------------------

Trek export geometries are translucid red by default. In order to control the
apparence of objects in public trek exports, use the following setting :

::

    MAP_STYLES['print']['path'] = {'weight': 3}

See *Leaflet* reference documentation for detail about layers apparence.

Primary color in PDF templates
------------------------------

You can override `PRIMARY_COLOR` to change emphase text in PDF export.
Beware of contrast, colour is used for text so we advise you to avoid light colour.

Custom logos
------------

**Without Docker**

You might also need to deploy logo images in the following places :

* ``var/media/upload/favicon.png``
* ``var/media/upload/logo-login.png``
* ``var/media/upload/logo-header.png``

**With Docker**

You might also need to deploy logo images in the following places :

* ``var/conf/extra_static/images/favicon.png``
* ``var/conf/extra_static/images/logo-login.png``
* ``var/conf/extra_static/images/logo-header.png``

Share services between several Geotrek instances
------------------------------------------------

As explained :ref:`in the design section <design-section>`, *Geotrek* relies
on several services. They are generic and reusable, and can thus be shared
between several instances, in order to save system resources for example.

A simple way to achieve this is to install one instance with everything
as usual (*standalone*), and plug the other instances on its underlying services.


Database
~~~~~~~~

Sharing your postgreSQL server is highly recommended. Create several databases
for each of your instances.


Then in ``etc/settings.ini`` (no-docker) or ``.env`` (docker), adjust the ``host`` and ``dbname`` sections of
each instance.


Capture and conversion (without docker)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On the standalone server, make sure the services will be available to others.
Add the following lines in its ``settings.ini`` :

.. code-block:: python

    [convertit]
    host = 0.0.0.0

    [screamshotter]
    host = 0.0.0.0

In ``custom.py``, point the tiles URL to the shared services (replace ``SERVER`` by
the one you installed as standalone) :

.. code-block :: python

    MAPENTITY_CONFIG['CONVERSION_SERVER'] = 'http://SERVER:6543'
    MAPENTITY_CONFIG['CAPTURE_SERVER'] = 'http://SERVER:8001'


Shutdown useless services (without docker)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that your instances point the shared server. You can shutdown the useless
services on each instance.

Start by stopping everything :

::

    sudo stop geotrek

Before you used to run ``make env_standalone deploy`` on every server.
Now you will have only one *standalone*, and on the other ones
the *Geotrek* application only.

To achieve this, you will just have to run the *prod* environment instead
of *standalone* in the deployment procedure (*or when settings are changed*) :

::

    make env_prod deploy


Control number of workers and request timeouts
----------------------------------------------

**Without Docker**

By default, the application runs on 4 processes, and timeouts after 30 seconds.

To control those values, add a section in ``etc/settings.ini`` for each running service.
See ``conf/settings-defaults.cfg`` for an exhaustive list:

::

    [gunicorn-app-conf]
    workers = 4
    timeout = 30

To know how many workers you should set, please refer to `gunicorn documentation <http://gunicorn-docs.readthedocs.org/en/latest/design.html#how-many-workers>`_.


**With Docker**

By default, the application runs on 5 processes, and timeouts after 600 seconds.
Change the args in your ``.env``

::

    GUNICORN_CMD_ARGS=--bind=0.0.0.0:8000 --workers=5 --timeout=600



To know how many workers you should set, please refer to `gunicorn documentation <http://gunicorn-docs.readthedocs.org/en/latest/design.html#how-many-workers>`_.
