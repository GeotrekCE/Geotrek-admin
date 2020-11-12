=========================
Valorisation des sentiers
=========================

TODO : Détailler le fonctionnement des modules de valorisation (itinéraires, POI, contenus et évenements touristiques, services, signalement et zones de sensibilité).

Points des références
=====================

Lorsque l'on localise un itinéraire, il est aussi possible de localiser le parking de la randonnée et de placer des points de référence numérotées sous forme de puces rouges sur la carte. 

Ces derniers servent à y faire référence dans le champs Description de l'itinéraire (Pas à pas) :

.. image :: /images/user-manual/references-geotrek-rando.jpg

Pour que des puces numérotées sous forme de pastilles rouges soient affichées dans la description, il suffit de les saisir en tant que Liste numérotées dans le champs Description : 

.. image :: /images/user-manual/references-geotrek-admin.jpg

Ordre des catégories
====================

Dans le portail Geotrek-rando, les différents types de contenus sont éclatés en catégories. 

Pour définir leur ordre d'affichage, il est possible de le définir dans la base de données pour certains contenus (ordre des pratiques et des catégories de contenus touristiques) en renseignant leur champs ``ordre`` depuis l'Adminsite de Geotrek-admin.

Pour l'ordre d'affichage des catégorie Randonnées, Itinérance et Evènements touristiques, il est possible de modifier les valeurs par défaut définies dans le fichier ``geotrek/settings/base.py`` en surcouchant les paramètres correspondant dans le fichier de configuration avancée ``geotrek/settings/custom.py`` : 

- ``TREK_CATEGORY_ORDER = 1``
- ``ITINERANCY_CATEGORY_ORDER = 2``
- ``TOURISTIC_EVENT_CATEGORY_ORDER = 99``

Il est aussi possible d'éclater les randonnées pour que chaque pratique soit une catégorie en surcouchant le paramètre ``SPLIT_TREKS_CATEGORIES_BY_PRACTICE = False``, d'éclater les types d'accessibilité en catégories avec le paramètre ``SPLIT_TREKS_CATEGORIES_BY_ACCESSIBILITY = False`` et de séparer les randonnées itinérantes dans une catégorie avec le paramètre ``SPLIT_TREKS_CATEGORIES_BY_ITINERANCY = False``.
