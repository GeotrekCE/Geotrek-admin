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


Nginx configuration for docker
------------------------------

* This new version require the following configuration in your Nginx server to allow the mobile application to access the API:

Example::

    location ~ ^/m/(?<remaining_path>.*)$ {
        root /;
        try_files /opt/geotrek-admin/var/frontend/dist/$remaining_path /opt/geotrek-admin/var/frontend/dist/index.html =404;
    }

    location ^~ /m/sw.js {
        alias /opt/geotrek-admin/var/frontend/dist/sw.js;
        add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0";
        expires off;
        access_log off;
    }

    location = /m {
        return 307 /m/;
    }

This snippet is defined in new default Nginx configuration for Docker. https://github.com/GeotrekCE/Geotrek-admin/blob/master/docker/install/conf/nginx.conf

Configuring and generating offline maps
---------------------------------------

- Add map base layers

  - With admin interface (/admin/mapbox_baselayer/mapbaselayer/)
    This support raster and vector tiles layers. For vector tiles, you need to set style url.

  - With command line, you can add a new map base layer with the following command:

.. md-tab-set::
    :name: generate-pmtiles-command-tabs

    .. md-tab-item:: With Debian

         .. code-block:: python

          sudo geotrek install_layer osm (or ign or other provider).

    .. md-tab-item:: With Docker

         .. code-block:: python

          docker compose run --rm web ./manage.py install_layer osm (or ign or other provider).

- generate offline map with following command:

.. md-tab-set::
    :name: generate-pmtiles-command-tabs

    .. md-tab-item:: With Debian

         .. code-block:: python

          sudo geotrek generate_pmtiles <id> (id of the map base layer)

    .. md-tab-item:: With Docker

         .. code-block:: python

          docker compose run --rm web ./manage.py generate_pmtiles <id> (id of the map base layer)