.. _advanced-configuration-section:

======================
Advanced Configuration
======================

Custom setting file
-------------------

Geotrek configuration is currently restricted to values present in ``etc/settings.ini``.

However, it is still possible to write a custom Django setting file.

* Create your a file in *geotrek/settings/custom.py* with the following content ::

    from .prod import *

    # My custom value
    HIDDEN_OPTION = 3.14

* Add this ``etc/settings.ini`` to specify the newly created setting ::

    [django]
    settings = settings.custom

* As for any change in settings, re-run ``make env_standalone deploy``.


WYSIWYG editor configuration
----------------------------

Text form fields are enhanced using `TinyMCE <http://tinymce.com>`_.

Its configuration can be customized using advanced settings (see above paragraph).

For example, in order to control which buttons are to be shown, and which tags
are to be kept when cleaning-up, add this bloc :

::

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

::

    MAPENTITY_CONFIG['SERVE_MEDIA_AS_ATTACHMENT'] = False
