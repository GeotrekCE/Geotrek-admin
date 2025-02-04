.. _attachments:

==============
Attachments
==============

View attachments in the browser
---------------------------------

Mapentity config for medias
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Attached files are downloaded by default by browser, with the following line, files will be opened in the browser :

.. md-tab-set::
    :name: mapentityconfig-medias-tabs

    .. md-tab-item:: Default configuration

            .. code-block:: python
    
                MAPENTITY_CONFIG['SERVE_MEDIA_AS_ATTACHMENT'] = True

    .. md-tab-item:: Example

         .. code-block:: python
    
                MAPENTITY_CONFIG['SERVE_MEDIA_AS_ATTACHMENT'] = False

.. seealso:: 
  Check the official documentation of Django Mapentity `mapentity/views/base.py <https://django-mapentity.readthedocs.io/en/stable/customization.html#media>`_ to know more.


Resizing uploaded pictures
----------------------------

.. info::
  
  For a complete list of available parameters, refer to the default values in `geotrek/settings/base.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/settings/base.py>`_.

Paperclip resize attachments on upload 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To enable automatic resizing of uploaded pictures:

.. md-tab-set::
    :name: paperclip-resize-attachments-medias-tabs

    .. md-tab-item:: Default configuration

            .. code-block:: python
    
                PAPERCLIP_RESIZE_ATTACHMENTS_ON_UPLOAD = False

    .. md-tab-item:: Example

         .. code-block:: python
    
                PAPERCLIP_RESIZE_ATTACHMENTS_ON_UPLOAD = True

These corresponding height/width parameters can be overriden to select resized image size:

.. md-tab-set::
    :name: paperclip-resize-max-attachments-medias-tabs

    .. md-tab-item:: Default configuration

            .. code-block:: python
    
                PAPERCLIP_MAX_ATTACHMENT_WIDTH = 1280
                PAPERCLIP_MAX_ATTACHMENT_HEIGHT = 1280

    .. md-tab-item:: Example

         .. code-block:: python
    
                PAPERCLIP_MAX_ATTACHMENT_WIDTH = 800
                PAPERCLIP_MAX_ATTACHMENT_HEIGHT = 800

Prohibit usage of big pictures and small width / height
---------------------------------------------------------

Paperclip max bytes size images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to prohibit the usage of heavy pictures:

.. md-tab-set::
    :name: paperclip-max-bytes-size-tabs

    .. md-tab-item:: Default configuration

            .. code-block:: python
    
                PAPERCLIP_MAX_BYTES_SIZE_IMAGE = None

    .. md-tab-item:: Example

         .. code-block:: python
    
                PAPERCLIP_MAX_BYTES_SIZE_IMAGE = 50000 # Bytes

If you want to prohibit the usage of small pictures in pixels:

.. md-tab-set::
    :name: paperclip-min-bytes-size-tabs

    .. md-tab-item:: Default configuration

            .. code-block:: python
    
                PAPERCLIP_MIN_IMAGE_UPLOAD_WIDTH = None
                PAPERCLIP_MIN_IMAGE_UPLOAD_HEIGHT = None

    .. md-tab-item:: Example

         .. code-block:: python
    
               PAPERCLIP_MIN_IMAGE_UPLOAD_WIDTH = 300
               PAPERCLIP_MIN_IMAGE_UPLOAD_HEIGHT = 300

.. note:: 
  These three settings will also not allow downloading images from the parsers.

Prohibit usage of certain file types
-------------------------------------

Paperclip will only accept attachment files matching a list of allowed extensions.

Here is the default value for this setting, which you can extend if needed:

.. md-tab-set::
    :name: paperclip-allowed-extensions-tabs

    .. md-tab-item:: Default configuration

            .. code-block:: python
    
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

    .. md-tab-item:: Example

         .. code-block:: python
    
            PAPERCLIP_ALLOWED_EXTENSIONS = [
                'jpeg',
                'avi',
                'zip',
                'jpg',
                'mp3',
                'mp4',
                'odt',
                'pdf',
                'png',
                'svg',
                'txt',
                'gif',
            ]

It will verify that the mimetype of the file matches the extension. 

Paperclip extra alloawed mimetypes 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can add extra allowed mimetypes for a given extension with the following syntax:

.. md-tab-set::
    :name: paperclip-extra-allowed-mimetypes-tabs

    .. md-tab-item:: Default configuration

            .. code-block:: python
    
                PAPERCLIP_EXTRA_ALLOWED_MIMETYPES = {
                  'bmp': ['image/bmp'],
                  'gpx': ['text/xml'],
                  'webp': ['image/webp'],
                  'svg': ['image/svg']
                }

    .. md-tab-item:: Example

         .. code-block:: python
    
               PAPERCLIP_EXTRA_ALLOWED_MIMETYPES['gpx'] = ['text/xml']

Paperclip allowed extensions 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can also entirely deactivate these checks with the following:

.. code-block:: python

    PAPERCLIP_ALLOWED_EXTENSIONS = None

.. note:: 
  These two settings (``PAPERCLIP_ALLOWED_EXTENSIONS`` and ``PAPERCLIP_EXTRA_ALLOWED_MIMETYPES``) will also not allow downloading images from the parsers.


