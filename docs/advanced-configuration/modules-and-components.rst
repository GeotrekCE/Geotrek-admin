.. _modules-and-components:

=======================
Modules and components
=======================

See the default values in `geotrek/settings/base.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/settings/base.py>`_ for the complete list of available parameters.

Enable Apps
------------

In order to disable a full set of modules, in the custom settings file, add the following code:

.. md-tab-set::
    :name: disable-app-tabs

    .. md-tab-item:: Examples of disabling apps

         .. code-block:: python
    
              # Disable infrastructure and maintenance
              _INSTALLED_APPS = list(INSTALLED_APPS)
              _INSTALLED_APPS.remove('geotrek.infrastructure')
              _INSTALLED_APPS.remove('geotrek.maintenance')
              INSTALLED_APPS = _INSTALLED_APPS

    .. md-tab-item:: Default enabled apps

         .. code-block:: python
    
              INSTALLED_APPS = (
                'geotrek.cirkwi',
                'geotrek.authent',
                'geotrek.common',
                'geotrek.altimetry',
                'geotrek.core',
                'geotrek.infrastructure',
                'geotrek.signage',
                'geotrek.maintenance',
                'geotrek.zoning',
                'geotrek.land',
                'geotrek.trekking',
                'geotrek.tourism',
                'geotrek.flatpages',
                'geotrek.feedback',
                'geotrek.api',
              )


Trail model enabled
~~~~~~~~~~~~~~~~~~~~
.. ns-only::

    .. 

This parameter is used to enable or disable trail module.

.. md-tab-set::
    :name: trail-model-enabled-tabs

    .. md-tab-item:: Default configuration

         .. code-block:: python
    
                TRAIL_MODEL_ENABLED = True

    .. md-tab-item:: Example

         .. code-block:: python
    
                TRAIL_MODEL_ENABLED = False

Landedge model enabled
~~~~~~~~~~~~~~~~~~~~~~~

.. ns-only::

    .. 

This parameter is used to enable or disable landedge module.

.. md-tab-set::
    :name: landedge-model-enabled-tabs

    .. md-tab-item:: Default configuration
    
         .. code-block:: python
    
                LANDEDGE_MODEL_ENABLED = True

    .. md-tab-item:: Example

         .. code-block:: python
    
                LANDEDGE_MODEL_ENABLED = False


Tourism enabled
~~~~~~~~~~~~~~~~~

This parameter is used to enable or disable touristic contents or touristic events menus. 

.. md-tab-set::
    :name: tourism-enabled-tabs

    .. md-tab-item:: Default configuration

         .. code-block:: python
    
                TOURISM_ENABLED = True

    .. md-tab-item:: Example

         .. code-block:: python
    
                TOURISM_ENABLED = False

Flatpages enabled
~~~~~~~~~~~~~~~~~~~~

This parameter is used to enable or disable flatpages on menu. Flatpages are used in Geotrek-rando and Geotrek-mobile.

.. md-tab-set::
    :name: flatpages-enabled-tabs

    .. md-tab-item:: Default configuration

         .. code-block:: python
    
                FLATPAGES_ENABLED = True

    .. md-tab-item:: Example

         .. code-block:: python
    
                FLATPAGES_ENABLED = False

Accessibility attachments enabled
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This parameter is used to enable or disable the accessibility menu for attachments.

.. md-tab-set::
    :name: accessibility-attachements-enabled-tabs

    .. md-tab-item:: Default configuration

         .. code-block:: python
    
                ACCESSIBILITY_ATTACHMENTS_ENABLED = True

    .. md-tab-item:: Example

         .. code-block:: python
    
                ACCESSIBILITY_ATTACHMENTS_ENABLED = False

.. note::
  - By doing so, some software upgrades may not be as smooth as usual.
  - Never forget to mention this customization if you ask for community support.

Paths
------

Allow path deletion enabled
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If ``False``, it forbids to delete a path when at least one topology is linked to this path.

.. md-tab-set::
    :name: allow-path-deletion-topology-tabs

    .. md-tab-item:: Default configuration

         .. code-block:: python
    
                ALLOW_PATH_DELETION_TOPOLOGY = False

    .. md-tab-item:: Example

         .. code-block:: python
    
                ALLOW_PATH_DELETION_TOPOLOGY = True

Alert draft
~~~~~~~~~~~~~

If ``True``, it :ref:`sends a message to managers <email-settings>` whenever a path has been changed to draft.

.. md-tab-set::
    :name: alert-draft-tabs

    .. md-tab-item:: Default configuration

         .. code-block:: python
    
                ALERT_DRAFT = False

    .. md-tab-item:: Example

         .. code-block:: python
    
                ALERT_DRAFT = True

Alert review
~~~~~~~~~~~~~

If ``True``, it :ref:`sends a message to managers <email-settings>` whenever an object which can be validated has been changed to review mode.

.. md-tab-set::
    :name: alert-review-tabs

    .. md-tab-item:: Default configuration

         .. code-block:: python
    
                ALERT_REVIEW = False

    .. md-tab-item:: Example

         .. code-block:: python
    
                ALERT_REVIEW = True


Signage and Blade
-------------------

These parameters are used to enable or disable blades and lines submodules.

.. md-tab-set::
    :name: signage-blade-tabs

    .. md-tab-item:: Default configuration

         .. code-block:: python
    
                BLADE_ENABLED = True
                LINE_ENABLED = True

    .. md-tab-item:: Example

         .. code-block:: python
    
                BLADE_ENABLED = False
                LINE_ENABLED = True

These parameters are used to have `direction` field on lines instead of blades.

.. md-tab-set::
    :name: direction-on-lines-enabled-tabs

    .. md-tab-item:: Default configuration

         .. code-block:: python
    
                DIRECTION_ON_LINES_ENABLED = False

    .. md-tab-item:: Example

         .. code-block:: python
    
                DIRECTION_ON_LINES_ENABLED = True

Blade code type
~~~~~~~~~~~~~~~~

You can change the type of the blade code field (string or integer) :

.. md-tab-set::
    :name: blade-code-type-tabs

    .. md-tab-item:: Default configuration

         .. code-block:: python
    
                BLADE_CODE_TYPE = INT

    .. md-tab-item:: Example

         .. code-block:: python
    
                BLADE_CODE_TYPE = STR


Blade code format
~~~~~~~~~~~~~~~~~~

You can change the format of blade codes :

.. md-tab-set::
    :name: blade-code-format-tabs

    .. md-tab-item:: Default configuration

         .. code-block:: python
    
              BLADE_CODE_FORMAT = "{signagecode}-{bladenumber}"

    .. md-tab-item:: Example

        .. info::
            It will display : ``CD99.XIDNZEIU.01 (first blade of XIDNZEIU)``

          .. code-block:: python
      
                BLADE_CODE_FORMAT = "CD99.{signagecode}.{bladenumber}"

        

Line code format
~~~~~~~~~~~~~~~~~

You can change the format of line codes. It is used in the CSV export of lines.

.. md-tab-set::
    :name: line-code-format-tabs

    .. md-tab-item:: Default configuration

         .. code-block:: python
    
              LINE_CODE_FORMAT = "{signagecode}-{bladenumber}-{linenumber}"

    .. md-tab-item:: Example

        .. info::
            It will display : ``CD99.XIDNZEIU-01.02``

          .. code-block:: python
      
                BLADE_CODE_FORMAT = "CD99.{signagecode}-{bladenumber}.{linenumber}"
         
.. _trek-poi-intersection:

POI
----

Trek POI intersection margin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can define buffer around treks to intersects POIs (works only without dynamic segmentation).

.. md-tab-set::
    :name: trek-poi-intersection-marging-tabs

    .. md-tab-item:: Default configuration

         .. code-block:: python
    
                TREK_POI_INTERSECTION_MARGIN = 500  # meters

    .. md-tab-item:: Example

         .. code-block:: python
    
                TREK_POI_INTERSECTION_MARGIN = 800  # meters


Land
-----

You can insert circulation and authorization types with this command :

.. md-tab-set::
    :name: loaddata-circulation-tabs

    .. md-tab-item:: With Debian

         .. code-block:: bash
    
                sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/land/fixtures/circulations.json

    .. md-tab-item:: With Docker

         .. code-block:: python
    
                docker compose run --rm web ./manage.py loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/land/fixtures/circulations.json

.. _outdoor:

Outdoor
--------

Installed app for Outdoor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to enable Outdoor module, in the custom settings file, add the following code:

.. code-block:: python

    INSTALLED_APPS += ('geotrek.outdoor', )

Then run :

.. md-tab-set::
    :name: install-outdoor-tabs

    .. md-tab-item:: With Debian

         .. code-block:: bash
    
                sudo dpkg-reconfigure -pcritical geotrek-admin

    .. md-tab-item:: With Docker

         .. code-block:: python
    
                docker compose run --rm web update.sh

You can also insert Outdoor minimal data:

.. md-tab-set::
    :name: loaddata-outdoor-minimal-data-tabs

    .. md-tab-item:: With Debian

         .. code-block:: bash
    
                sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/outdoor/fixtures/basic.json

    .. md-tab-item:: With Docker

         .. code-block:: python
    
                docker compose run --rm web ./manage.py loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/outdoor/fixtures/basic.json


After installing Outdoor module, you need to add permissions to your user groups on outdoor sites and courses.

.. note::
  - Outdoor module is not compatible with PostGIS <= 2.4 that is included in Ubuntu 18.04.
  - You should either upgrade to Ubuntu 20.04 or upgrade postGIS to 2.5 with https://launchpad.net/~ubuntugis/+archive/ubuntu/ppa

.. _sensitivity:

Sensitive areas
-----------------

.. note::
    The sensitivity module was developed as part of the Biodiv'Sports project to provide a central platform for sensitive areas. 

    The official address of the Geotrek instance of the Biodiv'Sports project is: https://biodiv-sports.fr, and is the base URL for the following API URLs.

Installed app for Sensitive areas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to enable sensitivity module, in the custom settings file, add the following code:

.. code-block:: python

    INSTALLED_APPS += ('geotrek.sensitivity', )


You can insert rules of sensitive area with these commands:

.. md-tab-set::
    :name: loaddata-outdoor-tabs

    .. md-tab-item:: With Debian

         .. code-block:: bash
    
                sudo geotrek loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/sensitivity/fixtures/rules.json
                cp -r /opt/geotrek-admin/lib/python*/site-packages/geotrek/sensitivity/fixtures/upload/rules/ /opt/geotrek-admin/var/media/upload/

    .. md-tab-item:: With Docker

         .. code-block:: python
    
                docker compose run --rm web ./manage.py loaddata /opt/geotrek-admin/lib/python*/site-packages/geotrek/sensitivity/fixtures/rules.json
                cp -r /opt/geotrek-admin/lib/python*/site-packages/geotrek/sensitivity/fixtures/upload/rules/ /opt/geotrek-admin/var/media/upload/

The following settings are related to sensitive areas:

Sensitivity default radius
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can define radius of sensitivity areas when not specified for species :

.. md-tab-set::
    :name: sensitivity-default-radius-tabs

    .. md-tab-item:: Default configuration

         .. code-block:: python
    
                SENSITIVITY_DEFAULT_RADIUS = 100  # meters

    .. md-tab-item:: Example

         .. code-block:: python
    
                SENSITIVITY_DEFAULT_RADIUS = 200  # meters


Sensitive area intersection margin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can define buffer around treks to intersects sensitive areas :

.. md-tab-set::
    :name: sensitive-areas-intersection-margin-tabs

    .. md-tab-item:: Default configuration

         .. code-block:: python
    
                SENSITIVE_AREA_INTERSECTION_MARGIN = 500  # meters

    .. md-tab-item:: Example

         .. code-block:: python
    
                SENSITIVE_AREA_INTERSECTION_MARGIN = 800  # meters

.. notes

    # Take care if you change this value after adding data. You should update buffered geometry in SQL.
    ```UPDATE sensitivity_sensitivearea SET geom_buffered = ST_BUFFER(geom, <your new value>);```

.. seealso::
  
  See :ref:`sensitive-areas-import` to import data.

Zoning
--------

These parameters are used to enable/disable zoning combo-boxes on list map.

.. md-tab-set::
    :name: zoning-combo-boxes-tabs

    .. md-tab-item:: Default configuration

         .. code-block:: python
    
              LAND_BBOX_CITIES_ENABLED = True
              LAND_BBOX_DISTRICTS_ENABLED = True
              LAND_BBOX_AREAS_ENABLED = False

    .. md-tab-item:: Example

         .. code-block:: python
    
              LAND_BBOX_CITIES_ENABLED = False
              LAND_BBOX_DISTRICTS_ENABLED = False
              LAND_BBOX_AREAS_ENABLED = False

.. image:: ../images/advanced-configuration/zoning-combo-boxes.png
   :align: center
   :alt: Zoning combo boxes