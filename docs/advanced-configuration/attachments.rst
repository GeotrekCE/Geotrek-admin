.. _attachments:

==============
Attachments
==============

.. contents::
   :local:
   :depth: 2


View attachments in the browser
---------------------------------

MAPENTITY_CONFIG for medias
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Attached files are downloaded by default by browser, with the following line, files will be opened in the browser :

    Example::

        MAPENTITY_CONFIG['SERVE_MEDIA_AS_ATTACHMENT'] = False

    Default::

        True

Resizing uploaded pictures
----------------------------

PAPERCLIP_RESIZE_ATTACHMENTS_ON_UPLOAD
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Attached pictures can be resized at upload by enabling this parameter :

    Example::

        PAPERCLIP_RESIZE_ATTACHMENTS_ON_UPLOAD = True

    Default::

        False


These corresponding height/width parameters can be overriden to select resized image size:

.. code-block:: python

    PAPERCLIP_MAX_ATTACHMENT_WIDTH = 1280
    PAPERCLIP_MAX_ATTACHMENT_HEIGHT = 1280


Prohibit usage of big pictures and small width / height
---------------------------------------------------------

PAPERCLIP_MAX_BYTES_SIZE_IMAGE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    If you want to prohibit the usage of heavy pictures:

    Example::

        PAPERCLIP_MAX_BYTES_SIZE_IMAGE = 50000 # Bytes

If you want to prohibit the usage of small pictures in pixels:

.. code-block:: python

    PAPERCLIP_MIN_IMAGE_UPLOAD_WIDTH = 100
    PAPERCLIP_MIN_IMAGE_UPLOAD_HEIGHT = 100

These three settings will also not allow downloading images from the parsers.


Prohibit usage of certain file types
-------------------------------------

Paperclip will only accept attachment files matching a list of allowed extensions.
Here is the default value for this setting, which you can extend if needed:

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

It will verify that the mimetype of the file matches the extension. 

PAPERCLIP_EXTRA_ALLOWED_MIMETYPES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    You can add extra allowed mimetypes for a given extension with the following syntax:

    Example::

        PAPERCLIP_EXTRA_ALLOWED_MIMETYPES['gpx'] = ['text/xml']

PAPERCLIP_ALLOWED_EXTENSIONS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    You can also entirely deactivate these checks with the following:

    Example::

        PAPERCLIP_ALLOWED_EXTENSIONS = None

.. note:: 
  These two settings will also not allow downloading images from the parsers.


