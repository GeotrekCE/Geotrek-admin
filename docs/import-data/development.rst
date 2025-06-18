.. _development-parser-import:

======================
Development 
======================

.. _available-attributs:

Available attributs
===================

+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| **Parameter**              | **Type**| **Description**                                                                                                                                 |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| label                      | str     | Display name shown in the interface to identify this parser.                                                                                    |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| model                      | str     | Name of the data model where the information should be saved.                                                                                   |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| filename                   | str     | Name of the source file containing the data to import.                                                                                          |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| url                        | str     | API address where the data comes from.                                                                                                          |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| simplify_tolerance         | float   | Minimum distance (in meters) between two points of a geographic shape. Points that are too close may be removed to simplify the shape.          |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| update_only                | bool    | If enabled, only existing data can be updated. No new object will be created.                                                                   |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| delete                     | bool    | If enabled, objects no longer present in the new data will be deleted.                                                                          |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| duplicate_eid_allowed      | bool    | If enabled, multiple objects can have the same external identifier.                                                                             |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| fill_empty_translated_fields | bool  | Automatically fills in empty translation fields. *(Description may need refinement as per context.)*                                            |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| warn_on_missing_fields     | bool    | Shows a warning message if expected fields are missing from the imported data.                                                                  |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| warn_on_missing_objects    | bool    | Shows a warning message if expected objects are not found in the imported data.                                                                 |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| separator                  | str     | Character used to separate multiple values in a single cell (e.g., a comma).                                                                    |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| eid                        | str     | Name of the field that contains the unique external identifier for each object.                                                                 |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| provider                   | str     | Name of the source the data comes from (e.g., a partner or an API name).                                                                        |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| fields                     | dict    | Mapping between model fields and source fields. A model field can be linked to multiple source fields.                                          |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| constant_fields            | dict    | Assigns fixed values to specific model fields for every imported object.                                                                        |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| m2m_fields                 | dict    | Mapping between model's many-to-many fields and those from the source.                                                                          |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| m2m_constant_fields        | dict    | Fixed values to be assigned to many-to-many fields for each object.                                                                             |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| m2m_aggregate_fields       | list    | List of many-to-many fields where new data should be added without removing existing data.                                                      |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| non_fields                 | dict    | Mapping of source data to fields not part of the main model (e.g., ancillary data).                                                             |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| natural_keys               | dict    | Indicates which field to use to identify related objects (e.g., for foreign key relationships).                                                 |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| field_options              | dict    | Extra parameters for each field, such as "required" or "create if not exists".                                                                  |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| default_language           | str     | Default language used for imported data.                                                                                                        |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
| intersection_geom          | dict    | Geographic area to restricts imported objects (e.g., a City or District).                                                                       |
+-----------------------------+---------+------------------------------------------------------------------------------------------------------------------------------------------------+
.. _general-architecture:

General architecture
====================

.. mermaid::

   flowchart TD
       PARSE["PARSE<br/>starts data import"] --> START["START<br/>lists database objects"]
       PARSE --> NEXT_ROW["NEXT_ROW<br/>iterates over input rows"]
       PARSE --> PARSE_ROW["PARSE_ROW<br/>handles full row import"]
       PARSE --> END["END<br/>deletes outdated objects"]
       PARSE_ROW --> PARSE_OBJ["PARSE_OBJ<br/>creates/updates object"]
       PARSE_ROW --> GET_EID_KWARGS["GET_EID_KWARGS<br/>gets unique ID"]
       PARSE_OBJ --> PARSE_FIELDS["PARSE_FIELDS<br/>handles all object fields"]
       PARSE_FIELDS --> PARSE_FIELD["PARSE_FIELD<br/>individual field import"]
       PARSE_FIELD --> GET_VAL["GET_VAL<br/>gets field values"]
       PARSE_FIELD --> PARSE_TRANSLATION_FIELD["PARSE_TRANSLATION_FIELD<br/>updates translated field"]
       PARSE_FIELD --> PARSE_REAL_FIELD["PARSE_REAL_FIELD<br/>updates real field"]
       PARSE_FIELD --> PARSE_NON_FIELD["PARSE_NON_FIELD<br/>handles special fields"]
       GET_VAL --> GET_PART["GET_PART<br/>extract nested data"]
       PARSE_TRANSLATION_FIELD --> SET_VALUE["SET_VALUE<br/>save value"]
       PARSE_REAL_FIELD --> SET_VALUE
       PARSE_REAL_FIELD --> APPLY_FILTER["APPLY_FILTER<br/>filter fk/m2m"]

.. _overloadable-existing-parsers:

Overloadable existing parsers
=============================




.. _importing-from-multiple-sources:

Import from multiple sources
============================

When importing data for the same model using two (or more) different sources, the ``provider`` field should be used to differenciate between sources, allowing to enable object deletion with ``delete = True`` without causing the last parser to delete objects created by preceeding parsers.

In the following example, ``Provider_1Parser`` and ``Provider_2Parser`` will each import their objects, set the ``provider`` field on these objects, and only delete objects that disappeared from their respective source since last parsing.

.. code-block:: python

    class Provider_1Parser(XXXXParser):
        delete = True
        provider = "provider_1"

    class Provider_2Parser(XXXParser):
        delete = True
        provider = "provider_2"

.. important::

    - It is recommended to use ``provider`` from the first import.
    - Do not add a ``provider`` field to preexisting parsers that already imported objects, or you will have to manually set the same value for ``provider`` on all objects already created by this parser.
    - If a parser does not have a ``provider`` value, it will not take providers into account, meaning that it could delete objects from preceeding parsers even if these other parsers do have a ``provider`` themselves.

The following example would cause ``NoProviderParser`` to delete objects from ``Provider_2Parser`` and ``Provider_1Parser``.

.. code-block:: python

    class Provider_1Parser(XXXXParser):
        delete = True
        provider = "provider_1"

    class Provider_2Parser(XXXParser):
        delete = True
        provider = "provider_2"

    class NoProviderParser(XXXParser):
        delete = True
        provider = None # (default)

.. seealso::

  To set up automatic commands you can check the :ref:`Automatic commands section <automatic-commands>`.

.. _aggregators:

Aggregators
===========

.. _further_information:

Further information
===================

.. _import-attachments:

Detailed operation of attachment parsing
----------------------------------------

``AttachmentParserMixin`` lets a parser **link (and optionally download) media files** to any object it imports (signage, infrastructures, POIs, touristic content, events, etc).
The mixin is located in ``geotrek/common/parsers.py`` and must be inherited by your parser:

.. code-block:: python

   class ExampleParser(AttachmentParserMixin, Parser):

       # Parser configuration …

.. warning::

   Use ``AttachmentParserMixin`` **only in base parsers**.
   Custom parsers should focus on configuration.
   Factor attachment logic into shared base classes to keep custom parsers clean and maintainable.

Attributes
~~~~~~~~~~

The following attributes can be customized:

* ``download_attachments`` (default: ``True``):
  Whether to download and store attachments via Paperclip. If set to ``False``, attachments are only linked.
  Requires ``PAPERCLIP_ENABLE_LINK = True`` in Django settings.

* ``base_url`` (default: ``""``):
  Base URL prepended to each relative attachment path returned by ``filter_attachments``.

* ``delete_attachments`` (default: ``True``):
  After the new attachments have been processed, **every existing
  attachment that is *not* present in the current feed (or whose file has
  been replaced)** is permanently removed.

* ``filetype_name`` (default: ``"Photographie"``):
  Label of the ``FileType`` model assigned to all imported files.
  If it does not exist in the database, the import will fail with a warning:

  ::

     FileType '<name>' does not exist in Geotrek-Admin. Please add it

* ``non_fields`` (default: ``{"attachments": _("Attachments")}``):
  Maps the internal ``attachments`` field to the field name(s) containing attachments data in the external source.

* ``default_license_label`` (default: ``None``):
  If specified, this license will be assigned to all imported attachments.
  If the license does not exist, it will be created automatically.

Filtering attachments
~~~~~~~~~~~~~~~~~~~~~

The ``filter_attachments`` method formats the external source data to match with the internal format.

If the attachment data has a different structure than the default ``filter_attachments``, the method must be overridden.

See the `geotrek/common/parsers.py/ <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/common/parsers.py/>`_ file to see more about attachments.

.. _geometry-filtering:

Geometry filtering in Geotrek Parsers
-------------------------------------

In some cases, you may want to restrict imported objects to a specific geographic area already defined in geotrek model instance (ex: a City or District).
This can be done by defined the parser’s ``intersection_geom`` attribute

This attribute is a dictionary with the following keys:

- ``model``: The Django model containing the reference geometry object.
- ``app_label``: The Django application where the model is defined.
- ``geom_field``: The name of the geometry field in the model.
- ``object_filter``: A dictionary to identify the reference object (e.g., using an ID).

The ``object_filter`` must return exactly one object:

- If no object is found, the parser raises a **blocking error**.
- If multiple objects are returned, only the **first** will be used, which may cause unexpected behavior.

Conditional Deletion with ``delete = True``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If ``delete`` attribut is set to ``True``, the parser will automatically **delete existing objects** of the current model
that **do not intersect** the reference geometry.

.. note::

   Deletion only affects objects of the model handled by the current parser. Other models are not impacted.
