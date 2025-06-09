.. meta::
    :description lang=en: Welcome to the Geotrek-admin documentation!
    :description lang=fr: Bienvenue sur la documentation de Geotrek-admin!
    :keywords: Geotrek-admin documentation

Geotrek-admin's documentation
=============================

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Explore Geotrek
        :link: qu-est-ce-que-geotrek
        :link-type: ref
        :link-alt: what is Geotrek

        🏞️ **About Geotrek (fr)**
        ^^^
        Discover Geotrek’s main features and ecosystem.

        - Components & profiles
        - Community & governance
        - Open-source stack
        +++
        Introduction

    .. grid-item-card:: Use Geotrek
        :link: user-manual
        :link-type: ref
        :link-alt: user manual

        🚀 **User manual (fr)**
        ^^^
        Step-by-step guide for all users.

        - Modules & views
        - Data & media
        - API & menus
        +++
        Functional docs

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Tutorials
        :link: visualiser-les-donnees-dans-qgis
        :link-type: ref
        :link-alt: visualize your data in Qgis

        💡 **Tutorials (fr)**
        ^^^
        Hands-on guides to learn by doing.

        - QGIS connection
        - Basemaps setup
        - Fix topology
        +++
        Learn by doing

    .. grid-item-card:: Install & Configure
        :link: basic-configuration-update
        :link-type: ref
        :link-alt: basic configuration

        🔧 **Installation**
        ^^^
        Set up and adapt Geotrek.

        - Ubuntu install
        - Config & users
        - Maintenance
        +++
        Technical setup

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Customize
        :link: application-settings
        :link-type: ref
        :link-alt: application settings

        ⚙️ **Advanced config**
        ^^^
        Fine-tune Geotrek’s settings.

        - Maps & APIs
        - UI & PDF
        - Mobile sync
        +++
        Power options

    .. grid-item-card:: Import data
        :link: minimal-initial-data
        :link-type: ref
        :link-alt: minimal initial data

        🗃️ **Import data**
        ^^^
        Import, update, and manage data.

        - Import data
        - Touristic data systems
        - Aggregator
        +++
        Data management

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Contribute
        :link: contributing
        :link-type: ref
        :link-alt: contributing

        ✨ **Contribute**
        ^^^
        Improve Geotrek together.

        - Code & docs
        - Translations
        - Guidelines
        +++
        Community

    .. grid-item-card:: Extra
        :link: troubleshooting
        :link-type: ref
        :link-alt: troubleshooting

        📝 **Others**
        ^^^
        Tips, fixes, and credits.

        - Troubleshooting
        - Authors
        - Changelog
        +++
        Resources


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

    import-data/introduction
    import-data/minimal-initial-data
    import-data/fixtures
    import-data/command-load
    import-data/parsers
    import-data/aggregator
    import-data/development

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
