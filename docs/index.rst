.. meta::
    :description lang=en: Welcome to the Geotrek-admin documentation!
    :description lang=fr: Bienvenue sur la documentation de Geotrek-admin!
    :keywords: Geotrek-admin documentation

Geotrek-admin's documentation
=============================

**Geotrek-admin** is a web application designed to manage, centralize, and structure geographical and touristic information for your territory. It is the back-office application of the Geotrek ecosystem.

.. image:: http://geotrek.fr/assets/img/screen-1.png
   :align: center
   :alt: Interface de Geotrek-admin

With **Geotrek-admin**, you can:

- Manage treks, touristic information, and related content (media, descriptions, etc.).
- Organize your data with maps, layers, and metadata.
- Export content to various public interfaces, such as Geotrek-rando or printed topoguides.

You can explore **Geotrek-admin** in action through the demonstration website:

- `https://demo-admin.geotrek.fr/ <https://demo-admin.geotrek.fr/>`_ (demo / demo)

**Geotrek-admin** is built on Django and leverages a PostGIS database for handling geographical data. It serves as the data source for Geotrek-rando, Geotrek-widget, and other tools of the Geotrek ecosystem.

.. seealso::
    Learn more about Geotrek-admin in the :ref:`general documentation (french) <qu-est-ce-que-geotrek>`.

.. _cards-clickable:

Main sections
...............

.. grid:: 2  

    .. card:: Explore what Geotrek can do
        :link: qu-est-ce-que-geotrek
        :link-type: ref
        :link-alt: what is Geotrek

        🏞️ **About Geotrek (fr)**
        ^^^
        Discover what Geotrek is, its main features, and how it can help manage and promote outdoor activities.  

        *Includes an overview of the 4 main components, user profiles, how to join the community, the open-source components used in each module, and the ownership and governance of the project.*
        +++
        Introduction to Geotrek

    .. card:: Learn how to use Geotrek
        :link: user-manual
        :link-type: ref
        :link-alt: user manual

        🚀 **User manual (fr)**
        ^^^
        Step-by-step guide for administrators, editors, and end users.  

        *Covers management and promotion modules, the different views (list, detail, edit), details for each module, geometric calculations on objects, additional attributes (medias, HD views, accessibility photos, etc.), configuration options (modules, user management, multilingual setup, portal configuration, pictograms), the Geotrek API, integrations with external APIs, static pages, and menus.*
        +++
        Functional documentation

.. grid:: 2  

    .. card:: Follow step-by-step tutorials
        :link: visualiser-les-donnees-dans-qgis
        :link-type: ref
        :link-alt: visualize your data in Qgis

        💡 **Tutorials (fr)**
        ^^^
        Hands-on guides and practical examples to help you get started and explore advanced features.  

        *Includes how to visualize your data in QGIS (SQL views, PostgreSQL database connection), configure basemaps (Leaflet layers, adding IGN and cadastral layers), and fix topology issues.*
        +++
        Learn by doing

    .. card:: Set up and configure your environment
        :link: basic-configuration-update
        :link-type: ref
        :link-alt: basic configuration

        🔧 **Installation and configuration**
        ^^^
        All you need to set up Geotrek on your server and adapt it to your needs.  

        *Covers installation on Ubuntu, prerequisites, installation steps, upgrades, server migration, PostgreSQL installation, basic configuration, Nginx configuration, mandatory settings, user management, maintenance tasks, operational commands (deleting attachments, removing duplicate paths, reordering topologies, cron jobs), and synchronization with Geotrek-mobile.*
        +++
        Technical setup

.. grid:: 2  

    .. card:: Customize and optimize Geotrek
        :link: application-settings
        :link-type: ref
        :link-alt: application settings

        ⚙️ **Advanced configuration**
        ^^^
        Fine-tune Geotrek with advanced settings and custom integrations.  

        *Includes application settings (email, API, custom SQL), map settings (Leaflet configuration, Mapentity configuration, map screenshots, geographical CRUD), enabling/disabling apps, feedback report settings (Suricate support), attachment management, interface customization (columns displayed in list views and exports, form fields in creation views), edition settings (PDF templates, booklet PDFs), and configuration for Geotrek-mobile.*
        +++
        Power user options

    .. card:: Import and update your data
        :link: minimal-initial-data
        :link-type: ref
        :link-alt: minimal initial data

        🗃️ **Import data**
        ^^^
        Learn how to import, update, and manage your data in Geotrek.  

        *Covers minimal initial data (DEM, areas), replacing DEM, importing paths, importing new areas, importing data from tourism systems (Apidae, Tourinsoft, Cirkwi), loading data (POIs, infrastructures, signages), and using Geotrek Aggregator.*
        +++
        Data management

.. grid:: 2  

    .. card:: Get involved in the project
        :link: contributing
        :link-type: ref
        :link-alt: contributing

        ✨ **Contribute**
        ^^^
        Help improve Geotrek by contributing code, translations, or documentation.  

        *Includes ways to contribute, contribution guidelines (conventions, pull requests, releases), development (quickstart, model modifications, quality checks, running tests, UML diagram of the data model), translation, documentation, and design (architecture, main components).*
        +++
        Community contributions

    .. card:: Access extra resources
        :link: troubleshooting
        :link-type: ref
        :link-alt: troubleshooting

        📝 **Others**
        ^^^
        Various resources, tips, and complementary documentation.  

        *Covers troubleshooting, frequently encountered problems, list of authors, and changelog.*
        +++
        Additional resources

.. toctree::
    :caption: 🏞️ A propos
    :hidden:

    about/geotrek.rst

.. toctree::
    :caption: 🚀 Manuel d'utilisation
    :hidden:

    user-manual/overview.rst
    user-manual/interfaces.rst
    user-manual/management-modules.rst
    user-manual/touristic-modules.rst 
    user-manual/editing-objects.rst
    user-manual/configuration-ttw.rst
    user-manual/apis.rst
    user-manual/static-pages.rst

.. toctree::
    :caption: 💡 Tutoriels
    :hidden:

    tutorials/vizualize-data-in-qgis.rst
    tutorials/update-basemaps-layers.rst
    tutorials/topologies-issues.rst

.. toctree::
    :caption: 🔧 Installation & configuration
    :hidden:

    installation-and-configuration/installation
    installation-and-configuration/upgrade
    installation-and-configuration/configuration
    installation-and-configuration/maintenance
    installation-and-configuration/exploitation-commands
    installation-and-configuration/synchronization

.. toctree::
    :caption: ⚙️ Advanced configuration
    :hidden:

    advanced-configuration/application-settings
    advanced-configuration/map-settings
    advanced-configuration/modules-and-components
    advanced-configuration/feedback-report-settings
    advanced-configuration/attachments
    advanced-configuration/interface
    advanced-configuration/edition
    advanced-configuration/settings-for-geotrek-mobile

.. toctree::
    :caption: 🗃️ Import data
    :hidden:

    import-data/minimal-initial-data
    import-data/import-dem-raster
    import-data/import-paths
    import-data/import-areas
    import-data/import-touristic-data-systems
    import-data/import-other-data
    import-data/import-aggregator

.. toctree::
    :caption: ✨ Contribute
    :hidden:

    contribute/contributing
    contribute/guidelines
    contribute/development
    contribute/translating
    contribute/documentation
    contribute/design

.. toctree::
    :caption: 📝 Others
    :hidden:

    others/troubleshooting
    others/authors
    changelog
