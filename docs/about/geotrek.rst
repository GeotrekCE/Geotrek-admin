=======
Geotrek
=======

.. contents::
   :local:
   :depth: 2

Qu'est ce que Geotrek ?
=======================

Geotrek est un outil dédié à la **gestion et la valorisation** des activités de randonnées et des informations touristiques.

La plate-forme permet la gestion de **nombreuses pratiques sportives** liées à des linéaires (randonnée pédestre, à vélo, en VTT, à cheval, avec poussette, etc.) mais également pour **contenus outdoor** non linéaires (escalade, vol libre, sports d’eau vive, etc.).

C’est l’**application de référence** des parcs naturels, mais aussi de nombreuses structures publiques (conseils départementaux, communautés de communes, comités régionaux du tourisme, offices du tourisme, etc.).

**Utiliser Geotrek vous permettra** :

* d’intégrer une **communauté de gestionnaires de randonnées très active**
* de **bénéficier de l’ensemble des évolutions** commandées par les autres utilisateurs. Le service est vivant et s’améliore sans cesse
* de disposer d’une **offre complète** qui pourrait également être utilisée par d’autres acteurs du territoire
* de facilement pouvoir **accéder à d’autres fonctionnalités** quand le besoin s’en fera ressentir : site web, impression de fiches de parcours, gestion de la signalétique, organisation des travaux…
* d’exporter facilement vos contenus valorisables (itinéraires, POIs, contenus touristiques …) vers d’autres **plateformes touristiques nationales** (IGN Rando, VisoRando, OutdoorActive, Apidae, Cirkwi, etc.)

Les quatre modules
==================

Geotrek dispose de quatre modules à la fois distincts et complémentaires :

* **Geotrek Admin** : outil de gestion et de saisie de l’ensemble des informations, intégrant les données des Systèmes d’Informations Touristiques (SIT) et pouvant se relier à votre SIG ou à des systèmes d’information transport
* **Geotrek Rando** : site web, reprenant les informations saisies dans Geotrek Admin, à destination des internautes grand public
* **Geotrek Mobile** : application mobile fonctionnant sous Android et iOS, reprenant des informations saisies dans Geotrek Admin et optimisées pour l’usage mobile (volume, impact sur la batterie…)
* **Geotrek Widget** : nouveau composant web permettant de valoriser une offre de contenus touristiques et de randonnées auprès des usagers du territoire

Utilisateurs
============

L’application Geotrek, **destinée à deux types de public**, est une solution web qui apporte :

* des fonctionnalités de gestion des informations (itinéraires, destinations, points d’intérêts, description, interprétation…) et de gestion des infrastructures (signalétique, aménagement, travaux, réglementation…) pour les utilisateurs administrant un territoire (**Geotrek-Admin**) 
* des fonctionnalités simples et ludiques de recherche et de parcours d’itinéraires pour les internautes et les mobinautes (**Geotrek-Rando V3**, **Geotrek-Mobile** et **Geotrek-Widget**).

Composants libres
=================

L’application Geotrek utilise les technologies open source suivantes :

* **Python / Django**, l'épine dorsale de l'application qui prend en charge les principales fonctionnalités comme l'interface d'administration, l'exploitation de la base de données, la gestion des utilisateurs et de leurs droits ou l'intégration avec les bibliothèques cartographiques. La richesse de son écosystème permet de concevoir des applications aux possibilités infinies, en favorisant la production d'applications sécurisées, solides (tests automatiques) et robustes (Python).
* **PostgreSQL / PostGIS** pour la base de données. La totalité des données de l'application est stockée dans une instance PostgreSQL avec l'extension spatiale PostGIS :

  * attributs, comptes utilisateurs…,
  * géométries,
  * raster (Modèle Numérique Terrain).
* **JavaScript / React**, **Next.js**, **Leaflet**, **SVG** et **WebGL** pour l'interaction avec les utilisateurs et la visualisation, **HTML5** pour la structure du site, **CSS3** pour l’apparence.
