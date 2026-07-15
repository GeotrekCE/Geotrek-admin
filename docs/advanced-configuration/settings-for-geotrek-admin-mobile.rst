.. _settings-for-geotrek-admin-mobile:

=================================
Settings for Geotrek-admin mobile
=================================

.. info::
  
  For a complete list of available parameters, refer to the default values in `geotrek/settings/base.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/settings/base.py>`_.

Reference data synchronization interval
---------------------------------------

Defines the maximum amount of time reference data can remain unsynchronized. Once this interval has elapsed, the user must manually synchronize the reference data before continuing to use the application.

Example::

    GTAM_CONFIG["REFERENCES_INTERVAL_SYNC"] = 7 * 24

.. note::

   - The value is expressed in hours.

Embedded data synchronization interval
------------------------------------------------

Defines the maximum amount of time embedded data can remain unsynchronized. Once this interval has elapsed, the user must manually synchronize the embedded data before continuing to use the application.

Example::

    GTAM_CONFIG["DATA_INTERVAL_SYNC"] = 7 * 24

.. note::

   - The value is expressed in hours.

Minimum zoom level for map synchronization
-------------------------------------------

Defines the minimum zoom level from which users are allowed to download map tiles.

Example::

    GTAM_CONFIG["SYNC_MAP_MIN_ZOOM"] = 10

.. note::

   - A zoom level greater than ``10`` is recommended to limit the number of downloaded tiles.

JWT authentication
------------------

Defines the lifetime of the JSON Web Tokens used for API authentication.

Example::

    SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(days=3)
    SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"] = timedelta(days=21)

.. note::

   - ``ACCESS_TOKEN_LIFETIME`` defines how long an access token remains valid before it expires.
   - ``REFRESH_TOKEN_LIFETIME`` defines how long a refresh token remains valid. Once it expires, the user must authenticate again to obtain new tokens.
