===========
USER MANUAL
===========

Screencasts
-----------

( **In French** )

* `Présentation de l'interface  <http://youtu.be/-iVe9cwBZ50>`_
* `Création d'un itinéraire <http://youtu.be/d37WixqDs6c>`_
* `Création d'un POI <http://youtu.be/PRY8y7y8WxM>`_
* `Ajout de photos <http://youtu.be/n96O09284ao>`_
* `Administration <http://youtu.be/P106bQCRZKk>`_

Modules
-------

Geotrek est composé de différents modules.

**Gestion des sentiers** :

* Tronçons (linéaire entre 2 intersections)
* Sentiers (groupe de tronçons)
* Statuts (physique, foncier, organismes ayant la compétence sentiers, gestionnaires des travaux et de la signalétique)
* Aménagements (ouvrages et équipements)
* Signalétique
* Interventions (travaux)
* Chantiers (groupe d'interventions)

**Valorisation de l'offre touristique** :

* Itinéraires (randonnées)
* POI (points d'intérêt patrimoniaux)
* Objets touristiques (activités de pleine nature, musées, produits labellisés...)
* Evènements (animations, expositions, sorties...)
* Signalements (problèmes signalés par les internautes sur un itinéraire depuis Geotrek-rando)

Chaque module est accessible depuis le bandeau vertical. 

Tous les modules sont construits de la même façon : 

* une liste paginée des objets du module
* la possibilité de filtrer la liste ou de faire une recherche libre
* la possibilité d'exporter les résultats en CSV (pour EXCEL ou CALC), en SHAPEFILE (pour QGIS ou ArcGIS) et en GPX (pour l'importer dans un GPS)
* une carte dans laquelle il est possible de naviguer (déplacer, zoomer), d'afficher en plein écran, de mesurer une longueur, d'exporter une image de la carte, de réinitialiser l'étendue, de zommer sur une commune ou un secteur et de choisir les couches à afficher

.. image :: images/user-manual/01-liste-fr.jpg

Au survol d'un objet dans la liste, celui-ci est mis en surbrillance sur la carte. 

Au survol d'un objet sur la carte, celui-ci est mis en évidence dans la liste.

La liste des résultats est filtrée en fonction de l'étendue de la carte affichée.

C'est aussi depuis un module qu'il est possible d'ajouter de nouveaux objets.

Un clic sur un objet dans la liste ou la carte permet d'accéder à la fiche détaillée de celui-ci.

Fiches détails
--------------

Edition d'un objet
------------------

Pictogrammes
------------

Les pictogrammes contribués dans Geotrek doivent être au format :

* SVG (de préférence, cela permet de conserver la qualité en cas de redimensionnement) ou PNG,
* SVG pour les thèmes (afin de permettre un changement de couleur pour les thèmes sélectionnés),
* SVG si l'application mobile est déployée (le support du format PNG n'est pas assuré sur l'application mobile).

Il doivent :

* Avoir un viewport carré afin de ne pas être déformés sur le portail,
* Ne pas déborder du cercle inscrit pour les pratiques et les catégories de contenus touristiques, en prévoyant une
  marge si nécessaire.

Afin de s'intégrer au mieux dans le design standard, les couleurs suivantes sont recommandées :

* Blanc sur fond transparent pour les pratiques et les catégories de contenus touristiques,
* Gris sur fond transparent pour les thèmes,
* Blanc sur fond orange pour les types de POI.
