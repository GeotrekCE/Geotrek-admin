===========
5. Vues HD
===========

.. contents::
   :local:
   :depth: 2

5.1 Représentation verticale : les vues HD
==========================================

Pour aller au-delà de la localisation sur une carte dans la représentation des sites d'activité Outdoor, notamment celles verticales (escalade, via-ferrata, alpinisme...), nous avons la possibilité d'ajouter des photos très haute définition (gigapixel) sur les itinéraires, POI et sites outdoor, et d'annoter celles-ci pour les enrichir.

Le bloc "Vues HD" dans l'onglet "Fichier liés" permet d'associer une photo très haute définition (de plusieurs dizaines ou centaines de Mo) aux itinéraires, POI et sites Outdoor. Ces images sont tuilées automatiquement pour disposer de fichiers plus légers à charger dans un navigateur (en fonctionnant comme les fonds de carte tuilés). 

.. image :: /images/user-manual/hd_view_trek.png

Une fois l'image ajoutée, un formulaire d'annotation permet d'ajouter des objets (points, lignes, polygones, cercles...) et des textes pour enrichir les photos. 

.. image :: /images/user-manual/hd_view_annotations.png

Les annotations sont stockées en GeoJSON et peuvent donc être affichées par dessus la photo tuilée dans une librairie javascript de cartographie (comme Leaflet ou GeoJS) au niveau de Geotrek-rando-v3 ou autre. Pour cela, l'APIv2 expose pour chaque Vue HD l'adresse de récupération des tuiles ainsi que les annotations GeoJSON.

La vue HD est également associée à une localisation correspondant à l'emplacement de ce que l'on voit sur l'image. 

.. image :: /images/user-manual/hd_view_detail.png
