.. _edition:

==========
Edition
==========

WYSIWYG editor configuration
-----------------------------

Text form fields are enhanced using `TinyMCE <http://tinymce.com>`_.

TinyMCE default configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To customize which buttons are displayed and which tags are preserved during cleanup, use the following configuration:

.. code-block:: bash
    :caption: Example

    TINYMCE_DEFAULT_CONFIG = {
    'theme_advanced_buttons1': 'bold,italic,forecolor,separator,code',
    'valid_elements': "img,p,a,em/i,strong/b",
    }

.. note::
  - This configuration applies to all text fields.
  - For more details, refer to the official *TinyMCE version 3* documentation.

Max characters count
---------------------

Mapentity for characters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To set a maximum character limit for text fields, add the ``MAX_CHARACTERS_BY_FIELD`` setting:

.. code-block:: bash
    :caption: Example

    MAPENTITY_CONFIG['MAX_CHARACTERS_BY_FIELD'] = { 
       "tourism_touristicevent": [{'field': 'description_teaser_fr', 'value': 50}, {'field': 'accessibility_fr', 'value': 25}],
       "trekking_trek": [{'field': 'description_teaser_fr', 'value': 150}],
    }

.. note::
  - Limits are applied per field and per language.
  - See `this issue <https://github.com/GeotrekCE/Geotrek-admin/issues/3844>`_ for further details.

Copyright on pictures
------------------------

Thumbnail copyright format
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To add copyright information to images, modify this parameter:

.. md-tab-set::
    :name: thumbnail-copyright-format-tabs

    .. md-tab-item:: Default configuration

            .. code-block:: python
    
                THUMBNAIL_COPYRIGHT_FORMAT = ""

    .. md-tab-item:: Example

         .. code-block:: python
    
                THUMBNAIL_COPYRIGHT_FORMAT = "{title} {author}"

Some variables can be used: ``{title},{author},{legend}``               

.. note::
  - This configuration applies to all text fields.
  - For more details, refer to the official *TinyMCE version 3* documentation.

Thumbnail copyright size
~~~~~~~~~~~~~~~~~~~~~~~~~~

To modify the size of the copyright text on thumbnails:

.. md-tab-set::
    :name: thumbnail-copyright-size-tabs

    .. md-tab-item:: Default configuration

            .. code-block:: python
    
                THUMBNAIL_COPYRIGHT_SIZE = 15

    .. md-tab-item:: Example

         .. code-block:: python
    
                THUMBNAIL_COPYRIGHT_SIZE = 20

Override translations
----------------------

Translations in Geotrek-admin are managed through `Weblate <https://weblate.makina-corpus.net/>`_, where you can contribute to the official translations.

However, if you need to modify specific translations without altering the global project, you can override default translation files for each module.

For example, the translation files for the Trekking module are located at:
``/opt/geotrek-admin/lib/python3.6/site-packages/geotrek/trekking/locale/fr/LC_MESSAGES/django.po``.

.. important::
  
  Do not edit these default files directly. Instead, use them as a reference to identify the terms you want to override.

Create custom translation folder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To override translations, follow these steps:

1. Create a ``django.po`` file inside the ``/opt/geotrek-admin/var/conf/extra_locale`` directory.
2. Organize translations by language: each language should have its own folder with a ``django.po`` file. 
   
   - Example for French: ``/opt/geotrek-admin/var/conf/extra_locale/fr/LC_MESSAGES/django.po``.

In this file, override only the necessary translations.

**Example of content for the French translation overriding:**

.. code-block:: python

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

Apply changes
~~~~~~~~~~~~~~

Once you have modified the translation file, apply the changes using the following commands:

.. md-tab-set::
    :name: apply-changes-translations-tabs

    .. md-tab-item:: With Debian

        .. code-block:: bash
    
            cd /opt/geotrek-admin/var/conf/extra_locale
            sudo chown -R geotrek: geotrek-admin fr/LC_MESSAGES/
            sudo geotrek compilemessages
            sudo service geotrek restart

    .. md-tab-item:: With Docker

         .. code-block:: bash

            cd /opt/geotrek-admin/var/conf/extra_locale
            sudo chown -R geotrek: geotrek-admin fr/LC_MESSAGES/
            docker compose run --rm web update.sh 

.. note::
  - The default PDF templates and translations may be updated in future versions of Geotrek-admin. Ensure that you maintain your custom modifications accordingly.
  - Restarting the Geotrek service ensures the new translations are applied correctly.

Override public PDF templates
------------------------------

PDF files are generated from HTML templates using `Django templating <https://docs.djangoproject.com/en/1.11/ref/templates/>`_. The following elements can be exported as PDFs:

- **Treks:** ``geotrek/trekking/templates/trekking/trek_public_pdf.html``
- **Touristic Contents:** ``geotrek/tourism/templates/tourism/touristiccontent_public_pdf.html``
- **Touristic Events:** ``geotrek/tourism/templates/tourism/touristicevent_public_pdf.html``
- **Outdoor Sites:** ``geotrek/outdoor/templates/outdoor/site_public_pdf.html``
- **Outdoor Courses:** ``geotrek/outdoor/templates/outdoor/course_public_pdf.html``

Customize PDF templates
~~~~~~~~~~~~~~~~~~~~~~~

To customize a PDF template, you need to place your modified version in:

``/opt/geotrek-admin/var/conf/extra_templates/<appname>`` where ``<appname>`` corresponds to the relevant module (e.g., ``trekking``, ``tourism``).

.. code-block:: bash
    :caption: For example, to override the **Trek PDF template**, copy the default file:

    cp geotrek/trekking/templates/trekking/trek_public_pdf.html \
       /opt/geotrek-admin/var/conf/extra_templates/trekking/trek_public_pdf.html

.. code-block:: django
    :caption: Alternatively, you can extend the default template by including the following in your custom file:

    {% extends "trekking/trek_public_pdf.html" %}


Customize specific sections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Geotrek PDF templates use a block structure, allowing you to override specific sections without modifying the entire file.

.. code-block:: django
    :caption: For instance, to modify only the **description block**, add:

    {% block description %}
        Custom description content here.
    {% endblock description %}

Use custom for pictograms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: django
    :caption: You can use practice-specific colors for pictograms by adding the following inside your template:

    {% block picto_attr %}style="background-color: {{ object.practice.color }};"{% endblock picto_attr %}

Override CSS style
~~~~~~~~~~~~~~~~~~~~~

To customize the styles of exported PDFs, copy the CSS files to:

- ``var/media/templates/trekking/``
- ``var/media/templates/tourism/``

.. code-block:: bash
    :caption: For example:

    cp geotrek/trekking/templates/trekking/trek_public_pdf.css \
       /opt/geotrek-admin/var/conf/extra_templates/trekking/trek_public_pdf.css

Create a template for each portal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you need to apply different templates for specific portals, you can create dedicated templates by following these steps:

.. code-block:: bash
    :caption: 1.Identify the portal ID by checking its URL in the admin interface:

    /admin/common/targetportal/{id_portal}

.. code-block:: bash
    :caption: 2.Create a corresponding folder in:

    /opt/geotrek-admin/var/conf/extra_templates/portal_{id_portal}

.. code-block:: django
    :caption: 3.Place your customized template inside this directory and extend the base template:

    {% extends "trekking/trek_public_pdf.html" %}

Only the modifications in this folder will apply to the specified portal.

.. note::
  This step is **optional**. If you have multiple portals but only need to modify the template for one, you can create a dedicated folder for that portal only.

Custom images in PDF
~~~~~~~~~~~~~~~~~~~~

If you need to include your own images in the PDF templates, store them in:

``/opt/geotrek-admin/var/conf/extra_static/images/``

Then, reference them in your template as follows:

.. code-block:: django

    {% load static %}
    <img src="{% static 'images/custom-logo.jpg' %}" alt="Custom Logo">

Add custom logo and URL
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: django

    {% extends "trekking/trek_public_pdf.html" %}
    {% load static %}

    {% block logo %}
       <img src="{% static 'images/logo-gte.jpg' %}" alt="Grand Tour des Écrins">
    {% endblock %}
    {% block url %}
       <div class="main">Grand Tour des Écrins</div>
       <div class="geo"><a href="https://www.grand-tour-ecrins.fr">grand-tour-ecrins.fr</a></div>
    {% endblock url %}


- The default PDF templates may be updated in future versions of Geotrek-admin. Ensure that you maintain your custom modifications accordingly.
- Test your modifications by exporting a trek or touristic content to PDF from the Geotrek-admin interface.

Only external public PDF
~~~~~~~~~~~~~~~~~~~~~~~~~~

Only externally imported PDFs with the "Topoguide" file type are used, rather than autogenerated PDFs.

.. md-tab-set::
    :name: only-external-public-tabs

    .. md-tab-item:: Default configuration

            .. code-block:: python
    
                ONLY_EXTERNAL_PUBLIC_PDF = False

    .. md-tab-item:: Example

         .. code-block:: python
    
               ONLY_EXTERNAL_PUBLIC_PDF = True

**Order of all the objects without practices on Geotrek-rando website** :

.. code-block:: python

    TREK_CATEGORY_ORDER = 1
    ITINERANCY_CATEGORY_ORDER = 2
    TOURISTIC_EVENT_CATEGORY_ORDER = 99

.. note::
  - Order settings determine the display order within the Geotrek-rando website.
  - Practices for treks, and touristic content categories are taken into account.

Trek export 
~~~~~~~~~~~~

POI list limit 
^^^^^^^^^^^^^^^

Defines the maximum number of POIs displayed in the trek PDF export.

.. md-tab-set::
    :name: trek-export-poi-list-tabs

    .. md-tab-item:: Default configuration

        .. code-block:: python

            TREK_EXPORT_POI_LIST_LIMIT = 14

    .. md-tab-item:: Example

        .. code-block:: python

            TREK_EXPORT_POI_LIST_LIMIT = 20

.. note::
  ``14`` is already a large number of POIs, but you can increase this limit if needed.

Information desk list limit 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Defines the maximum number of information desks displayed in the trek PDF export.

.. md-tab-set::
    :name: trek-export-informationdesk-list-tabs

    .. md-tab-item:: Default configuration

        .. code-block:: python

            TREK_EXPORT_INFORMATION_DESK_LIST_LIMIT = 2

    .. md-tab-item:: Example

        .. code-block:: python

            TREK_EXPORT_INFORMATION_DESK_LIST_LIMIT = 5

.. note::
  Use ``-1`` to display all available information desks.

PDF as booklet
----------------

Use booklet for PDF:

.. md-tab-set::
    :name: use-booklet-pdf-tabs

    .. md-tab-item:: Default configuration

            .. code-block:: python
    
                USE_BOOKLET_PDF = False

    .. md-tab-item:: Example

         .. code-block:: python
    
                USE_BOOKLET_PDF = True

.. note:: 
  It is possible to customize the PDF, with ``trek_public_booklet_pdf.html``.

Custom font in public document template
----------------------------------------

In order to use custom fonts in trek PDF, it is necessary to install the
font files on the server.

*Microsoft* fonts like *Arial* and *Verdana* can be installed via the package
manager:

::

    sudo apt-get install ttf-mscorefonts-installer

For specific fonts, copy the ``.ttf`` (or ``.otf``) files into the folder
``/usr/local/share/fonts/custom/`` as root, and run the following command:

.. code-block:: bash

    fc-cache

For more information, check out Ubuntu documentation.

Custom colors in public document template
------------------------------------------

Mapentity for custom colors in PDF
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Trek export geometries are translucid red by default. In order to control the apparence of objects in public trek PDF exports, use the following setting:

.. md-tab-set::
    :name: mapentity-config-map-style-tabs

    .. md-tab-item:: Default configuration

            .. code-block:: python
    
                MAPENTITY_CONFIG['MAP_STYLES']['print']['path'] = {'weight': 1}

    .. md-tab-item:: Example

         .. code-block:: python
    
                MAPENTITY_CONFIG['MAP_STYLES']['print']['path'] = {'weight': 3}

See `Leaflet reference documentation <https://leafletjs.com/reference.html#path>`_ for detail about layers apparence.

Primary color in PDF templates 
-------------------------------

Primary color
~~~~~~~~~~~~~~

You can override ``PRIMARY_COLOR`` to change emphase text in PDF export.

.. md-tab-set::
    :name: mapentity-config-map-style-color-tabs

    .. md-tab-item:: Default configuration

            .. code-block:: python
    
                PRIMARY_COLOR = "#7b8c12"

    .. md-tab-item:: Example

         .. code-block:: python
    
                PRIMARY_COLOR = "#0000FF"

.. note:: 
  Beware of contrast, white colour is used for text so we advise you to avoid light colour.

Custom logos
-------------

You might also need to deploy logo images in the following places :

* ``var/conf/extra_static/images/favicon.png``
* ``var/conf/extra_static/images/logo-login.png``
* ``var/conf/extra_static/images/logo-header.png``


