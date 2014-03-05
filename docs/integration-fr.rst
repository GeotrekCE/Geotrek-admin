=====================
Prérequis Intégration
=====================

:toc:


Modèle Numérique de Terrain
---------------------------

Le format du raster d'élévation doit être compatible avec GDAL (Geotiff, ASCII, ...) ;

L'étendue du raster doit couvrir l'ensemble des tronçons ;

La projection du raster doit être identique à celle envisagée pour les
tronçons (*Lambert 93, EPSG:2154* de préférence) ;


Vectoriel des tronçons
----------------------

Le format doit être compatible avec OGR (ESRI Shapefile, GeoJSON, ...) ;

Le type de géometrie doit être *linestring*.


Valides et simples
~~~~~~~~~~~~~~~~~~

Les géométries doivent être valides et simples :

* Sans intersection sur elles-mêmes ;
* Sans tangence sur elles-mêmes ;


Topologiquement correct
~~~~~~~~~~~~~~~~~~~~~~~

* Sans tronçons qui se croisent
* Découpés aux intersections (*ex: sans "T" formé par 2 tronçons au lieu de 3*)
* Sans tronçons superposés
* Connectés avec précision aux intersections
* Tronçons isolés à éviter


Les outils qui permettent de vérifier ces aspects :

* `Plugin QGis Vérificateur de topologies <http://www.qgis.org/en/docs/user_manual/plugins/plugins_topology_checker.html>`_
* `JOSM Validator <http://wiki.openstreetmap.org/wiki/JOSM/Validator>`_
* `Module topology de PostGIS 2 <http://makina-corpus.com/blog/metier/utiliser-les-topologies-postgis-pour-nettoyer-un-filaire-de-voirie>`_


Attributs
~~~~~~~~~

Tous les attributs sont **optionnels**. Des valeurs sont données ici à titre
d'exemple.

* Nom (*libellé*)
* Source (*BDTopo IGN, Cadastre, OpenStreetMap, Bing Maps, ...*)
* Nom départ
* Nom arrivée
* Comfort (*Facile, moyen, difficile, ...*)
* Usages (*VTT, pédestre, véhicule, ...*)
* Réseau (*GR, ...*)
* Enjeu (*Faible, moyen, fort*)

La nature des tronçons peut également être intégrée :

* Nature physique (*Sente, piste, route, ...*)
* Type foncier (*PDIPR, rural, privé, domanial, ...*)


Zonage
------

Le format doit être compatible avec OGR (ESRI Shapefile, GeoJSON, ...) ;

Le type de géometrie doit être *polygon* ou *multipolygon*.

Les géométries doivent être valides et simples (sans auto-intersections).

Les géométries doivent topologiquement correctes (frontières communes propres).

Trois types principaux de zonages sont définis :

* Communes
* Secteurs
* Zones protégées


Communes
~~~~~~~~

* INSEE
* Nom


Secteurs/Vallées
~~~~~~~~~~~~~~~~

* Nom


Zones protégées
~~~~~~~~~~~~~~~

* Nom
* Type de zone (*Natura 2000, réserve intégrale, chasse, znieff, coeur du parc...*)


Itinéraires de randonnées
-------------------------

Le format doit être compatible avec OGR (ESRI Shapefile, GeoJSON, ...) ;

Le type de géometrie doit être *linestring*.

Dans l'application, les itinéraires sont définis en empruntant les
tronçons (segmentation dynamique).

Pour un import en masse, la couche des itinéraires doit donc être superposable
à la couche des tronçons (correspondance géometrique).

Il est également envisageable de créer la couche des tronçons à partir de la
couche des itinéraires.


Attributs (facultatifs)
~~~~~~~~~~~~~~~~~~~~~~~

À l'import, il est possible d'intégrer les attributs suivants. Il sont tous
facultatifs et pourront être complétés a posteriori via l'application.

* Nom
* Départ
* Arrivée
* Durée (heures)
* Position parking
* Thèmes (*Faune, flore, lacs...*)
* Réseaux (*GR, Chemin de Saint-Jacques, ...*)
* Usages (*Pédestre, VTT, Cheval, ...*)
* Parcours (*Aller-retour, boucle, ...*)
* Difficulté (*Très facile, facile, moyen, sportif*)
* Lieu de renseignement

Textes :

* Chapeau introduction
* Description
* Ambiance
* Modalité d'accès
* Infrastructures handicapés
* Parking conseillé
* Transport public
* Recommandations


Points d'intérêt
----------------

Attributs :

* Nom
* Description
* Type (*Point de vue, signalétique, patrimoine, géologie ...*)


Photos
------

Les photos sont associées aux itinéraires et POIs.

Attributs (facultatifs) :

* Auteur
* Titre
* Légende

Il convient de fournir des photos dans la résolution la plus grande possible,
les aperçus et encarts sont générés automatiquement de la publication.


Fonds de carte
--------------

Pour les fonds scan et orthophoto, plusieurs approches possibles :

* Serveur WMS (*doit supporter au moins la projection des données, voire EPSG:3857 sinon.*)
* Serveur WMTS
* Accès Geoportail IGN
* OpenStreetMap + Bing Maps
* Compte MapBox


Configuration fonctionnelle
---------------------------

* Liste des langues envisagées (*Français, Anglais, Italien, Castillan, Catalan*)
* Étendue par défault dans l'application (si différente des tronçons)
* Éléments attendus dans le pied de page


Pages satellites
----------------

Contenus à afficher sur le portail public, sous forme de pages, qui contiennent
textes et illustrations.

Examples :

* Réglementation
* Accompagnateurs
* À propos


Éléments graphiques
-------------------

* Logo (si possible vectoriel)
* Palette couleurs
* Police
* Photo pour bandeau supérieur haute qualité (1280px minimum)

Pictogrammes monochromes vectoriels (facultatif) :

* Thématiques randonnées
* Types de points d'intérêt
* Usages


Divers
------

* Google Analytics account number
