.. _introduction-import:

======================
Introduction
======================

Overview
========

Geotrek-admin offers multiple ways to import data, each suited to different contexts and technical needs. Depending on the data source, your level of expertise, or the frequency of updates, one method may be more appropriate than another.

Here is a summary of the available import methods:

- **Parsers** : custom or default, to automate data imports from files or online feeds (e.g. Tourism Information Systems).
- **Command-line `load` commands** : for importing structured geographic data (shapefiles, GeoJSON, Geopackage, etc.).
- **Fixtures** : predefined `.json` files used to populate or reset reference data in the database.
- **Manual import** : entering data directly through the Geotrek-admin web interface.
- **Aggregator** : advanced method to import and consolidate data from multiple remote Geotrek-admin instances.

Choosing the right method
===========================

The table below helps you identify the most appropriate import method based on key criteria.

.. list-table::
   :widths: 25 15 15 20 20
   :header-rows: 1

   * - **Import method**
     - **Automated**
     - **Requires dev skills**
     - **Suitable for**
     - **Examples**
   * - **Parsers**
     - ✅
     - ⚠️ Yes (for custom)
     - Recurring imports, data from feeds or files
     - Cities, POIs, treks, Biodiv'Sport, Apidae, Tourinsoft
   * - **Command-line `load`**
     - ❌
     - ⚠️ Basic command line interface skills
     - One-time
     - Paths, DEM, cities, districts, POIs
   * - **Fixtures**
     - ❌
     - ⚠️ Minimal
     - Initial setup or reset of reference data
     - Practices, zoning types, difficulties, categories, types
   * - **Manual import**
     - ❌
     - ❌ 
     - Occasional edits or new records
     - Adding new POIs or cities
   * - **Aggregator**
     - ✅
     - ✅ 
     - Sync from multiple Geotrek instances
     - Consolidating treks from multiple parks

.. note::
   - **Automated** = Can be scheduled with ``cron`` or updated regularly
   - **Requires dev skills** = Needs code configuration, file templates, or CLI (command line interface) use

Recommendations
=================

- For regular imports from external sources (Tourism Information Systems, Biodiv'Sport, etc.), use **parsers**.
- For importing shapefiles or GeoJSON (e.g. paths, DEM, districts, cities), use **`load` commands** from the CLI.
- To initialize a new Geotrek-admin instance or reset certain reference data, use **fixtures**.
- To edit or add a few individual records, prefer the **manual interface**.
- To aggregate data from multiple Geotrek-admin platforms, use the **aggregator parser**.

.. seealso::

   - :doc:`parsers`
   - :doc:`command-load`
   - :doc:`fixtures`
   - :doc:`aggregator`

