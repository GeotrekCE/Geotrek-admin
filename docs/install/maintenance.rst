===========
Maintenance
===========


Operating system updates
------------------------

.. code-block:: bash

    sudo apt-get update
    sudo apt-get dist-upgrade


Application backup
------------------

Database

.. code-block:: bash

    sudo -u postgres pg_dump --no-acl --no-owner -Fc geotrekdb > `date +%Y%m%d%H%M`-database.backup

Media files

.. code-block:: bash

    tar -zcvf `date +%Y%m%d%H%M`-media.tar.gz /opt/geotrek-admin/var/media/

Configuration

.. code-block:: bash

    tar -zcvf `date +%Y%m%d%H%M`-conf.tar.gz /opt/geotrek-admin/var/conf/


Application restore
-------------------

If you restore Geotrek-admin on a new server, you will have to install PostgreSQL and PostGIS and create a database user first.
Otherwise go directly to the database creation step.

Example for Ubuntu 18:

.. code-block:: bash

    sudo apt install postgresql-10 postgresql-10-postgis-2.5
    sudo -u postgres psql -c "CREATE USER geotrek PASSWORD 'geotrek';"


Create an empty database (``geotrekdb`` in this example):

.. code-block:: bash

    sudo -u postgres psql -c "CREATE DATABASE geotrekdb OWNER geotrek ENCODING 'UTF8' TEMPLATE template0;"
    sudo -u postgres psql -d geotrekdb -c "CREATE EXTENSION postgis;"
    sudo -u postgres psql -d geotrekdb -c "CREATE EXTENSION postgis_raster;"
    sudo -u postgres psql -d geotrekdb -c "CREATE EXTENSION pgcrypto;"


Restore backup:

.. code-block:: bash

    sudo -u postgres pg_restore -d geotrekdb 20200510-geotrekdb.backup

If errors occurs on restore, try to add ``--clean`` option.

If errors persists, rename your database and recreate a fresh one, then restore.

Extract media and configuration files:

.. code-block:: bash

    tar -zxvf 20200510-media.tar.gz
    tar -zxvf 20200510-conf.tar.gz

Follow *Fresh installation* method. Choose to manage database by yourself.


PostgreSQL optimization
-----------------------

* Increase ``shared_buffers`` and ``work_mem`` according to your RAM

* `Log long queries <http://wiki.postgresql.org/wiki/Logging_Difficult_Queries>`_

* Use `pg activity <https://github.com/julmon/pg_activity#readme>`_ for monitoring


Access your database securely on your local machine (QGIS)
----------------------------------------------------------

Instead of opening your database to the world (by opening the 5432 port for
example), you can use `SSH tunnels <http://www.postgresql.org/docs/9.3/static/ssh-tunnels.html>`_.


Major evolutions
----------------

Tables and Columns name changes in version 2.32.7
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tables and column name were previously set in french, and from this version they get the default name given by Django models name.

Tables names

- geotrek.o_b_cirkwi_tag -> public.cirkwi_cirkwitag
- geotrek.o_b_cirkwi_locomotion -> public.cirkwi_cirkwilocomotion
- geotrek.o_b_cirkwi_poi_category -> public.cirkwi_cirkwipoicategory
- geotrek.m_b_organisme -> public.common_organism
- geotrek.fl_b_fichier -> public.common_filetype
- geotrek.fl_t_fichier -> public.common_attachment
- geotrek.o_b_theme -> public.common_theme
- geotrek.o_b_source_fiche -> public.common_recordsource
- geotrek.o_b_target_portal -> public.common_targetportal
- geotrek.l_r_troncon_usage -> public.core_path_usages
- geotrek.l_r_troncon_reseau -> public.core_path_networks
- geotrek.l_t_troncon -> public.core_path
- geotrek.e_t_evenement -> public.core_topology
- geotrek.e_r_evenement_troncon -> public.core_pathaggregation
- geotrek.l_b_source_troncon -> public.core_pathsource
- geotrek.l_b_enjeu -> public.core_stake
- geotrek.l_b_confort -> public.core_comfort
- geotrek.l_b_usage -> public.core_usage
- geotrek.l_b_reseau -> public.core_network
- geotrek.l_t_sentier -> public.core_trail
- trekking.g_b_pratique -> public.trekking_practice
- trekking.g_b_difficulte -> public.trekking_difficulty
- trekking.g_b_niveau -> public.trekking_level
- trekking.g_r_plongee_niveau -> public.diving_dive_levels
- trekking.g_r_plongee_theme -> public.diving_dive_themes
- trekking.g_r_plongee_source -> public.diving_dive_source
- trekking.g_r_plongee_portal -> public.diving_dive_portal
- trekking.g_t_plongee -> public.diving_dive
- management.f_t_signalement -> public.feedback_report
- management.f_b_categorie -> public.feedback_reportcategory
- management.f_b_status -> public.feedback_reportstatus
- geotrek.t_r_page_source -> public.flatpages_flatpage_source
- geotrek.t_r_page_portal -> public.flatpages_flatpage_portal
- geotrek.p_t_page -> public.flatpages_flatpage
- management.a_b_infrastructure -> public.infrastructure_infrastructuretype
- management.a_b_etat -> public.infrastructure_infrastructurecondition
- management.a_t_infrastructure -> public.infrastructure_infrastructure
- land.f_b_nature -> public.land_physicaltype
- land.f_t_nature -> public.land_physicaledge
- land.f_b_foncier -> public.land_landtype
- land.f_t_foncier -> public.land_landedge
- land.f_t_competence -> public.land_competenceedge
- land.f_t_gestion_travaux -> public.land_workmanagementedge
- land.f_t_gestion_signaletique -> public.land_signagemanagementedge
- management.m_r_intervention_desordre -> public.maintenance_intervention_disorders
- management.m_t_intervention -> public.maintenance_intervention
- management.m_b_suivi -> public.maintenance_interventionstatus
- management.m_b_intervention -> public.maintenance_interventiontype
- management.m_b_desordre -> public.maintenance_interventiondisorder
- management.m_b_fonction -> public.maintenance_interventionjob
- management.m_r_intervention_fonction -> public.maintenance_manday
- management.m_r_chantier_prestataire -> public.maintenance_project_contractors
- management.m_t_chantier -> public.maintenance_project
- management.m_b_chantier -> public.maintenance_projecttype
- management.m_b_domaine -> public.maintenance_projectdomain
- management.m_b_prestataire -> public.maintenance_contractor
- management.m_r_chantier_financement -> public.maintenance_funding
- geotrek.s_b_pratique_sportive -> public.sensitivity_sportpractice
- geotrek.s_b_espece_ou_suite_zone_regl -> public.sensitivity_species_practices
- geotrek.s_t_zone_sensible -> public.sensitivity_species
- geotrek.s_b_scellement -> public.sensitivity_sensitivityarea
- management.s_b_signaletique -> public.signage_signagetype
- management.s_t_signaletique -> public.signage_signage
- management.s_b_direction -> public.signage_direction
- management.s_b_color -> public.signage_color
- management.s_b_lame -> public.signage_bladetype
- management.s_t_lame -> public.signage_blade
- management.s_t_ligne -> public.signage_line
- tourism.t_b_type_renseignement -> public.tourism_informationdesktype
- tourism.t_b_renseignement -> public.tourism_informationdesk
- tourism.t_b_contenu_touristique_categorie -> public.tourism_touristiccontentcategory
- tourism.t_b_contenu_touristique_type -> public.tourism_touristiccontenttype
- tourism.t_b_systeme_reservation -> public.tourism_reservationsystem
- tourism.t_r_contenu_touristique_theme -> public.tourism_touristiccontent_themes
- tourism.t_r_contenu_touristique_type1 -> public.tourism_touristiccontent_type1
- tourism.t_r_contenu_touristique_type2 -> public.tourism_touristiccontent_type2
- tourism.t_r_contenu_touristique_source -> public.tourism_touristiccontent_source
- tourism.t_r_contenu_touristique_portal -> public.tourism_touristiccontent_portal
- tourism.t_t_contenu_touristique -> public.tourism_touristiccontent
- tourism.t_b_evenement_touristique_type -> public.tourism_touristiceventtype
- tourism.t_r_evenement_touristique_theme -> public.tourism_touristicevent_themes
- tourism.t_r_evenement_touristique_source -> public.tourism_touristicevent_source
- tourism.t_r_evenement_touristique_portal -> public.tourism_touristicevent_portal
- tourism.t_t_evenement_touristique -> public.tourism_touristicevent
- trekking.o_r_itineraire_itineraire2 -> public.trekking_orderedtrekchild
- trekking.o_r_itineraire_theme -> public.trekking_trek_themes
- trekking.o_r_itineraire_reseau -> public.trekking_trek_networks
- trekking.o_r_itineraire_accessibilite -> public.trekking_trek_accessibilities
- trekking.o_r_itineraire_web -> public.trekking_trek_web_links
- trekking.o_r_itineraire_renseignement -> public.trekking_trek_information_desks
- trekking.o_r_itineraire_source -> public.trekking_trek_source
- trekking.o_r_itineraire_portal -> public.trekking_trek_portal
- trekking.l_r_troncon_poi_exclus -> public.trekking_trek_pois_excluded
- trekking.o_t_itineraire -> public.trekking_trek
- trekking.o_r_itineraire_itineraire -> public.trekking_trekrelationship
- trekking.o_b_reseau -> public.trekking_treknetwork
- trekking.o_b_pratique -> public.trekking_practice
- trekking.o_b_accessibilite -> public.trekking_trek_accessibilities
- trekking.o_b_parcours -> public.trekking_route
- trekking.o_b_difficulte -> public.trekking_difficultylevel
- trekking.o_t_web -> public.trekking_weblink
- trekking.o_b_web_category -> public.trekking_weblinkcategory
- trekking.o_t_poi -> public.trekking_poi
- trekking.o_b_poi -> public.trekking_poitype
- trekking.o_r_service_pratique -> public.trekking_servicetype_practices
- trekking.o_b_service -> public.trekking_servicetype
- trekking.o_t_service -> public.trekking_service
- zoning.f_b_zonage -> public.zoning_restrictedareatype
- zoning.l_zonage_reglementaire -> public.zoning_restrictedarea
- zoning.f_t_zonage -> public.
- zoning.l_commune -> public.zoning_city
- zoning.f_t_commune -> public.
- zoning.l_secteur -> public.zoning_district
- zoning.f_t_secteur -> public.

Some columns name has changed too:

- longueur -> length
- ascent

See `commit <https://github.com/GeotrekCE/Geotrek-admin/commit/b27e42be5>`


Package Debian from version 2.33
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From version 2.33, Geotrek-admin is packaged in a debian package. This mean several things :

- a system user ``geotrek`` is created on install ;

- base code is located in ``/opt/geotrek-admin`` folder ;

- ``geotrek`` is the new command, replacing ``bin/django``, and must be run in root (system user ``geotrek`` is used after) ;

- there is no more ``settings.ini`` but an ``env`` file with environment variables ;

- configuration files (custom.py et env), parsers and all customisation files (templates and translations) are now located in ``/opt/geotrek-admin/var/conf`` ;

- we advise you to configure data synchronization in ``/opt/geotrek-admin/var``
