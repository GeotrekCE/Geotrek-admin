.. _advanced-configuration-section:

======================
ADVANCED CONFIGURATION
======================

Custom setting file
-------------------

Geotrek configuration is currently restricted to values present in ``etc/settings.ini``.

However, it is still possible to write a custom Django setting file.

* Create your a file in *geotrek/settings/custom.py* with the following content :

.. code-block :: python

    from .prod import *

    # My custom value
    HIDDEN_OPTION = 3.14

* Add this ``etc/settings.ini`` to specify the newly created setting :

.. code-block :: ini

    [django]
    settings = settings.custom

* As for any change in settings, re-run ``make env_standalone deploy``.


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


Using Google Maps projection in the Web interface
-------------------------------------------------

Just add this line in your custom production settings file :

.. code-block :: python

    LEAFLET_CONFIG['SRID'] = 3857

Your data will still be stored using the SRID you specified in the ``settings.ini``
file.

Now you can use WMTS or *OpenStreetMap* tiles for example :

.. code-block :: python

    LEAFLET_CONFIG['TILES'] = [
        ('Scan', 'http://{s}.tile.osm.org/{z}/{x}/{y}.png', '(c) OpenStreetMap Contributors'),
        ('Ortho', 'http://{s}.tiles.mapbox.com/v3/openstreetmap.map-4wvf9l0l/{z}/{x}/{y}.jpg', '(c) MapBox'),
    ]


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

    User management will be disabled from Administration backoffice.

    In order to disable remote login, just remove *authent_dbname* value in settings
    file, and update instance (see paragraph above).

    Geotrek can support many types of users authentication (LDAP, oauth, ...), contact-us
    for more details.


External map layers
-------------------

In order to display external layers in *Geotrek* and *Geotrek-rando*, it is
possible to define external datasources.

So far, the following formats are supported :

* GeoJSON
* TIF (*TourInFrance*)

From the Administration backoffice, create datasources using a name, an URL, and
a pictogram. You can choose if this layer should be displayed in the different
Geotrek modules, or published to the public Website (*Geotrek-rando*).
