========
Visualiser les données dans Qgis
========

.. image :: /images/qgis/Qgis_projet.png

Création de vues SQL pour afficher des couches dans QGIS
=========

Des vues SQL ont été créés dans la base de données PostgreSQL dans le but de pouvoir les afficher dans Qgis. Ces vues contiennent les informations essentielles que l'on retrouve dans Geotrek Admin au niveau de chaque formulaire de module.

Ces vues sont consultables en lecture seule dans Qgis sous forme de couche.

Les modifications se font directement dans Geotrek Admin pour chaque projet, et elles sont répercutées instantanément dans les vues SQL.

Créer une connexion à la base de données PostgreSQL du projet
=========

1. Ouvrir le logiciel QGIS
2. Créer une nouvelle connexion de base de données PostgreSQL

* Dans l'Explorateur > PostgreSQL > Nouvelle connexion
* Renseigner les informations suivantes :
  * Nom de la connexion 
  * Hôte 
  * Port 
  * Base de données 
  * SSL mode : permet
  * Nom d’utilisateur 
  * Mot de passe 
* Cliquer sur « Tester la connexion »
* Si la connexion est réussi, cliquer sur OK pour enregistrer la connexion

.. image :: /images/qgis/Connexion_bdd.png

Créer un projet QGIS à partir des vues SQL
=========


Importer une vue SQL sous forme de couche
--------------

* Dans l'Explorateur > PostgreSQL > Ouvrir la connexion précédemment créé > Schéma public
* Ajouter les vues suffixées par `_qgis` : Clic droit sur l'objet > Ajouter la couche au projet
* Correspondance couches <> vues
  * Sentiers <> `v_trail_qgis`
  * Aménagements <> `v_infrastructures_qgis`
  * Signalétiques <> `v_signage_qgis`
  * Interventions <> `v_intervention_qgis`
  * Chantiers <> `v_project_qgis`
  * Itinéraires <> `v_treks_qgis`
  * POI's <> `v_pois_qgis`
  * Contenus touristiques <> `v_touristiccontent_qgis`
  * Évènements touristiques <> `v_touristicevent_qgis`
  * Signalement <> `v_report_qgis`
  * Zones sensibles <> `v_sensitivearea_qgis`
  * Zones <> `v_zoning_district_qgis`
  * Communes <> `v_zoning_city_qgis`
* Couches supplémentaires (dépend des projets)
  * Sites outdoor
    * Points : `v_outdoor_site_qgis_point`
    * Lignes : `v_outdoor_site_qgis_line`
    * Polygones : `v_outdoor_site_qgis_polygon`
  * Parcours outdoor
    * Points : `v_outdoor_course_qgis_point`
    * Lignes : `v_outdoor_course_qgis_line`
    * Polygones : `v_outdoor_course_qgis_polygon`

Afficher un fond de plan OpenStreetMap
--------------

* Dans l'Explorateur > XYZ Tiles > OpenStreetMap

Créer des groupes de couches
--------------

* Dans le panneau des couches > clic droit > Ajouter un groupe

Il peut être utile de créer des groupes de couches dans le cas où certaines couches sont disponibles dans plusieurs types géométriques : exemple pour la couche Sentiers qui peut contenir des lignes et des points

.. image :: /images/qgis/groupe_couches.png

Changer le style d'une couche
--------------

* Clic droit sur la couche > Propriétés > Symbologie

Selon le type géométrique de la couche (point, ligne, polygone), il est possible de changer à volonté la couleur de remplissage, la couleur de contour, la taille ou l'épaisseur.

Dimensionner les colonnes de la table attributaire
--------------
Le fait de dimensionner la taille des colonnes dans la table attributaire permet une permet lisibilité des noms de champs et des informations contenues à l'intérieur : 

* Clic droit sur la couche > Ouvrir la Table d'Attributs > clic droit sur une colonne > Taille autom pour toutes les colonnes

Certains champs texte peuvent être très larges (exemple _Description_ dans la couche **Zones sensibles**). Dans ce cas il est possible d'adapter manuellement la taille de la colonne :
* Clic droit sur la couche > Ouvrir la Table d'Attributs > clic droit sur la colonne > Largeur > Entrer une largeur de colonne (exemple : 200)

Afficher le décompte des entités d'une couche
--------------
* Clic droit sur la couche > Afficher le nombre d'entités

Zoomer sur l'emprise d'une couche
--------------
* Clic droit sur la couche > Zoomer sur la(les) couches
