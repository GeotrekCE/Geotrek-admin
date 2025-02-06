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

<p align="center">
    <a href="#admin"><b>Admin</b></a>  •  
    <a href="#features"><b>Features</b></a>  •  
    <a href="#user-manual-french"><b>User manual</b></a>  •  
    <a href="#installation-and-configuration"><b>Installation and configuration</b></a>  •  
</p>
<p align="center">
    <a href="#support"><b>Support</b></a>  •   
    <a href="#contribution"><b>Contribution</b></a>  •  
    <a href="#thanks-to-all-contributors-"><b>Contributors</b></a>  •  
    <a href="#license"><b>License</b></a>  • 
</p>

[![Alt text](http://geotrek.fr/assets/img/screen-1.png "Interface de Geotrek-admin")](http://geotrek.fr)

## Admin

**Geotrek-admin** is a web application designed to manage, centralize, and structure geographical and touristic information for your territory. It is the back-office application of the Geotrek ecosystem.

With Geotrek-admin, you can:
- Manage treks, touristic information, and related content (media, descriptions, etc.).
- Organize your data with maps, layers, and metadata.
- Export content to various public interfaces, such as Geotrek-rando or printed topoguides.

You can explore Geotrek-admin in action through the demonstration website:
- [https://demo-admin.geotrek.fr/](https://demo-admin.geotrek.fr/) (demo / demo) : 

Geotrek-admin is built on Django and leverages a PostGIS database for handling geographical data. It serves as the data source for Geotrek-rando, Geotrek-widget and other tools of the Geotrek ecosystem.

Learn more about Geotrek-admin in the [general documentation (French)](https://geotrek.readthedocs.io/fr/latest/about/geotrek.html).

## Features

Geotrek-Admin is a powerful web mapping application designed for managing trekking, outdoor and tourism data with ease. Tailored to support GIS features and extensive customization, it empowers organizations to manage, maintain, and publish their outdoor assets seamlessly:

- **Management tool**: manage paths, interventions, signage, treks, POIs, touristic events, and much more.
- **Maintenance tracking**: track the maintenance of equipment and infrastructures with precision.
- **Advanced GIS capabilities**: control objects by district, protected areas, physical and legal status of paths, and compute 3D attributes using DEM draping.
- **Data synchronization**: interconnect with external platforms like Suricate, Apidae, and Tourinsoft for real-time data updates.
- **Publishing tools**:  
  - create public websites with [Geotrek-rando](https://github.com/GeotrekCE/Geotrek-rando-v3) (e.g., [Destination Écrins](https://rando.ecrins-parcnational.fr), [Alpes Rando](https://alpesrando.net/)).
  - embed trek information into existing websites with [Geotrek-widget](https://github.com/GeotrekCE/Geotrek-rando-widget) for flexible and lightweight integration (e.g., [Sidobre Vallée Tourisme](https://sidobre-vallees-tourisme.com/type_activite/balades-et-randonnees-sidobre-vallees/), [la Toscane Occitane](https://www.la-toscane-occitane.com/a-voir-a-faire/balades-randonnees))..
  - deploy mobile applications with [Geotrek-mobile](https://github.com/GeotrekCE/Geotrek-mobile) (e.g., [Grand Carcasssonne](https://play.google.com/store/apps/details?id=io.geotrek.grandcarcassonne), [Jura outdoor](https://apps.apple.com/app/jura-outdoor/id6446137384)).
- **Customizable outputs**: export data in various formats (PDF, GPX, KML) for offline use and tailored user experiences. 
- **Interactive mapping**: enable users to visualize and explore data-rich maps with detailed elevation profiles.
- **Documentation and support**: access comprehensive documentation, best practices and community support for all your needs in the ([official documentation](https://geotrek.readthedocs.io/en/2.111.0/usage/overview.html)).

Learn more on the [Geotrek product website](http://geotrek.fr).  

## User manual (french)

- [Presentation](https://geotrek.readthedocs.io/fr/latest/usage/overview.html)
- [Management modules](https://geotrek.readthedocs.io/fr/latest/usage/management-modules.html)
- [Touristic modules](https://geotrek.readthedocs.io/fr/latest/usage/touristic-modules.html)

## Installation and configuration

- [Installation](https://geotrek.readthedocs.io/fr/latest/install/installation.html)
- [Configuration](https://geotrek.readthedocs.io/fr/latest/install/configuration.html)
- [Advanced configuration](https://geotrek.readthedocs.io/fr/latest/install/advanced-configuration.html)

## Support

- To report bugs or suggest features, please [submit a ticket](https://github.com/GeotrekCE/Geotrek-admin/issues).
- Join our community to stay updated and share your experience! Connect on [Matrix](https://matrix.to/#/%23geotrek:matrix.org) for real-time discussions, or connect through the [Google Group](https://groups.google.com/g/geotrek-fr) to exchange ideas and insights.

## Contribution

Interested in contributing? See our [Contributing Guide](https://geotrek.readthedocs.io/en/latest/contribute/contributing.html
). You can help in many ways, the ability to code is not necessary.

## Thanks to all contributors ❤

<a href="https://github.com/GeotrekCE/Geotrek-admin/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=GeotrekCE/Geotrek-admin" />
</a>

Made with [contrib.rocks](https://contrib.rocks).

## License

This project is under the BSD License. See the [LICENSE](Geotrek-admin/blob/main/LICENSE) for details.

- OpenSource - BSD
- Copyright (c) 2012-2024 - Makina Corpus Territoires / Parc national des Ecrins - Parc National du Mercantour - Parco delle Alpi Marittime

<a href="https://territoires.makina-corpus.com/"><img src="https://geotrek.fr/assets/img/logo_makina.svg" alt="Logo de Makina Corpus Territoires" width="115"></a>
[![Alt text](https://geotrek.fr/assets/img/logo_autonomens-h120m.png "Logo Autonomens")](https://datatheca.com/)

----

[![Alt text](http://geotrek.fr/assets/img/parc_ecrins.png "Logo du Parc national des Ecrins")](http://www.ecrins-parcnational.fr)
[![Alt text](http://geotrek.fr/assets/img/parc_mercantour.png "Logo du Parc national du Mercantour")](http://www.mercantour.eu)
[![Alt text](http://geotrek.fr/assets/img/alpi_maritime.png "Logo du Parc naturel des Alpes maritimes")](http://www.parcoalpimarittime.it)
