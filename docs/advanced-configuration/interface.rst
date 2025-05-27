.. _interface:

============
Interface
============

.. info::

  For a complete list of available parameters, refer to the default values in `geotrek/settings/base.py <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/settings/base.py>`_.

Configure columns displayed in lists views and exports
--------------------------------------------------------

You can customize the columns displayed in list views and data exports for each module.

To configure which columns appear in the main table view for a specific module, use the following syntax:

.. md-tab-set::
    :name: module-view-list-columns-tabs

    .. md-tab-item:: Syntax

        .. code-block:: python

              COLUMNS_LISTS['<module>_view'] = ['list', 'of', 'columns']

    .. md-tab-item:: Example

         .. code-block:: python

              COLUMNS_LISTS['trek_view'] = [
              'structure',
              'departure',
              'arrival',
              'duration',
              'description_teaser',
              'description',
              'gear',
              'route',
              'difficulty',
              'ambiance',
              'access',
              'themes',
              'practice']

To define which columns should be included when exporting data to CSV or SHP formats, use the syntax below:

.. md-tab-set::
    :name: module-view-list-columns-export-tabs

    .. md-tab-item:: Syntax

        .. code-block:: python

              COLUMNS_LISTS['<module>_export'] = ['list', 'of', 'columns']

    .. md-tab-item:: Example

         .. code-block:: python

              COLUMNS_LISTS['outdoor_site_export'] = [
                    'structure',
                    'name',
                    'practice',
                    'description',
                    'description_teaser',
                    'ambiance',
                    'advice',
                    'accessibility',
                    'period',
                    'labels',
                    'themes',
                    'portal',
                    'source',
                    'information_desks',
                    'orientation',
                    'wind'
                ]

Enable jobs cost detailed export
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, job cost details are not included in intervention exports. You can enable a more detailed export by setting the following parameter:

.. md-tab-set::
    :name: enable-job-costs-detailed-export-tabs

    .. md-tab-item:: Default configuration

            .. code-block:: python

                ENABLE_JOBS_COSTS_DETAILED_EXPORT = False
    .. md-tab-item:: Example

         .. code-block:: python

                ENABLE_JOBS_COSTS_DETAILED_EXPORT = True

When enabled, a new column will be added to intervention exports, displaying the total cost for each job.

Custom columns available
~~~~~~~~~~~~~~~~~~~~~~~~~

A complete list of attributes that can be used for displaying or exporting columns is available. You can customize these based on your requirements.

.. example:: List of available attributes for displaying
    :collapsible:

    ::

      COLUMNS_LISTS["path_view"] = [
          "length_2d",
          "valid",
          "structure",
          "visible",
          "min_elevation",
          "max_elevation",
          "date_update",
          "date_insert",
          "stake",
          "networks",
          "comments",
          "departure",
          "arrival",
          "comfort",
          "source",
          "usages",
          "draft",
          "trails",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["trail_view"] = [
          "departure",
          "arrival",
          "category",
          "length",
          "structure",
          "min_elevation",
          "max_elevation",
          "date_update",
          "length_2d",
          "date_insert",
          "comments",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["landedge_view"] = [
          "eid",
          "min_elevation",
          "max_elevation",
          "date_update",
          "length_2d",
          "date_insert",
          "owner",
          "agreement",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["circulationedge_view"] = [
          "eid",
          "min_elevation",
          "max_elevation",
          "date_update",
          "length_2d",
          "date_insert",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["physicaledge_view"] = [
          "eid",
          "date_insert",
          "date_update",
          "length",
          "length_2d",
          "min_elevation",
          "max_elevation",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["competenceedge_view"] = [
          "eid",
          "date_insert",
          "date_update",
          "length",
          "length_2d",
          "min_elevation",
          "max_elevation",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["infrastructure_view"] = [
          "condition",
          "cities",
          "structure",
          "type",
          "description",
          "accessibility",
          "date_update",
          "date_insert",
          "implantation_year",
          "usage_difficulty",
          "maintenance_difficulty",
          "published",
          "uuid",
          "eid",
          "provider",
          "access",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["signage_view"] = [
          "code",
          "type",
          "condition",
          "structure",
          "description",
          "date_update",
          "date_insert",
          "implantation_year",
          "printed_elevation",
          "coordinates",
          "sealing",
          "access",
          "manager",
          "published",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["intervention_view"] = [
          "begin_date",
          "end_date",
          "type",
          "target",
          "status",
          "stake",
          "structure",
          "subcontracting",
          "status",
          "disorders",
          "length",
          "material_cost",
          "min_elevation",
          "max_elevation",
          "heliport_cost",
          "contractor_cost",
          "date_update",
          "date_insert",
          "description",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["project_view"] = [
          "structure",
          "begin_year",
          "end_year",
          "constraint",
          "global_cost",
          "type",
          "date_update",
          "domain",
          "contractors",
          "project_owner",
          "project_manager",
          "founders",
          "date_insert",
          "comments",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["trek_view"] = [
          "structure",
          "departure",
          "arrival",
          "duration",
          "description_teaser",
          "description",
          "gear",
          "route",
          "difficulty",
          "ambiance",
          "access",
          "accessibility_infrastructure",
          "advised_parking",
          "parking_location",
          "public_transport",
          "themes",
          "practice",
          "min_elevation",
          "max_elevation",
          "length_2d",
          "date_update",
          "date_insert",
          "accessibilities",
          "accessibility_advice",
          "accessibility_covering",
          "accessibility_exposure",
          "accessibility_level",
          "accessibility_signage",
          "accessibility_slope",
          "accessibility_width",
          "ratings_description",
          "ratings",
          "points_reference",
          "source",
          "reservation_system",
          "reservation_id",
          "portal",
          "uuid",
          "eid",
          "eid2",
          "provider",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["poi_view"] = [
          "structure",
          "description",
          "type",
          "min_elevation",
          "date_update",
          "date_insert",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["service_view"] = [
          "structure",
          "min_elevation",
          "type",
          "length_2d",
          "date_update",
          "date_insert",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["touristic_content_view"] = [
          "structure",
          "description_teaser",
          "description",
          "category",
          "contact",
          "email",
          "website",
          "practical_info",
          "accessibility",
          "label_accessibility",
          "type1",
          "type2",
          "source",
          "reservation_system",
          "reservation_id",
          "date_update",
          "date_insert",
          "uuid",
          "eid",
          "provider"
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["touristic_event_view"] = [
          "structure",
          "themes",
          "description_teaser",
          "description",
          "meeting_point",
          "start_time",
          "end_time",
          "duration",
          "begin_date",
          "contact",
          "email",
          "website",
          "end_date",
          "organizers",
          "speaker",
          "type",
          "accessibility",
          "capacity",
          "portal",
          "source",
          "practical_info",
          "target_audience",
          "booking",
          "date_update",
          "date_insert",
          "uuid",
          "eid",
          "provider",
          "bookable",
          "cancelled",
          "cancellation_reason"
          "place",
          'preparation_duration',
          'intervention_duration',
          'price',
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["feedback_view"] = [
          "email",
          "comment",
          "activity",
          "category",
          "problem_magnitude",
          "status",
          "related_trek",
          "uuid",
          "eid",
          "external_eid",
          "locked",
          "origin"
          "date_update",
          "date_insert",
          "created_in_suricate",
          "last_updated_in_suricate",
          "current_user",
          "uses_timers",
          "provider",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["sensitivity_view"] = [
          "structure",
          "species",
          "published",
          "publication_date",
          "contact",
          "pretty_period",
          "category",
          "pretty_practices",
          "description",
          "date_update",
          "date_insert",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["outdoor_site_view"] = [
          "structure",
          "name",
          "practice",
          "description",
          "description_teaser",
          "ambiance",
          "advice",
          "accessibility",
          "period",
          "labels",
          "themes",
          "portal",
          "source",
          "information_desks",
          "web_links",
          "eid",
          "orientation",
          "wind",
          "ratings",
          "managers",
          "type",
          "description",
          "description_teaser",
          "ambiance",
          "period",
          "orientation",
          "wind",
          "labels",
          "themes",
          "portal",
          "source",
          "managers",
          "min_elevation",
          "date_insert",
          "date_update",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["outdoor_course_view"] = [
          "structure",
          "name",
          "parent_sites",
          "description",
          "advice",
          "equipment",
          "accessibility",
          "eid",
          "height",
          "ratings",
          "gear",
          "duration"
          "ratings_description",
          "type",
          "points_reference",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]

.. example:: List of available attributes for exporting
    :collapsible:

    ::

      COLUMNS_LISTS["path_export"] = [
          "structure",
          "valid",
          "visible",
          "name",
          "comments",
          "departure",
          "arrival",
          "comfort",
          "source",
          "stake",
          "usages",
          "networks",
          "date_insert",
          "date_update",
          "length_2d",
          "length",
          "ascent",
          "descent",
          "min_elevation",
          "max_elevation",
          "slope",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["trail_export"] = [
          "structure",
          "name",
          "comments",
          "departure",
          "arrival",
          "category",
          "certifications",
          "date_insert",
          "date_update",
          "cities",
          "districts",
          "areas",
          "length",
          "ascent",
          "descent",
          "min_elevation",
          "max_elevation",
          "slope",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["signagemanagementedge_export"] = [
          "eid",
          "date_insert",
          "date_update",
          "length",
          "length_2d",
          "min_elevation",
          "max_elevation",
          "uuid",
          "provider",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["workmanagementedge_export"] = [
          "eid",
          "date_insert",
          "date_update",
          "length",
          "length_2d",
          "min_elevation",
          "max_elevation",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["landedge_export"] = [
          "eid",
          "land_type",
          "owner",
          "agreement",
          "date_insert",
          "date_update",
          "cities",
          "districts",
          "areas",
          "length",
          "length_2d",
          "ascent",
          "descent",
          "min_elevation",
          "max_elevation",
          "slope",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["circulationedge_export"] = [
          "eid",
          "circulation_type",
          "authorization_type",
          "date_insert",
          "date_update",
          "cities",
          "districts",
          "areas",
          "length",
          "length_2d",
          "ascent",
          "descent",
          "min_elevation",
          "max_elevation",
          "slope",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["physicaledge_export"] = [
          "eid",
          "physical_type",
          "date_insert",
          "date_update",
          "cities",
          "districts",
          "areas",
          "length",
          "length_2d",
          "ascent",
          "descent",
          "min_elevation",
          "max_elevation",
          "slope",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["competenceedge_export"] = [
          "eid",
          "organization",
          "date_insert",
          "date_update",
          "cities",
          "districts",
          "areas",
          "length",
          "length_2d",
          "ascent",
          "descent",
          "min_elevation",
          "max_elevation",
          "slope",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["signagemanagementedge_export"] = [
          "eid",
          "organization",
          "date_insert",
          "date_update",
          "cities",
          "districts",
          "areas",
          "length",
          "length_2d",
          "ascent",
          "descent",
          "min_elevation",
          "max_elevation",
          "slope",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["workmanagementedge_export"] = [
          "eid",
          "organization",
          "date_insert",
          "date_update",
          "cities",
          "districts",
          "areas",
          "length",
          "length_2d",
          "ascent",
          "descent",
          "min_elevation",
          "max_elevation",
          "slope",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["infrastructure_export"] = [
          "name",
          "type",
          "condition",
          "access",
          "description",
          "accessibility",
          "implantation_year",
          "published",
          "publication_date",
          "structure",
          "date_insert",
          "date_update",
          "cities",
          "districts",
          "areas",
          "ascent",
          "descent",
          "min_elevation",
          "max_elevation",
          "slope",
          "usage_difficulty",
          "maintenance_difficulty"
          "uuid",
          "eid",
          "provider",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["signage_export"] = [
          "structure",
          "name",
          "code",
          "type",
          "condition",
          "description",
          "implantation_year",
          "published",
          "date_insert",
          "date_update",
          "cities",
          "districts",
          "areas",
          "lat_value",
          "lng_value",
          "printed_elevation",
          "sealing",
          "access",
          "manager",
          "length",
          "ascent",
          "descent",
          "min_elevation",
          "max_elevation",
          "uuid",
          "eid",
          "provider",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["intervention_export"] = [
          "name",
          "begin_date",
          "end_date",
          "type",
          "target",
          "status",
          "stake",
          "disorders",
          "total_manday",
          "project",
          "subcontracting",
          "width",
          "height",
          "length",
          "area",
          "structure",
          "description",
          "date_insert",
          "date_update",
          "material_cost",
          "heliport_cost",
          "contractor_cost",
          "total_cost_mandays",
          "total_cost",
          "cities",
          "districts",
          "areas",
          "length",
          "ascent",
          "descent",
          "min_elevation",
          "max_elevation",
          "slope",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["project_export"] = [
          "structure",
          "name",
          "period",
          "type",
          "domain",
          "constraint",
          "global_cost",
          "interventions",
          "interventions_total_cost",
          "comments",
          "contractors",
          "project_owner",
          "project_manager",
          "founders",
          "date_insert",
          "date_update",
          "cities",
          "districts",
          "areas",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["trek_export"] = [
          "eid",
          "eid2",
          "structure",
          "name",
          "departure",
          "arrival",
          "duration",
          "duration_pretty",
          "description",
          "description_teaser",
          "gear",
          "networks",
          "advice",
          "ambiance",
          "difficulty",
          "information_desks",
          "themes",
          "practice",
          "accessibilities",
          "accessibility_advice",
          "accessibility_covering",
          "accessibility_exposure",
          "accessibility_level",
          "accessibility_signage",
          "accessibility_slope",
          "accessibility_width",
          "ratings_description",
          "ratings",
          "access",
          "route",
          "public_transport",
          "advised_parking",
          "web_links",
          "labels",
          "accessibility_infrastructure",
          "parking_location",
          "points_reference",
          "children",
          "parents",
          "pois",
          "review",
          "published",
          "publication_date",
          "date_insert",
          "date_update",
          "cities",
          "districts",
          "areas",
          "source",
          "portal",
          "length_2d",
          "length",
          "ascent",
          "descent",
          "min_elevation",
          "max_elevation",
          "slope",
          "uuid",
          "provider",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["poi_export"] = [
          "structure",
          "eid",
          "name",
          "type",
          "description",
          "treks",
          "review",
          "published",
          "publication_date",
          "structure",
          "date_insert",
          "date_update",
          "cities",
          "districts",
          "areas",
          "length",
          "ascent",
          "descent",
          "min_elevation",
          "max_elevation",
          "slope",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["service_export"] = [
          "eid",
          "type",
          "length",
          "ascent",
          "descent",
          "min_elevation",
          "max_elevation",
          "slope",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["dive_export"] = [
          "eid",
          "structure",
          "name",
          "departure",
          "description",
          "description_teaser",
          "advice",
          "difficulty",
          "levels",
          "themes",
          "practice",
          "disabled_sport",
          "published",
          "publication_date",
          "date_insert",
          "date_update",
          "areas",
          "source",
          "portal",
          "review",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["touristic_content_export"] = [
          "structure",
          "eid",
          "name",
          "category",
          "type1",
          "type2",
          "description_teaser",
          "description",
          "themes",
          "contact",
          "email",
          "website",
          "practical_info",
          "accessibility",
          "label_accessibility",
          "review",
          "published",
          "publication_date",
          "source",
          "portal",
          "date_insert",
          "date_update",
          "cities",
          "districts",
          "areas",
          "approved",
          "uuid",
          "provider",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["touristic_event_export"] = [
          "structure",
          "eid",
          "name",
          "type",
          "description_teaser",
          "description",
          "themes",
          "begin_date",
          "end_date",
          "duration",
          "meeting_point",
          "start_time",
          "end_time",
          "contact",
          "email",
          "website",
          "organizers",
          "speaker",
          "accessibility",
          "capacity",
          "booking",
          "target_audience",
          "practical_info",
          "date_insert",
          "date_update",
          "source",
          "portal",
          "review",
          "published",
          "publication_date",
          "cities",
          "districts",
          "areas",
          "approved",
          "uuid",
          "provider",
          "bookable",
          "cancelled",
          "cancellation_reason"
          "place",
          'preparation_duration',
          'intervention_duration',
          'price',
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["feedback_export"] = [
          "comment",
          "activity",
          "category",
          "problem_magnitude",
          "status",
          "related_trek",
          "uuid",
          "eid",
          "external_eid",
          "locked",
          "origin"
          "date_update",
          "date_insert",
          "created_in_suricate",
          "last_updated_in_suricate",
          "current_user",
          "assigned_handler",
          "uses_timers",
          "provider",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["sensitivity_export"] = [
          "species",
          "published",
          "description",
          "contact",
          "pretty_period",
          "pretty_practices",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["outdoor_site_export"] = [
          "structure",
          "name",
          "practice",
          "description",
          "description_teaser",
          "ambiance",
          "advice",
          "accessibility",
          "period",
          "information_desks",
          "web_links",
          "eid",
          "ratings",
          "type",
          "description",
          "description_teaser",
          "ambiance",
          "period",
          "orientation",
          "wind",
          "labels",
          "themes",
          "portal",
          "source",
          "managers",
          "min_elevation",
          "date_insert",
          "date_update",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]
      COLUMNS_LISTS["outdoor_course_export"] = [
          "structure",
          "name",
          "parent_sites",
          "description",
          "advice",
          "equipment",
          "accessibility",
          "eid",
          "height",
          "ratings",
          "gear",
          "duration"
          "ratings_description",
          "type",
          "points_reference",
          "uuid",
          "last_author",
          "creator",
          "authors",
      ]

.. note::
  
  - You can find all mandatory, default, and searchable columns for each module directly in the Geotrek-admin source code. For example, these are the properties for `outdoor_site_view <https://github.com/GeotrekCE/Geotrek-admin/blob/master/geotrek/outdoor/views.py#L35>`_ :

    .. code-block:: python

      mandatory_columns = ["id", "name"]
      default_extra_columns = ["super_practices", "date_update"]
      searchable_columns = ["id", "name"]

  - ``mandatory_columns`` defines the list of columns required for displaying and exporting the view's list.
  - ``default_extra_columns`` defines the list of columns included in the default export
  - ``searchable_columns`` defines the columns on which it will be possible to perform a search in the view's list. For example, for outdoor sites, it is possible to search by ``name`` or ``id``, but not by ``practice``.



Configure form fields in creation views
-----------------------------------------

Hidden form fields
~~~~~~~~~~~~~~~~~~~~

For each module, use the following syntax to configure fields to hide in the creation form.

.. md-tab-set::
    :name: module-view-hidden-columns-export-tabs

    .. md-tab-item:: Syntax

        .. code-block:: python

              HIDDEN_FORM_FIELDS['<module>'] = ['list', 'of', 'fields']

    .. md-tab-item:: Example

         .. code-block:: python

              HIDDEN_FORM_FIELDS['signage'] = [
                      'condition',
                      'description',
                      'implantation_year',
                      'code'
                  ]

Hideable form fields
^^^^^^^^^^^^^^^^^^^^^

.. example:: Exhaustive list of form fields hideable in each module
    :collapsible:

    ::

      HIDDEN_FORM_FIELDS["path"] = [
              "departure",
              "name",
              "stake",
              "comfort",
              "arrival",
              "comments",
              "source",
              "networks",
              "usages",
              "valid",
              "draft",
              "reverse_geom",
          ],
      HIDDEN_FORM_FIELDS["trek"] = [
              "structure",
              "name",
              "review",
              "published",
              "labels",
              "departure",
              "arrival",
              "duration",
              "difficulty",
              "gear",
              "route",
              "ambiance",
              "access",
              "description_teaser",
              "description",
              "points_reference",
              "accessibility_infrastructure",
              "advised_parking",
              "parking_location",
              "public_transport",
              "advice",
              "themes",
              "networks",
              "practice",
              "accessibilities",
              "accessibility_advice",
              "accessibility_covering",
              "accessibility_exposure",
              "accessibility_level",
              "accessibility_signage",
              "accessibility_slope",
              "accessibility_width",
              "web_links",
              "information_desks",
              "source",
              "portal",
              "children_trek",
              "eid",
              "eid2",
              "ratings",
              "ratings_description",
              "reservation_system",
              "reservation_id",
              "pois_excluded",
              "hidden_ordered_children",
          ],
      HIDDEN_FORM_FIELDS["trail"] = [
              "departure",
              "arrival",
              "comments",
              "category",
          ],
      HIDDEN_FORM_FIELDS["landedge"] = [
              "owner",
              "agreement"
          ],
      HIDDEN_FORM_FIELDS["infrastructure"] = [
              "condition",
              "access",
              "description",
              "accessibility",
              "published",
              "implantation_year",
              "usage_difficulty",
              "maintenance_difficulty"
          ],
      HIDDEN_FORM_FIELDS["signage"] = [
              "condition",
              "description",
              "published",
              "implantation_year",
              "code",
              "printed_elevation",
              "manager",
              "sealing",
              "access"
          ],
      HIDDEN_FORM_FIELDS["intervention"] = [
              "disorders",
              "description",
              "type",
              "subcontracting",
              "end_date",
              "length",
              "width",
              "height",
              "stake",
              "project",
              "material_cost",
              "heliport_cost",
              "contractor_cost",
          ],
      HIDDEN_FORM_FIELDS["project"] = [
              "type",
              "domain",
              "end_year",
              "constraint",
              "global_cost",
              "comments",
              "project_owner",
              "project_manager",
              "contractors",
          ],
      HIDDEN_FORM_FIELDS["site"] = [
              "parent",
              "review",
              "published",
              "practice",
              "description_teaser",
              "description",
              "ambiance",
              "advice",
              "period",
              "orientation",
              "wind",
              "labels",
              "themes",
              "information_desks",
              "web_links",
              "portal",
              "source",
              "managers",
              "eid"
          ],
      HIDDEN_FORM_FIELDS["course"] = [
              "review",
              "published",
              "description",
              "advice",
              "equipment",
              "accessibility",
              "height",
              "children_course",
              "eid",
              "gear",
              "duration"
              "ratings_description",
          ]
      HIDDEN_FORM_FIELDS["poi"] = [
              "review",
              "published",
              "description",
              "eid",
          ],
      HIDDEN_FORM_FIELDS["service"] = [
              "eid",
          ],
      HIDDEN_FORM_FIELDS["dive"] = [
              "review",
              "published",
              "practice",
              "advice",
              "description_teaser",
              "description",
              "difficulty",
              "levels",
              "themes",
              "owner",
              "depth",
              "facilities",
              "departure",
              "disabled_sport",
              "source",
              "portal",
              "eid",
          ],
      HIDDEN_FORM_FIELDS["touristic_content"] = [
              'label_accessibility'
              'type1',
              'type2',
              'review',
              'published',
              'accessibility',
              'description_teaser',
              'description',
              'themes',
              'contact',
              'email',
              'website',
              'practical_info',
              'approved',
              'source',
              'portal',
              'eid',
              'reservation_system',
              'reservation_id'
          ],
      HIDDEN_FORM_FIELDS["touristic_event"] = [
              'review',
              'published',
              'description_teaser',
              'description',
              'themes',
              'end_date',
              'duration',
              'meeting_point',
              'start_time',
              'end_time',
              'contact',
              'email',
              'website',
              'organizers',
              'speaker',
              'type',
              'accessibility',
              'capacity',
              'booking',
              'target_audience',
              'practical_info',
              'approved',
              'source',
              'portal',
              'eid',
              "bookable",
              'cancelled',
              'cancellation_reason'
              'place',
              'preparation_duration',
              'intervention_duration',
              'price'
          ],
      HIDDEN_FORM_FIELDS["report"] = [
              "email",
              "comment",
              "activity",
              "category",
              "problem_magnitude",
              "related_trek",
              "status",
              "locked",
              "uid",
              "origin",
              "current_user",
              "uses_timers"
          ],
      HIDDEN_FORM_FIELDS["sensitivity_species"] = [
              "contact",
              "published",
              "description",
          ],
      HIDDEN_FORM_FIELDS["sensitivity_regulatory"] = [
              "contact",
              "published",
              "description",
              "pictogram",
              "elevation",
              "url",
              "period01",
              "period02",
              "period03",
              "period04",
              "period05",
              "period06",
              "period07",
              "period08",
              "period09",
              "period10",
              "period11",
              "period12",
          ],
      HIDDEN_FORM_FIELDS["blade"] = [
              "condition",
              "color",
          ],
      HIDDEN_FORM_FIELDS["report"] = [
              "comment",
              "activity",
              "category",
              "problem_magnitude",
              "related_trek",
              "status",
              "locked",
              "uid",
              "origin"
          ],
      HIDDEN_FORM_FIELDS["circulationedge"] = [
          ]

.. note::

  By default, the *current_user* field is hidden in ``HIDDEN_FORM_FIELDS['report']``. To make it visible, set:

  .. code-block:: python

    HIDDEN_FORM_FIELDS['report'] = []

Configure form fields required or needed for review or publication
-------------------------------------------------------------------

Completeness level
~~~~~~~~~~~~~~~~~~~

Controls the strictness of completeness checks:

.. md-tab-set::
    :name: completeness-checks-tabs

    .. md-tab-item:: Default configuration

        .. code-block:: python

              COMPLETENESS_LEVEL = 'warning'

    .. md-tab-item:: Example

         .. code-block:: python

              COMPLETENESS_LEVEL = 'error_on_publication'

.. info::

  Set ``error_on_publication`` to avoid publication without completeness fields and ``error_on_review`` if you want this fields to be required before sending to review.


Completeness fields
~~~~~~~~~~~~~~~~~~~~~

Define which fields are mandatory before review or publication:

.. md-tab-set::
    :name: completeness-fields-tabs

    .. md-tab-item:: Default configuration

        .. code-block:: python

              COMPLETENESS_FIELDS = {
              'trek': ['practice', 'departure', 'duration', 'difficulty', 'description_teaser'],
              'dive': ['practice', 'difficulty', 'description_teaser'],
              }

    .. md-tab-item:: Example

         .. code-block:: python

              COMPLETENESS_FIELDS = {
              'trek': ['practice', 'departure', 'duration', 'difficulty', 'description_teaser'],
              'signage': ['code', 'type', 'condition','description','sealing'],
              'intervention': ['begin_date', 'end_date', 'status','material_cost','description'],
              }




