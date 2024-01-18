=====================
Présentation générale
=====================

.. contents::
   :local:
   :depth: 2

Architecture
=============

L’application est composée : 

- d’une **page d’accueil**, demandant la saisie d’un login et d’un mot de passe ;
- d’une **interface de consultation des modules** ;
  - avec la liste de sélection déroulante des modules avec compteur des résultats
  - un onglet latéral de sélection des modules
  - un accès aux paramètres d’administration
  - un bouton déconnexion de l’application
- de **paramètres d’administration** (gestion des droits, des listes déroulantes…).

Page d'accueil
==============

.. figure:: ../images/user-manual/geotrek-login.png
   :alt: Accès à Geotrek-admin via un login et un mot de passe
   :align: center

   Accès à Geotrek-admin via un login et un mot de passe


Interface de consultation des modules
=====================================

Modules
-------

Geotrek est composé de différents modules.

**Gestion des sentiers** :

+-------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Icone | Module        | Description                                                                                                                                                                          |
+=======+===============+======================================================================================================================================================================================+
|       | Tronçon       | C'est l’équivalent du réseau routier : ils constituent le support des tracés des itinéraires. Leur modification est relativement rare (fermeture d’un chemin, éboulement...).        |
+-------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|       | Sentier       | Les itinéraires, non pas de randonnée, mais de gestion, correspondent au départ et à l'arrivée d'un sentier.                                                                         |
+-------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|       | Statut        | Gestion des communes, organismes ayant la compétence sentiers, gestionnaires des travaux et de la signalétique, zones protégées, secteurs. Type physique (route, piste, sente, etc.) |
+-------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|       | Aménagement   | Décrit et localise les ouvrages, le mobilier, les équipements                                                                                                                        |
+-------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|       | Signalétique  | Reprend l'ensemble de la signalétique d'accueil, d'information et d'orientation à destination des randonneurs. Gestion des fichiers associés comme les BAT, les maquettes…           |
+-------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|       | Interventions | Répertorie les travaux liés à l'entretien courant des ouvrages.                                                                                                                      |
+-------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|       | Chantiers     | Correspond aux exemples d'interventions. Cela permet d'avoir une approche globale de chantiers significatifs et des informations administratives associées.                          |
+-------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**Valorisation de l'offre touristique** :

+-------+-------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Icone | Module                  | Description                                                                                                                                                                                                                                                                                                                                                              |
+=======+=========================+==========================================================================================================================================================================================================================================================================================================================================================================+
|       | Itinéraire              | Tracés présentés au grand public : l’itinéraire est défini selon la géométrie des tronçons empruntés. L’ajout, la modification ou la dé-publication sont fréquents.                                                                                                                                                                                                      |
+-------+-------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|       | Points d'intérêts (POI) | Ponctuels associés aux randonnées : en fonction de leur emplacement, ils sont associés automatiquement aux randonnées. Leur catégorie détermine leur pictogramme (faune, flore, patrimoine, équipements...). L’ajout, la modification ou la suppression sont fréquents.                                                                                                  |
+-------+-------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|       | Services                | informations pratiques comme les points d'eau, passages délicats... selon la typologie souhaitée. Ils n'ont pas de description ni de nom, ni de photo et sont uniquement affichés sur la carte de l'itinéraire sous forme de pictogramme.                                                                                                                                |
+-------+-------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|       | Contenus touristiques   | Correspond aux informations issues des Systèmes d'Informations Touristiques (SIT), qui permettent d'alimenter automatiquement la base de données Geotrek. Celles-ci sont regroupées dans des catégories de type : dormir pour les campings, gîtes… ou manger pour les restaurants… ou déguster pour mettre en évidence les produits locaux … ou visiter pour les musées… |
+-------+-------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|       | Évènements touristiques | Correspond aux informations issues des Systèmes d'Informations Touristiques (SIT), qui permettent d'alimenter automatiquement la base de données Geotrek. Celles-ci sont regroupées dans des catégories de type : animations, expositions, sorties…                                                                                                                      |
+-------+-------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|       | Signalements            | Contient les informations saisies par un internautes via le formulaire dédié sur Geotrek-Rando                                                                                                                                                                                                                                                                           |
+-------+-------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|       | Zones sensibles         | Module non activé par défaut permettant de saisir et de gérer des zones de sensibilité de la faune sauvage pour les afficher sur Geotrek-rando ou les diffuser avec l'API de Geotrek-admin).                                                                                                                                                                             |
+-------+-------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|       | Sites outdoor           | Permet de définir des sites (sites d'escalade, rivières, aires de vol libre…)                                                                                                                                                                                                                                                                                            |
+-------+-------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|       | Parcours outdoor        | Couplé au module « site outdoor», permet de saisir et renseigner des activités de pleines natures diverses (kayak, rafting, parapente, course d'orientation, voie d'escalade, parcours d'eau vive…etc.)                                                                                                                                                                  |
+-------+-------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Chaque module est accessible depuis le bandeau vertical.

Navigation et saisie
--------------------

Les résultats sont affichés sous forme de liste puis on accède aux détails des objets.

Vue liste
~~~~~~~~~~

Tous les modules sont construits de la même façon :

* une liste paginée des objets du module
* la possibilité de filtrer la liste selon des attributs ou de faire une recherche libre
* la possibilité de filtrer selon l'étendu de la carte
* la sélection coordonnée (liste → carte, carte → liste)
* la possibilité d'exporter les résultats en CSV (pour EXCEL ou CALC), en SHAPEFILE (pour QGIS) et en GPX (pour l'importer dans un GPS)
* une carte dans laquelle il est possible de naviguer (déplacer, zoomer), d'afficher en plein écran, de mesurer une longueur, d'exporter une image de la carte, de réinitialiser l'étendue, de zommer sur une commune ou un secteur et de superposer des données externes (contours communes / secteurs / physique / foncier / responsabilités…)
* l'accès à la vue détail d'un objet au clic

.. figure:: ../images/user-manual/01-liste-fr.jpg
   :alt: Vue liste avec la carte
   :align: center

   Vue liste avec la carte 

.. note::
	Au survol d'un objet dans la liste, celui-ci est mis en surbrillance sur la carte.
	Au survol d'un objet sur la carte, celui-ci est mis en évidence dans la liste.
	La liste des résultats est filtrée en fonction de l'étendue de la carte affichée.
	C'est aussi depuis un module qu'il est possible d'ajouter de nouveaux objets.
	Un clic sur un objet dans la liste ou la carte permet d'accéder à la fiche détaillée de celui-ci.

Vue détail
~~~~~~~~~~~

A partir de chaque module, il est possible d'afficher la fiche détail d'un objet en cliquant sur celui-ci dans la liste ou la carte du module. Les objets de chaque module peuvent ainsi être affichés individuellement dans une fiche détail pour en consulter tous les attributs, tous les objets des autres modules qui intersectent l'objet, les fichiers qui y sont attachés et l'historique des modifications de l'objet.

Voici les possibilités de la fiche détail :

- le récapitulatif des attributs (saisis et calculés)
- récupérer automatiquement des informations liées (communes, secteurs, POI…)
- ajouter des fichiers (redimensionnement automatique pour les photos)
- l'accès à la vue d’édition selon les droits de l’utilisateur connecté
- l'export GPX, KML, OpenDocument, Word, PDF

.. figure:: ../images/user-manual/fiche-detail.png
   :alt: Fiche détail d'un itinéraire
   :align: center

   Fiche détail d'un itinéraire

.. note::
	Lorsque le statut de publication de l’itinéraire est activé, celui-ci ainsi que tous ses objets associés, sont mis en ligne.
	À tout moment et ce sur chaque module, les informations peuvent être soit mises en ligne, soit désactivées, voire supprimées.
	Ne sont mises en ligne que les informations choisies et disponibles. Les catégories non encore alimentées ne seront pas visibles pour le grand public.

Vue édition
~~~~~~~~~~~

- Saisie des champs multilingues
- Saisie des tracés
- Possibilité de forcer des points de passage (détours, boucles, aller-retours)
- Édition WYSIWYG des champs texte
- Ajout de couches locales en superposition à partir de fichiers GPX ou KML (aide à la saisie)
- Outils de mesure

.. figure:: ../images/user-manual/vue-edition.png
   :alt: Fiche détail d'un itinéraire en édition
   :align: center

   Fiche détail d'un itinéraire en édition

Fichiers liés
~~~~~~~~~~~~~

L’ajout, la modification ou la suppression des illustrations et photos s’effectuent depuis l’onglet « Fichiers liés » de la fiche détail.

Pour chaque fichier lié, l’auteur, le titre, la légende et sa catégorie sont saisis. Les fichiers liés peuvent être de tout type (photo, dessin, PDF, fichier audio…). Pour les images, un aperçu est présenté.

Les vignettes et versions redimensionnées des photos sont créées automatiquement lors de l’ajout.
Les contenus saisis sont publiés automatiquement.

Il est possible de limiter la gestion des fichiers liés à un groupe restreint d’utilisateurs.

Paramètres d'administration
===========================

Toutes les listes de choix (thématiques, pratiques, parcours…) sont administrables depuis l'outil d'administration Django, selon les droits dont dispose l’utilisateur connecté.

.. figure:: ../images/user-manual/admin-django.png
   :alt: Interface de l'administration Django
   :align: center

   Interface de l'administration Django

.. figure:: ../images/user-manual/django-pratique.png
   :alt: Exemple d’édition des pratiques et de leur pictogramm
   :align: center

   Exemple d’édition des pratiques et de leur pictogramme

Voir la section 

..  Comment.
    :ref:`Paramétrage des modules <parametrages-des-modules>`   

