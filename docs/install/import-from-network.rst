====================
Import from network
====================

.. contents::
   :local:
   :depth: 2

.. _import-data-from-a-remote-geotrek-instance:

Import data from a remote Geotrek-admin instance
===========================================

Importing from a Geotrek-admin instance works the same way as from SIT.
A usecase for this is to aggregate data from several Geotrek-admin instance.

.. danger::
    Importing data from a remote Geotrek-admin instance does not work with dynamic segmentation, your instance where you import data
    must have dynamic segmentation disabled.


For example, to import treks from another instance,
edit ``/opt/geotrek-admin/var/conf/parsers.py`` file with the following content:

.. code-block:: python

    class DemoGeotrekTrekParser(BaseGeotrekTrekParser):
        url = "https://remote-geotrek-admin.net"  # replace url with remote instance url
        delete = False
        field_options = {
            'difficulty': {'create': True, },
            'route': {'create': True, },
            'themes': {'create': True},
            'practice': {'create': True},
            'accessibilities': {'create': True},
            'networks': {'create': True},
            'geom': {'required': True},
            'labels': {'create': True},
        }

Then run in command line

.. code-block:: bash

    sudo geotrek import DemoGeotrekTrekParser

Treks are now imported into your own instance.

.. _sensitive-areas-import:

Sensitive Areas Import
=======================

Geotrek provides tools to import sensitive areas data when the module is enabled. The imports can be done through the web interface or the command line. Below are the available options:

Import from Biodiv'Sports
----------------------------

Automatically import sensitive areas from Biodiv'Sports:

- **From the web interface**:

  1. Click on the **user button** (top-right corner) and go to **Imports**.
  2. Under **Data to import from network**, select **Biodiv'Sports** and click **Import**.
  3. Wait for the import process to complete.
  4. Check the Sensitivity module in Geotrek to view the imported data.

  .. warning::
    If no data appears, Biodiv'Sports might not have data for your region. Consider adding your data directly to Biodiv'Sports for shared access across users.

- **From the command line**:

  Run the following command:

.. code-block:: bash

    sudo geotrek import geotrek.sensitivity.parsers.BiodivParser

Import from a Shapefile
--------------------------

Sensitive areas can also be imported from an ESRI Shapefile (zipped). Ensure the following:

- The archive must include ``.shp``, ``.shx``, ``.dbf``, ``.prj``, etc.
- Field names must be configured correctly, as detailed below.

  **Species sensitive areas**:

  - ``espece``: Species name (required, must exist in Biodiv'Sports).
  - ``contact``: Optional contact information (text or HTML).
  - ``descriptio``: Optional description (text or HTML).

  **Regulatory sensitive areas**:

  - ``name``: Area name (required).
  - ``contact``: Optional contact information (text or HTML).
  - ``descriptio``: Optional description (text or HTML).
  - ``periode``: Months during which the area is sensitive (comma-separated, e.g., ``6,7,8`` for June-August).
  - ``practices``: Practices associated with the area (comma-separated).
  - ``url``: Optional URL for the record.

  .. warning::
    Field names in shapefiles are limited to 10 characters (e.g., ``descriptio``).

- **From the web interface**:

  1. Click on the **user button** (top-right corner) and go to **Imports**.
  2. Select the data type (**species** or **regulatory area**).
  3. Upload the zipped shapefile and select the appropriate encoding (UTF-8 or Windows-1252).
  4. Click **Import** and monitor the progress.
  5. View the import report for details.

  .. figure:: ../images/advanced-configuration/import_shapefile.png
     :alt: Import shapefile in user interface
     :align: center

     Import shapefile in user interface

- **From the command line**:

For species sensitive areas:

.. code-block:: bash

    sudo geotrek import
    geotrek.sensitivity.parsers.SpeciesSensitiveAreaShapeParser <file.zip>

For regulatory sensitive areas:

  .. code-block:: bash

      sudo geotrek import geotrek.sensitivity.parsers.RegulatorySensitiveAreaShapeParser <file.zip>

  .. warning::
    Re-importing the same file will create duplicates.

