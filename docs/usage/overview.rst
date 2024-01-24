========================
1. Présentation générale
========================

.. contents::
   :local:
   :depth: 2

1.1 Architecture
================

L’application est composée : 

* d’une **page d'authentification**, demandant la saisie d’un login et d’un mot de passe
* d’une **interface de consultation des objets de chaque module** 

    * avec la liste de sélection déroulante des modules avec compteur des résultats
    * un onglet latéral de sélection des modules
    * un accès aux paramètres d’administration
    * un bouton déconnexion de l’application

* de **paramètres d’administration** (gestion des droits, des listes déroulantes…)

1.2 Page d'authentification
===========================

.. figure:: ../images/user-manual/geotrek-login.png
   :alt: Accès à Geotrek-admin via un login et un mot de passe
   :align: center

   Accès à Geotrek-admin via un login et un mot de passe


1.3 Interface de consultation des modules
==========================================

1.3.1 Modules
-------------

Geotrek est composé de différents modules.

1.3.1.1 Modules de gestion
---------------------------

.. list-table:: Modules de gestion
   :widths: 25 25 50
   :header-rows: 1

   * - Icône
     - Module
     - Description
   * - .. figure:: ../images/user-manual/modules/troncons.png
     - :ref:`Tronçon <les-troncons>`
     - | C'est l’équivalent du réseau routier : ils constituent le support des tracés
       | des objets linéaires (itinéraires, statuts, interventions, aménagements...). 
       | Leur modification est relativement rare (fermeture d’un chemin, 
       | éboulement...).
   * - .. figure:: ../images/user-manual/modules/sentier.png
     - :ref:`Sentier <les-sentiers>`
     - | Les itinéraires, non pas de randonnée, mais de gestion, correspondent au 
       | départ et à l'arrivée d'un sentier.
   * - .. figure:: ../images/user-manual/modules/statut.png
     - :ref:`Statut <les-statuts>`
     - | Gestion des organismes ayant la compétence sentiers,  
       | gestionnaires des travaux et de la signalétique.  
       | Type physique (route, piste, sente, etc.)
   * - .. figure:: ../images/user-manual/modules/amenagement.png
     - :ref:`Aménagement <les-amenagements>`
     - | Décrit et localise les ouvrages, le mobilier, les équipements.
   * - .. figure:: ../images/user-manual/modules/signaletique.png
     - :ref:`Signalétique <la-signaletique>`
     - | Reprend l'ensemble de la signalétique d'accueil, d'information et 
       | d'orientation à destination des randonneurs.
       | Gestion des fichiers associés comme les BAT, les maquettes…
   * - .. figure:: ../images/user-manual/modules/intervention.png
     - :ref:`Intervention <les-interventions>`
     - | Répertorie les travaux liés à l'entretien courant des ouvrages,
       | l'entretien sur les sentiers, la mise en place et l'entretien 
       | de la signalétique, etc...
   * - .. figure:: ../images/user-manual/modules/chantier.png
     - :ref:`Chantier <les-chantiers>`
     - | Correspond à des ensembles d'interventions. Cela permet d'avoir une 
       | approche globale de chantiers significatifs et des informations 
       | administratives associées.

1.3.1.2 Modules de valorisation
--------------------------------

.. list-table:: Modules de valorisation
   :widths: 25 25 50
   :header-rows: 1

   * - Icône
     - Module
     - Description
   * - .. figure:: ../images/user-manual/modules/itineraire.png
     - :ref:`Itinéraire <itineraires>`
     - | Randonnées présentées au grand public : l’itinéraire est 
       | défini selon la géométrie des tronçons empruntés. L’ajout, 
       | la modification sont fréquents. La dé-publication est fortement
       | déconseillée pour le référencement et les passerelles 
       | avec d'autres outils.
   * - .. figure:: ../images/user-manual/modules/poi.png
     - :ref:`Points d'intérêts (POI) <points-d-interets-poi>`
     - | Ponctuels à découvrir associés aux randonnées : en fonction 
       | de leur  emplacement, ils sont associés automatiquement aux 
       | randonnées. Leur catégorie détermine leur pictogramme (faune,  
       | flore, patrimoine, équipements...).
   * - .. figure:: ../images/user-manual/modules/service.png
     - :ref:`Services <services>`
     - | Informations pratiques comme les points d'eau, passages 
       | délicats... selon la typologie souhaitée. Ils n'ont pas de 
       | description ni de nom, ni de photo et sont uniquement affichés 
       | sur la carte de l'itinéraire sous forme de pictogramme. 
   * - .. figure:: ../images/user-manual/modules/contenustouristiques.png
     - :ref:`Contenus touristiques <contenus-touristiques>`
     - | Correspond aux services touristiques pouvant être importés 
       | depuis des Systèmes d'Informations Touristiques (SIT),  
       | qui permettent d'alimenter automatiquement la base de
       | données Geotrek. Celles-ci sont regroupées dans des 
       | catégories de type : hébergements, musées, restaurants, 
       | produits du terroir...
   * - .. figure:: ../images/user-manual/modules/evenementstouristiques.png
     - :ref:`Évènements touristiques <evenements-touristiques>`
     - | Correspond aux animations pouvant être importées depuis 
       | des Systèmes d'Informations Touristiques (SIT), qui permettent
       | d'alimenter automatiquement la base de données Geotrek. 
       | Celles-ci sont regroupées dans des catégories de type : 
       | conférences, expositions, sorties…
   * - .. figure:: ../images/user-manual/modules/signalements.png
     - :ref:`Signalements <signalements>`
     - | Contient les problèmes remontés par les internautes, par 
       | exemple via le formulaire dédié sur Geotrek-rando
   * - .. figure:: ../images/user-manual/modules/zonessensibles.png
     - :ref:`Zones sensibles <zones-sensibles>`
     - | Module non activé par défaut permettant de saisir et de gérer  
       | des zones de sensibilité de la faune sauvage pour les afficher 
       | sur Geotrek-rando ou les diffuser avec l'API de Geotrek-admin). 
   * - .. figure:: ../images/user-manual/modules/sitesoutdoor.png
     - :ref:`Sites outdoor <pleinenature>`
     - | Permet de définir des sites d'activités de pleine nature 
       | (sites d'escalade, rivières, aires de vol libre)
   * - .. figure:: ../images/user-manual/modules/parcoursoutdoor.png
     - :ref:`Parcours outdoor <pleinenature>`
     - | Couplé au module « site outdoor», permet de les détailler en 
       | renseignant des activités de pleine nature diverses (kayak, 
       | rafting, parapente, course d'orientation, voie d'escalade, 
       | parcours d'eau vive…etc.) 

Chaque module est accessible depuis le bandeau vertical.

1.3.2 Navigation et saisie
--------------------------

Les résultats sont affichés sous forme de carte et liste puis on accède aux détails des objets.

1.3.2.1 Vue liste
~~~~~~~~~~~~~~~~~

Tous les modules sont construits de la même façon :

* une liste paginée des objets du module
* la possibilité de filtrer la liste selon des attributs ou de faire une recherche libre
* la possibilité de filtrer selon l'étendu de la carte
* la sélection coordonnée (liste → carte, carte → liste)
* la possibilité d'exporter les résultats en CSV (pour EXCEL ou CALC), en SHAPEFILE (pour QGIS) et en GPX (pour l'importer dans un GPS)
* une carte dans laquelle il est possible de naviguer (déplacer, zoomer), d'afficher en plein écran, de mesurer une longueur, d'exporter une image de la carte, de réinitialiser l'étendue, de zoomer sur une commune ou un secteur et de superposer des données des autres modules (contours communes / secteurs / physique / foncier / gestionnaires…)
* l'accès à la vue détail d'un objet au clic sur celui-ci

.. figure:: ../images/user-manual/01-liste-fr.jpg
   :alt: Vue liste avec la carte
   :align: center

   Vue liste avec la carte 

.. note::
	Au survol d'un objet dans la liste, celui-ci est mis en surbrillance sur la carte.
	La liste des résultats est filtrée en fonction de l'étendue de la carte affichée.
	C'est aussi depuis un module qu'il est possible d'ajouter de nouveaux objets.
	Un clic sur un objet dans la liste ou la carte permet d'accéder à la fiche détaillée de celui-ci.

1.3.2.2 Vue détail
~~~~~~~~~~~~~~~~~~

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

1.3.2.3 Vue édition
~~~~~~~~~~~~~~~~~~~~

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

1.3.2.4 Fichiers liés
~~~~~~~~~~~~~~~~~~~~~

L’ajout, la modification ou la suppression des documents, illustrations et photos s’effectuent depuis l’onglet « Fichiers liés » de la fiche détail.

Pour chaque fichier lié, l’auteur, le titre, la légende et sa catégorie sont saisis. Les fichiers liés peuvent être de tout type (photo, vidéo, dessin, PDF, tableur, fichier audio…). Pour les images, un aperçu est présenté.

Les vignettes et versions redimensionnées des photos sont créées automatiquement lors de l’ajout.
Les contenus saisis sont publiés automatiquement.

Il est possible de limiter la gestion des fichiers liés à un groupe restreint d’utilisateurs.

1.4 Paramètres d'administration
===============================

Toutes les listes de choix (thématiques, pratiques, parcours…) sont administrables depuis l'outil d'administration Django, selon les droits dont dispose l’utilisateur connecté.

.. figure:: ../images/user-manual/admin-django.png
   :alt: Interface de l'administration Django
   :align: center

   Interface de l'administration Django

.. figure:: ../images/user-manual/django-pratique.png
   :alt: Exemple d’édition des pratiques et de leur pictogramm
   :align: center

   Exemple d’édition des pratiques et de leur pictogramme

Voir la section :ref:`Paramétrage des modules <parametrages-des-modules>`
