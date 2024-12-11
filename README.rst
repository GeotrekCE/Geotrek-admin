Geotrek-admin
=============

.. raw:: html

    <h1 align="center">Geotrek-admin</h1>
    
    <p align="center"><img alt="geotrek admin image" src="/docs/_static/geotrek-admin.png"></p>
    
    <p align="center">
    <a href="https://geotrek.readthedocs.io/" rel="nofollow"><img alt="Documentation" src="https://img.shields.io/badge/Documentation-red.svg" style="max-width:100%;"></a>
    <a href="https://demo-admin.geotrek.fr/" rel="nofollow"><img alt="Geotrek Admin demo" src="https://img.shields.io/badge/Demo-purple.svg" style="max-width:100%;"></a>
    <a href="https://matrix.to/#/%23geotrek:matrix.org" rel="nofollow"><img alt="Chat Matrix" src="https://img.shields.io/badge/Chat-blue.svg" style="max-width:100%;"></a>
    <a href="https://groups.google.com/g/geotrek-fr" rel="nofollow"><img alt="Forum Google Group" src="https://img.shields.io/badge/Forum-brightgreen.svg" style="max-width:100%;"></a>
    </p>
    <p align="center">
    <a href="https://github.com/GeotrekCE/Geotrek-admin/actions/workflows/test.yml" rel="nofollow"><img alt="CI Status" src="https://github.com/GeotrekCE/Geotrek-admin/actions/workflows/test.yml/badge.svg" style="max-width:100%;"></a>
    <a href="https://codecov.io/gh/GeotrekCE/Geotrek-admin" rel="nofollow"><img alt="Coverage" src="https://codecov.io/gh/GeotrekCE/Geotrek-admin/branch/master/graph/badge.svg" style="max-width:100%;"></a>
    <a href="https://dashboard.cypress.io/projects/ktpy7v/runs" rel="nofollow"><img alt="End to End" src="https://img.shields.io/endpoint?url=https://dashboard.cypress.io/badge/simple/ktpy7v/master&style=flat&logo=cypress" style="max-width:100%;"></a>
    <a href="https://geotrek.readthedocs.io" rel="nofollow"><img alt="Documentation" src="https://readthedocs.org/projects/geotrek/badge/?version=latest&style=flat" style="max-width:100%;"></a>
    </p>

.. raw:: html

   <p align="center">
       <a href="#admin"><b>Admin</b></a>  &#8226;  
       <a href="#features"><b>Features</b></a>  &#8226;  
       <a href="#user-manual-french"><b>User manual</b></a>  &#8226;  
       <a href="#installation-and-configuration"><b>Installation and configuration</b></a>  &#8226;  
   </p>
   <p align="center">
       <a href="#support"><b>Support</b></a>  &#8226;   
       <a href="#contribution"><b>Contribution</b></a>  &#8226;  
       <a href="#thanks-to-all-contributors-"><b>Contributors</b></a>  &#8226;  
       <a href="#license"><b>License</b></a>  &#8226; 
   </p>

Admin
-----

**Geotrek-admin** is a web application designed to manage, centralize, and structure geographical and touristic information for your territory. It is the back-office application of the Geotrek ecosystem.

With Geotrek-admin, you can:

- Manage treks, touristic information, and related content (media, descriptions, etc.).
- Organize your data with maps, layers, and metadata.
- Export content to various public interfaces, such as Geotrek-rando or printed topoguides.

You can explore Geotrek-admin in action through the demonstration website:

- `https://demo-admin.geotrek.fr/ <https://demo-admin.geotrek.fr/>`_ (demo / demo)

Geotrek-admin is built on Django and leverages a PostGIS database for handling geographical data. It serves as the data source for Geotrek-rando, Geotrek-widget, and other tools of the Geotrek ecosystem.

Learn more about Geotrek-admin in the `general documentation (French) <https://geotrek.readthedocs.io/fr/latest/about/geotrek.html>`_.

Features
--------

Geotrek-Admin is a powerful web mapping application designed for managing trekking, outdoor, and tourism data with ease. Tailored to support GIS features and extensive customization, it empowers organizations to manage, maintain, and publish their outdoor assets seamlessly:

- **Management tool**: manage paths, interventions, signage, treks, POIs, touristic events, and much more.
- **Maintenance tracking**: track the maintenance of equipment and infrastructures with precision.
- **Advanced GIS capabilities**: control objects by district, protected areas, physical and legal status of paths, and compute 3D attributes using DEM draping.
- **Data synchronization**: interconnect with external platforms like Suricate, Apidae, and Tourinsoft for real-time data updates.
- **Publishing tools**:
  - Create public websites with `Geotrek-rando <https://github.com/GeotrekCE/Geotrek-rando-v3>`_ (e.g., `Destination Écrins <https://rando.ecrins-parcnational.fr>`_, `Alpes Rando <https://alpesrando.net/>`_).
  - Embed trek information into existing websites with `Geotrek-widget <https://github.com/GeotrekCE/Geotrek-rando-widget>`_ for flexible and lightweight integration (e.g., `Sidobre Vallée Tourisme <https://sidobre-vallees-tourisme.com/type_activite/balades-et-randonnees-sidobre-vallees/>`_, `la Toscane Occitane <https://www.la-toscane-occitane.com/a-voir-a-faire/balades-randonnees>`_).
  - Deploy mobile applications with `Geotrek-mobile <https://github.com/GeotrekCE/Geotrek-mobile>`_ (e.g., `Grand Carcassonne <https://play.google.com/store/apps/details?id=io.geotrek.grandcarcassonne>`_, `Jura outdoor <https://apps.apple.com/app/jura-outdoor/id6446137384>`_).
- **Customizable outputs**: export data in various formats (PDF, GPX, KML) for offline use and tailored user experiences.
- **Interactive mapping**: enable users to visualize and explore data-rich maps with detailed elevation profiles.
- **Documentation and support**: access comprehensive documentation, best practices, and community support for all your needs in the `official documentation <https://geotrek.readthedocs.io/en/2.111.0/usage/overview.html>`_.

Learn more on the `Geotrek product website <http://geotrek.fr>`_.

User manual (french)
--------------------

- `Presentation <https://geotrek.readthedocs.io/fr/latest/usage/overview.html>`_
- `Management modules <https://geotrek.readthedocs.io/fr/latest/usage/management-modules.html>`_
- `Touristic modules <https://geotrek.readthedocs.io/fr/latest/usage/touristic-modules.html>`_

Installation and configuration
------------------------------

- `Installation <https://geotrek.readthedocs.io/fr/latest/install/installation.html>`_
- `Configuration <https://geotrek.readthedocs.io/fr/latest/install/configuration.html>`_
- `Advanced configuration <https://geotrek.readthedocs.io/fr/latest/install/advanced-configuration.html>`_

Support
-------

- To report bugs or suggest features, please `submit a ticket <https://github.com/GeotrekCE/Geotrek-admin/issues>`_.
- Join our community to stay updated and share your experience! Connect on `Matrix <https://matrix.to/#/%23geotrek:matrix.org>`_ for real-time discussions, or connect through the `Google Group <https://groups.google.com/g/geotrek-fr>`_ to exchange ideas and insights.

Contribution
------------

Interested in contributing? See our `Contributing Guide <https://geotrek.readthedocs.io/en/latest/contribute/contributing.html>`_. You can help in many ways, the ability to code is not necessary.

Thanks to all contributors ❤
----------------------------

.. image:: https://contrib.rocks/image?repo=GeotrekCE/Geotrek-admin
    :target: https://github.com/GeotrekCE/Geotrek-admin/graphs/contributors

Made with `contrib.rocks <https://contrib.rocks>`_.

License
-------

This project is under the MIT License. See the `LICENSE <Geotrek-admin/blob/main/LICENSE>`_ for details.

- OpenSource - BSD
- Copyright (c) 2012-2024 - Makina Corpus Territoires / Parc national des Ecrins - Parc National du Mercantour - Parco delle Alpi Marittime

.. image:: https://geotrek.fr/assets/img/logo_makina.svg
    :alt: Logo MCT
    :width: 115
    :target: https://territoires.makina-corpus.com/

.. image:: https://geotrek.fr/assets/img/logo_autonomens-h120m.png
    :alt: Logo Autonomens
    :target: https://datatheca.com/

----

.. image:: http://geotrek.fr/assets/img/parc_ecrins.png
    :alt: Parc national des Ecrins
    :target: http://www.ecrins-parcnational.fr

.. image:: http://geotrek.fr/assets/img/parc_mercantour.png
    :alt: Parc du Mercantour
    :target: http://www.mercantour.eu

.. image:: http://geotrek.fr/assets/img/alpi_maritime.png
    :alt: Parco delle Alpi Marittime
    :target: http://www.parcoalpimarittime.it
