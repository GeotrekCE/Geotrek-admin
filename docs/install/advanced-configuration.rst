.. _advanced-configuration-section:

======================
Advanced configuration
======================

Custom setting file
-------------------

Geotrek-admin advanced configuration is done in ``/opt/geotrek-admin/var/conf/custom.py`` file.
The list of all overridable setting and default values can be found
`there <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/settings/base.py>`_.

After any change in ``custom.py``, run:

::

    sudo service geotrek restart

Sometimes you also have to run:

::

    sudo dpkg-reconfigure -u geotrek-admin

.. note ::

    Don't override the ``os.getenv()`` settings as they are managed with Basic configuration.


Application settings
--------------------

Spatial extents
~~~~~~~~~~~~~~~

In order to check your configuration of spatial extents, a small tool
is available at http://server/tools/extents/.

.. note ::

    Administrator privileges are required.


Email settings
~~~~~~~~~~~~~~

Geotrek-admin will send emails:

* to administrators when internal errors occur
* to managers when a feedback report is created

Email configuration takes place in ``/opt/geotrek-admin/var/conf/custom.py``, where you control
recipients emails (``ADMINS``, ``MANAGERS``) and email server configuration.

Set configuration settings in ``geotrek/settings/custom.py.dist`` template file.

You can test your configuration with the following command. A fake email will
be sent to the managers:

::

    sudo geotrek sendtestemail --managers


Swagger API documentation
~~~~~~~~~~~~~~~~~~~~~~~~~

In order to enable swagger module to auto-document API ``/api/v2/``, in the custom settings file,
add the following code:

.. code-block :: python

    # Enable API v2 documentation
    INSTALLED_APPS += ('drf_yasg', )

Then run ``sudo dpkg-reconfigure -u geotrek-admin``.

Share services between several Geotrek instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As explained :ref:`in the design section <design-section>`, *Geotrek-admin* relies
on several services. They are generic and reusable, and can thus be shared
between several instances, in order to save system resources for example.

A simple way to achieve this is to install one instance with everything
as usual (*standalone*), and plug the other instances on its underlying services.


Capture and conversion
''''''''''''''''''''''

If you want to use external services, in ``.env``, add following variables:

.. code-block :: bash

    CAPTURE_HOST=x.x.x.x
    CAPTURE_PORT=XX
    CONVERSION_HOST=x.x.x.x
    CONVERSION_PORT=XX

Then, you can delete all screamshotter and convertit references in ``docker-compose.yml``.


Shutdown useless services
'''''''''''''''''''''''''

Now that your instances point the shared server. You can shutdown the useless
services on each instance.

Start by stopping everything :

::

    sudo systemctl stop geotrek


Control number of workers and request timeouts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, the application runs on 4 processes, and timeouts after 30 seconds.

To control those values, edit and fix your ``docker-compose.yml`` file in web and api section.

To know how many workers you should set, please refer to `gunicorn documentation <http://gunicorn-docs.readthedocs.org/en/latest/design.html#how-many-workers>`_.


External authent
~~~~~~~~~~~~~~~~

You can authenticate user against a remote database table or view.

To enable this feature, fill these fields in ``/opt/geotrek-admin/var/conf/custom.py``:

::

    AUTHENT_DATABASE = 'authent'
    DATABASES['authent'] = {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': '<database name>',
        'USER': '<user name>',
        'PASSWORD': '<password>',
        'HOST': '<host>',
        'PORT': '<port>',
    }
    AUTHENT_TABLENAME = '<table name>'
    AUTHENTICATION_BACKENDS = ['geotrek.authent.backend.DatabaseBackend']

Expected columns in table/view are :

* username : string (*unique*)
* first_name : string
* last_name : string
* password : string (simple md5 encoded, or full hashed and salted password)
* email : string
* level : integer (1: readonly, 2: redactor, 3: path manager, 4: trekking manager, 5: management and trekking editor, 6: administrator)
* structure : string
* lang : string (language code)

.. note ::

    The schema used in ``AUTHENT_TABLENAME`` must be in the user search_path (``ALTER USER $geotrek_db_user SET search_path=public,userschema;``)

    User management will be disabled from Administration backoffice.

    In order to disable remote login, just comment *AUTHENTICATION_BACKENDS* line in settings
    file, and restart instance (see paragraph above).

    Geotrek-admin can support many types of users authentication (LDAP, oauth, ...), contact us
    for more details.


Map settings
------------

Change or add WMTS tiles layers (IGN, OSM, Mapbox…)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, you have 2 basemaps layers in your Geotrek-admin (OSM and OSM black and white).

You can change or add more basemaps layers.

Specify the tiles URLs this way in your custom Django setting file:

.. code-block :: python

    LEAFLET_CONFIG['TILES'] = [
        ('OSM', 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', '© OpenStreetMap Contributors'),
        ('OpenTopoMap', 'http://a.tile.opentopomap.org/{z}/{x}/{y}.png', 'Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)'),
    ]

Example with IGN and OSM basemaps :

.. code-block :: python

    LEAFLET_CONFIG['TILES'] = [
        ('IGN Scan', '//wxs.ign.fr/YOURAPIKEY/wmts?LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS&EXCEPTIONS=image/jpeg&FORMAT=image/jpeg&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}', '© IGN Geoportail'),
        ('IGN Plan V2', '//wxs.ign.fr/essentiels/geoportail/wmts?LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2&EXCEPTIONS=image/png&FORMAT=image/png&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}', '© IGN Geoportail'),
        ('IGN Ortho', '//wxs.ign.fr/essentiels/geoportail/wmts?LAYER=ORTHOIMAGERY.ORTHOPHOTOS&EXCEPTIONS=image/jpeg&FORMAT=image/jpeg&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}', '© IGN Geoportail'),
        ('IGN Cadastre', '//wxs.ign.fr/essentiels/geoportail/wmts?LAYER=CADASTRALPARCELS.PARCELLAIRE_EXPRESS&EXCEPTIONS=image/jpeg&FORMAT=image/png&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=bdparcellaire_o&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}', '© IGN Geoportail'),
        ('OSM', 'https//{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', '© OpenStreetMap contributors'),
        ('OSM Stamen Terrain', '//tile.stamen.com/terrain/{z}/{x}/{y}.jpg', '© OpenStreetMap contributors / Stamen Design'),
        ('OpenTopoMap', 'https//a.tile.opentopomap.org/{z}/{x}/{y}.png', 'Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)')
    ]

To use some IGN Geoportail WMTS tiles (Scan25, Scan100, etc.), you may need an API key. You can find more information about this on https://geoservices.ign.fr/services-web-issus-des-scans-ign.

Map layers colors and style
~~~~~~~~~~~~~~~~~~~~~~~~~~~

All layers colors can be customized from the settings.
See `Leaflet reference <http://leafletjs.com/reference.html#path>`_ for vectorial
layer style.

* To apply these style changes, re-run ``sudo systemctl restart geotrek``.

.. code-block :: python

    MAPENTITY_CONFIG['MAP_STYLES']['path'] = {'color': 'red', 'weight': 5}

Or change just one parameter (the opacity for example) :

.. code-block :: python

    MAPENTITY_CONFIG['MAP_STYLES']['city']['opacity'] = 0.8


Regarding colors that depend from database content, such as land layers
(physical types, work management...) or restricted areas. We use a specific
setting that receives a list of colors :

.. code-block :: python

    COLORS_POOL['restrictedarea'] = ['#ff00ff', 'red', '#ddddd'...]


See the default values in ``geotrek/settings/base.py`` for the complete list
of available styles.

**Restart** the application for changes to take effect.


External raster layers
~~~~~~~~~~~~~~~~~~~~~~

It is possible to add overlay tiles layer on maps. For example, it can be useful to:

* Get the cadastral parcels on top of satellite images
* Home made layers (*with Tilemill or QGisMapserver for example*).
  Like the park center borders, traffic maps, IGN BDTopo® or even the Geotrek paths
  that are marked as invisible in the database!

In ``custom.py``, just add the following lines:

.. code-block :: python

    LEAFLET_CONFIG['OVERLAYS'] = [
        ('Cadastre', '//wxs.ign.fr/essentiels/geoportail/wmts?LAYER=CADASTRALPARCELS.PARCELLAIRE_EXPRESS&EXCEPTIONS=image/jpeg&FORMAT=image/png&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}', '&copy; IGN - GeoPortail')
        ('Coeur de parc', 'http://serveur/coeur-parc/{z}/{x}/{y}.png', '&copy; PNF'),
    ]


**Expected properties:**

For ``GeoJSON`` files, you can provide the following properties :

* ``title``: string
* ``description``: string
* ``website``: string
* ``phone``: string
* ``pictures``: list of objects with ``url`` and ``copyright`` attributes
* ``category``: object with ``id`` and ``label`` attributes


Disable darker map backgrounds
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since IGN map backgrounds are very dense and colourful, a dark opacity is
applied. In order to disable, change this MapEntity setting :

.. code-block :: python

    MAPENTITY_CONFIG['MAP_BACKGROUND_FOGGED'] = False


Modules and components
----------------------

In order to disable a full set of modules, in the custom settings file,
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

.. note ::

    By doing so, some software upgrades may not be as smooth as usual.
    Never forget to mention this customization if you ask for community support.


Diving
~~~~~~

In order to enable diving module, in the custom settings file,
add the following code:

.. code-block :: python

    # Enable diving module
    INSTALLED_APPS += ('geotrek.diving', )

Then run ``sudo dpkg-reconfigure -pcritical geotrek-admin``.

You can also insert diving minimal data (default practices, difficulties, levels and group permissions values):

::

    sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/diving/fixtures/basic.json
    cp /opt/geotrek-admin/lib/python*/site-packages/geotrek/diving/fixtures/upload/* /opt/geotrek-admin/var/media/upload/

You can insert licenses of attachments with this command :

::

    sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/common/fixtures/licenses.json


Outdoor
~~~~~~~

In order to enable Outdoor module, in the custom settings file,
add the following code:

.. code-block :: python

    # Enable Outdoor module
    INSTALLED_APPS += ('geotrek.outdoor', )

Then run ``sudo dpkg-reconfigure -pcritical geotrek-admin``.

You can also insert Outdoor minimal data:

::

    sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/outdoor/fixtures/basic.json

After installing Outdoor module, you have to add permissions to your user groups on outdoor sites and courses.

Note: Outdoor module is not compatible with PostGIS <= 2.4 that is included in Ubuntu 18.04.
You should either upgrade to Ubuntu 20.04 or upgrade postGIS to 2.5 with
https://launchpad.net/~ubuntugis/+archive/ubuntu/ppa

Sensitive areas
~~~~~~~~~~~~~~~

In order to enable sensitivity module, in the custom settings file,
add the following code:

.. code-block :: python

    # Enable sensitivity module
    INSTALLED_APPS += ('geotrek.sensitivity', )

See `sensitivity section <./sensitivity.html>`_ for settings and imports.

Feedback reports settings
-------------------------

Send acknowledge email
~~~~~~~~~~~~~~~~~~~~~~

::

    SEND_REPORT_ACK = True

If false, no email will be sent to the sender of any feedback on Geotrek-rando website


Suricate support
~~~~~~~~~~~~~~~~

Geotrek reports can work together with Suricate API, using one of 3 modes. Proceed through a mode full configuration before proceeding to the next mode.

**1** - No Suricate (default)

This mode sends no report data to Suricate. 

To initialize Report forms (Geotrek-admin, Geotrek-rando-v2, Geotrek-rando-v3) load lists for categories, activities, statuses and problem magnitude:

.. code-block :: python

    geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/feedback/fixtures/basic.json

To make these lists available for your Geotrek-rando-v2, run ``sync_rando`` (see :ref:`synchronization <synchronization-section>`)


**2** - Suricate Standard

This mode simply forwards all reports to Suricate, using the Standard API to post reports.

Set your account settings in ``custom.py``:

.. code-block :: python

    SURICATE_REPORT_ENABLED = True

    SURICATE_REPORT_SETTINGS = {
        'URL': '<Suricate Standard API Url>',
        'ID_ORIGIN': '<Suricate origin ID>',
        'PRIVATE_KEY_CLIENT_SERVER': '<your private key client / server>',
        'PRIVATE_KEY_SERVER_CLIENT': '<your private key server / client>',
    }

**3** - Suricate Management (Workflow)

This mode allows to retrieve reports and related data directly from Suricate, using the Management API to get data. It is used to process and manage reports, using the Intervention module and following a predefined worklow, while sending all progress to Suricate. It implies enabling Suricate Report mode as well.
You can find a detailled explanation on the workflow here : https://github.com/GeotrekCE/Geotrek-admin/issues/2366#issuecomment-1113435035

- Set your settings in ``custom.py`` :

.. code-block :: python

    SURICATE_WORKFLOW_ENABLED = True

    SURICATE_MANAGEMENT_SETTINGS = {
        'URL': '<Suricate Management API Url>',
        'ID_ORIGIN': '<Suricate origin ID>',
        'PRIVATE_KEY_CLIENT_SERVER': '<your private key client / server>',
        'PRIVATE_KEY_SERVER_CLIENT': '<your private key server / client>',
    }

    SURICATE_WORKFLOW_SETTINGS = {
        "SURICATE_RELOCATED_REPORT_MESSAGE": "This report is not located in Workflow responsiblity area.",
        "SKIP_MANAGER_MODERATION": False
    }

You can use the following command to test your connection settings:

.. code-block :: python

    geotrek sync_suricate -v 2 --connection-test

Load lists for activities and/or report statuses from Suricate:

.. code-block :: python

    geotrek sync_suricate --activities --statuses -v 2

Load alerts from Suricate (located in your bounding box) :

.. code-block :: python

    geotrek sync_suricate -v 2 --no-notification

To make these lists available for your Geotrek-rando, run ``sync_rando`` (see :ref:`synchronization <synchronization-section>`)

- Then load extra required statuses for Reports and Interventions:

.. code-block :: python

    geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/feedback/fixtures/management_workflow.json
    geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/maintenance/fixtures/basic.json

- Go to the Admin Site and 
    - if you want to include the moderation steps (`SKIP_MANAGER_MODERATION = False`), select a user as Workflow Manager (`/admin/feedback/workflowmanager/`). Their role is to assign reports to other users.
    - select a district as Workflow District (`/admin/feedback/workflowdistrict/`). This zone defines the area of reponsibility for reports. Reports relocated outside of the district will be excluded from workflow.
    - create predefined emails (`/admin/feedback/predefinedemail/`) to notify Suricate Sentinels and Administrators. You can use `##intervention_date##` and `##supervisor##` in the messages' body to automatically replace with the report's linked Intervention date and author. The Extended Username field will be dsiplayed (see User Profile under `/admin/auth/user/`).
    - make sure Users involved in the workflow have proper permissions to create and update Reports and Interventions (`/admin/auth/user/`)

Be aware that, when enabling Suricate Management mode, Suricate becomes the master database for reports. This means **reports created in Geotrek-admin will not be saved to the database, they will only be sent to Suricate**. Reports are only saved when synchronized back from Suricate, when the synchronization command is run. Make sure to run these 3 commands daily to maintain synchronization and update reports (thanks to `cron` for instance) :

.. code-block :: python

    geotrek retry_failed_requests_and_mails
    geotrek check_timers
    geotrek sync_suricate


Display reports with status defined colors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block :: python

    ENABLE_REPORT_COLORS_PER_STATUS = True
 
Go to the Admin Site and select colors to display for each status (`/admin/feedback/reportstatus/`).


Use timers to receive alerts for your reports
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is possible to enable receiving email alerts for reports that have remained in the same status for too long.
For instance, I can create two report statuses "To program" with timer days set to 10 and "Programmed" with timer days set to 0.
If a report has had status "To program" for 10 days, an email alert will be sent. If its status is changed to "Programmed" within these 10 days, this will cancel the alert.
The email alert will be sent to the assigned user for this report, or to managers (setting `MANAGERS`) if there is no assigned user.

To enable the alerts :

- Go to the Admin Site and set "Timer days" to some integer other than 0 in relevant statuses (`/admin/feedback/reportstatus/`)

- Select the "Uses timers" checkbox on reports that you wish to receive alerts for (in report update form)

- Make sure to run this commands daily to send email alerts and clear obsolete timers (thanks to `cron` for instance) :

.. code-block :: python

    geotrek check_timers


Anonymize feedback reports
~~~~~~~~~~~~~~~~~~~~~~~~~~

To be compliant to GDPR, you cannot keep personnal data infinitely,
and should notice your users on how many time you keep their email.

A Django command is available to anonymize reports, by default older
than 365 days.

.. code-block :: bash

    geotrek erase_emails

Or if you want to erase emails for reports older than 90 days

.. code-block :: bash

    geotrek erase_emails --days 90


Attachments
-----------

View attachments in the browser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Attached files are downloaded by default by browser, with the following line,
files will be opened in the browser :

.. code-block :: python

    MAPENTITY_CONFIG['SERVE_MEDIA_AS_ATTACHMENT'] = False


Resizing uploaded pictures
~~~~~~~~~~~~~~~~~~~~~~~~~~

Attached pictures can be resized at upload by enabling ``PAPERCLIP_RESIZE_ATTACHMENTS_ON_UPLOAD`` :

::

    PAPERCLIP_RESIZE_ATTACHMENTS_ON_UPLOAD = True

These corresponding height/width parameters can be overriden to select resized image size :

::

    PAPERCLIP_MAX_ATTACHMENT_WIDTH = 1280
    PAPERCLIP_MAX_ATTACHMENT_HEIGHT = 1280


Prohibit usage of big pictures and small width / height
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to prohibit the usage of heavy pictures :

::

    PAPERCLIP_MAX_BYTES_SIZE_IMAGE = 50000  # Bytes


If you want to prohibit the usage of small pictures in pixels :

::

    PAPERCLIP_MIN_IMAGE_UPLOAD_WIDTH = 100
    PAPERCLIP_MIN_IMAGE_UPLOAD_HEIGHT = 100

These 3 settings will also not allow downloading images from the parsers.


Prohibit usage of certain file types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Paperclip will only accept attachment files matching a list of allowed extensions.
Here is the default value for this setting, which you can extend if needed :

::

    PAPERCLIP_ALLOWED_EXTENSIONS = [
        'jpeg',
        'jpg',
        'mp3',
        'mp4',
        'odt',
        'pdf',
        'png',
        'svg',
        'txt',
        'gif',
        'tiff',
        'tif',
        'docx',
        'webp',
        'bmp',
        'flac',
        'mpeg',
        'doc',
        'ods',
        'gpx',
        'xls',
        'xlsx',
        'odg',
    ]

It will verify that the mimetype of the file matches the extension. You can add extra allowed mimetypes for a given extension with the following syntax :

::

    PAPERCLIP_EXTRA_ALLOWED_MIMETYPES['gpx'] = ['text/xml']

You can also entirely deactivate these checks with the following :

::

    PAPERCLIP_ALLOWED_EXTENSIONS = None

These 2 settings will also not allow downloading images from the parsers.


Interface
---------

Configure columns displayed in lists views and exports
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For each module, use the following syntax to configure columns to display in the main table.

::

    COLUMNS_LISTS['<module>_view'] = ['list', 'of', 'columns']


For each module, use the following syntax to configure columns to export as CSV or SHP.

::

    COLUMNS_LISTS['<module>_export'] = ['list', 'of', 'columns']


Please refer to the "settings detail" section for a complete list of modules and available columms.

Another setting exists to enable a more detailed export of jobs costs in the interventions module. When enabling this settings, interventions list exports will contain a new column for each job's total cost.

::

    ENABLE_JOBS_COSTS_DETAILED_EXPORT = True


Configure form fields in creation views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For each module, use the following syntax to configure fields to hide in the creation form.

::

    HIDDEN_FORM_FIELDS['<module>'] = ['list', 'of', 'fields']


Please refer to the "settings detail" section for a complete list of modules and hideable fields.


Configure form fields required or needed for review or publication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set 'error_on_publication' to avoid publication without completeness fields
and 'error_on_review' if you want this fields to be required before sending to review.

::

    COMPLETENESS_LEVEL = 'warning'

For each module, configure fields to be needed or required on review or publication

::

    COMPLETENESS_FIELDS = {
        'trek': ['practice', 'departure', 'duration', 'difficulty', 'description_teaser'],
        'dive': ['practice', 'difficulty', 'description_teaser'],
    }


Edition
-------

WYSIWYG editor configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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


Max characters count
~~~~~~~~~~~~~~~~~~~~

Add ``MAX_CHARACTERS`` setting to be able to define a maximum number of characters
for text fields (to be used with django-mapentity >= 8.1).

.. code-block :: python

    MAPENTITY_CONFIG['MAX_CHARACTERS'] = 1500

This will apply to all text fields.
See `this issue <https://github.com/GeotrekCE/Geotrek-admin/issues/2901>`_ for details.


Copyright on pictures
~~~~~~~~~~~~~~~~~~~~~

If you want copyright added to your pictures, change ``THUMBNAIL_COPYRIGHT_FORMAT`` to this :

::

    THUMBNAIL_COPYRIGHT_FORMAT = "{title} {author}"

You can also add ``{legend}``.

::

    THUMBNAIL_COPYRIGHT_SIZE = 15


Facebook configuration
~~~~~~~~~~~~~~~~~~~~~~

When a content is shared to Facebook in Geotrek-rando V2,
it needs static html files built by synchronization (thanks to option ``--rando-url``).

In Facebook developper dashboard, create a Facebook app dedicated to Geotrek-rando and activate it.

.. image :: /images/facebookappid.png

In ``custom.py`` set Facebook App ID:

::

    FACEBOOK_APP_ID = '<your Facebook AppID>'

you can also override these settings:

::

    FACEBOOK_IMAGE = '/images/logo-geotrek.png'
    FACEBOOK_IMAGE_WIDTH = 200
    FACEBOOK_IMAGE_HEIGHT = 200


Override translations
~~~~~~~~~~~~~~~~~~~~~

Translations are managed by https://weblate.makina-corpus.net/ where you can contribute.
But you can also override default translation files available in each module
(for example those from trekking module available in ``/opt/geotrek-admin/lib/python3.6/site-packages/geotrek/trekking/locale/fr/LC_MESSAGES/django.po``).

Don't edit these default files, use them to find which words you want to override.

Create the custom translations destination folder:

Create a ``django.po`` file in ``/opt/geotrek-admin/var/conf/extra_locale`` directory.
You can do one folder and one ``django.po`` file for each language
(example ``/opt/geotrek-admin/var/conf/extra_locale/fr/LC_MESSAGES/django.po`` for French translation overriding)

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

Apply changes (French translation in this example) :

::

    cd /opt/geotrek-admin/var/conf/extra_locale
    sudo chown geotrek. fr/LC_MESSAGES/
    sudo geotrek compilemessages
    sudo service geotrek restart


Override public PDF templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PDF are generated from HTML templates, using `Django templating <https://docs.djangoproject.com/en/1.11/ref/templates/>`_.
Treks, touristic contents, touristic events, outdoor sites and courses can be exported in PDF files.

- Treks : ``geotrek/trekking/templates/trekking/trek_public_pdf.html``
- Touristic contents : ``geotrek/tourism/templates/tourism/touristiccontent_public_pdf.html``
- Touristic events : ``geotrek/tourism/templates/tourism/touristiccontent_public_pdf.html``
- Outdoor sites : ``geotrek/outdoor/templates/outdoor/site_public_pdf.html``
- Outdoor courses : ``geotrek/outdoor/templates/outdoor/course_public_pdf.html``

Overriden templates have to be located in ``/opt/geotrek-admin/var/conf/extra_templates/<appname>``, with ``<appname>`` = ``trekking`` or ``tourism``.
To override trekking PDF for example, copy the file ``geotrek/trekking/templates/trekking/trek_public_pdf.html``
to ``/opt/geotrek-admin/var/conf/extra_templates/trekking/trek_public_pdf.html``. Or add inside your file :

::

    {% extends "trekking/trek_public_pdf.html" %}


These templates derive from base templates, which content is organized in blocks.
To override for example the description block of trek PDF, copy and change the ``{% block description }…{% endblock description %}``
in your ``/opt/geotrek-admin/var/conf/extra_templates/trekking/trek_public_pdf.html``.

It is also possible to use color defined for practice for pictogram by adding in your
``/opt/geotrek-admin/var/conf/extra_templates/trekking/trek_public_pdf.html`` file :

::

    {% block picto_attr %}style="background-color: {{ object.practice.color }};"{% endblock picto_attr %}

CSS can be overriden like html templates: copy them to ``var/media/templates/trekking/`` or ``var/media/templates/tourism/`` folder
``/opt/geotrek-admin/var/conf/extra_templates/trekking/trek_public_pdf.css`` for example.

**You can also create a template for each portal.**

Add a folder ``portal_{id_portal}`` (portal ids are located in the portal url path ``/admin/common/targetportal/{id_portal}``) in
``/opt/geotrek-admin/var/conf/extra_templates/<appname>``, as the first template, and add at the top of your file:

::

    {% extends "trekking/trek_public_pdf.html" %}


The template for a specific portal will use the modification made on the overriden template in  ``/opt/geotrek-admin/var/conf/extra_templates/<appname>``
( except if you change specific  block)

.. note ::

    This modification is not mandatory, if you have multiple portal and you want to modify the template of only one portal, you create one folder for this specific portal

**You might need to use your own images in the PDF templates.**

Add your own images in ``/opt/geotrek-admin/var/conf/extra_static/images/``.

You can then use these images in your PDF templates with ``{% static 'images/file.jpg' %}``, after adding ``{% load static %}`` at the top of the file.

Example of a customised template (``/opt/geotrek-admin/var/conf/extra_templates/trekking/trek_public_pdf.html``) with a customised logo and URL:

::

    {% extends "trekking/trek_public_pdf.html" %}
    {% load static %}

    {% block logo %}
       <img src="{% static 'images/logo-gte.jpg' %}" alt="Grand tour des Ecrins">
    {% endblock %}
    {% block url %}
       <div class="main">Grand tour des Ecrins</div>
       <div class="geo"><a href="https://www.grand-tour-ecrins.fr">grand-tour-ecrins.fr</a></div>
    {% endblock url %}

.. note ::

    The default template may change in the future versions. You will be
    in charge of porting the modification to your copy.

Test your modifications by exporting a trek or a content to PDF from Geotrek-admin application.
To get your modifications available for Rando application, launch the ``sync_rando`` command.


Custom font in public document template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to use custom fonts in trek PDF, it is necessary to install the
font files on the server.

*Microsoft* fonts like *Arial* and *Verdana* can be installed via the package
manager:

::

    sudo apt-get install ttf-mscorefonts-installer

For specific fonts, copy the ``.ttf`` (or ``.otf``) files into the folder
``/usr/local/share/fonts/custom/`` as root, and run the following command:

::

    fc-cache

For more information, check out Ubuntu documentation.


Custom colors in public document template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Trek export geometries are translucid red by default. In order to control the
apparence of objects in public trek PDF exports, use the following setting:

::

    MAPENTITY_CONFIG['MAP_STYLES']['print']['path'] = {'weight': 3}

See *Leaflet* reference documentation for detail about layers apparence.


Primary color in PDF templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can override ``PRIMARY_COLOR`` to change emphase text in PDF export.
Beware of contrast, white colour is used for text so we advise you to avoid light colour.


Custom logos
~~~~~~~~~~~~

You might also need to deploy logo images in the following places :

* ``var/conf/extra_static/images/favicon.png``
* ``var/conf/extra_static/images/logo-login.png``
* ``var/conf/extra_static/images/logo-header.png``
