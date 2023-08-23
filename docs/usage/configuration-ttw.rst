=============
Paramétrage
=============


Accès interface admin
=====================

Menu à droite > admin

.. figure:: /images/admin/capture-admin.png
   :alt: Capture lien admin

   Capture lien admin

Paramétrages des modules
========================

Itinéraires
-----------

-  Pratiques
-  Accessibilités
-  Niveaux de difficulté
-  Thèmes
-  Types de services
-  Types de POIs

|image4|

Exemple : ajouter une pratique
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Dans admin, à la ligne “Pratiques” cliquer sur “+ ajouter”
-  Remplir les champs (en gras les champs obligatoires)

(note : la couleur n’est utilisée que pour le mobile actuellement)

|image5|

Exemple : ajouter une étiquette
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Les étiquettes sont des encarts "pré-configurés" pouvant être réutilisés sur de multiples itinéraires. Elles présentent plusieurs avantages : 
- ne pas avoir à saisir à chaque itinéraire les même informations
- permet de filtrer les itinéraires dans la vue liste (catégorie "Autres") sur Geotrek-Rando.

Pour les configurer, vous devez :
- vous rendre dans l'interface d'administration
- dans la section Étiquettes du groupe **COMMUN** cliquer sur :guilabel:`+ Ajouter`

Via cette interface vous pourrez créer des étiquettes puis, une fois créées, les rattacher à des itinéraires.

* Créer une étiquette :

.. image :: ../images/admin/creation_etiquette.png

Pour mettre en forme le contenu de l'étiquette, il est possible d'utiliser du ``HTML``. Pour cela, il est recommandé d'utiliser des outils permettant de formater du contenu et d'obtenir le résultat en HTML directement. Par exemple via l'outil libre `TinyMCE <https://www.tiny.cloud/docs/demo/basic-example/>`_.

* Associer une étiquette à un itinéraire :

Une fois l'étiquette créée il faut l'associer à un itinéraire pour qu'elle soit visible sur le site. 
Une fois dans votre instance Geotrek Admin, éditez l'itinéraire concerné. Cliquez ensuite sur l'onglet :guilabel:`Avancé` et dans le champ Étiquettes choisissez dans le menu déroulant l'étiquette de votre choix (si vous en avez défini plusieurs). 

.. image :: ../images/admin/associer_etiquette_itineraire.png

.. tip::
    * L'ajout d'un pictogramme est facultatif, par défaut le pictogramme de l'étiquette sera le même que celui des recommandations dans les "Infos pratiques" de la fiche d'une randonnées (Geotrek Rando).
    * Si le champ "Filtre" est coché, l'étiquette sera proposée comme filtre dans Geotrek-Rando.
    * Les images (hors pictogramme) utilisées dans le contenu de l'étiquette doivent être des liens web. 

Rendu dans **Geotrek Rando** (onglet :guilabel:`Infos pratiques` d'une fiche randonnée) :

.. image :: ../images/admin/rendu_etiquette.png

Rendu dans **Geotrek Rando** (partie :guilabel:`Filtres`) :

.. image :: ../images/admin/rendu_etiquette2.png

.. _sites-et-parcours-outdoor-1:

Sites et parcours outdoor
-------------------------

-  Cotations
-  Filières
-  Pratiques
-  Types de parcours
-  Types de site
-  Échelles de cotation


Plongées
--------

-  Niveau de difficulté
-  Niveau technique
-  Pratique


Tourisme
--------

-  Autres sports : catégorie activités → Types de contenus touristiques
-  Lieux de renseignements
-  Types de lieux de renseignement
-  Types d’événement touristiques
-  Systèmes de réservation

|image6|


Exemple : catégorie de contenu touristique et ses sous-types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|image7|


Pour chaque catégorie il est possible de définir deux listes de
sous-types et leur nom.

Édition des sous-types de la catégorie “Hébergements”

.. figure:: /images/admin/django-admin-categorie-contenu-touristique-sous-types.png
   :alt: Sous-types de la catégorie “Hébergements”

   Sous-types de la catégorie “Hébergements”


Dans l’édition d’un contenu touristique de catégorie “Hébergement”

|image8|


Zones
-----

-  Communes
-  Secteurs
-  Zones sensibles et types de zones


Gestion des utilisateurs
========================

Dans Geotrek, il est possible de créer et de paramétrer des profils d'utilisateurs, possédant chacun des droits spécifiques et rattachés à des structures. La gestion des utilisateurs et des groupes est basée sur le `système d'authentification de Django <https://docs.djangoproject.com/fr/4.2/topics/auth/default/>`_.
Pour cela les objets suivants dans l'interface d'administration doivent être utilisés :

|image9|

Utilisateurs et droits
----------------------

Une fois un utilisateur créé avec les informations minimales, il est possible de lui octroyer un certain nombre de permissions :

-  **Actif** : permet de déterminer si l'utilisateur peut se connecter à Geotrek-Admin ou non. 

  Il est préférable de désactiver un compte lorsqu'un utilisateur n'intervient plus sur Geotrek, plutôt que de le supprimer.
  En effet supprimer le compte supprimera également par exemple toutes les entrées dans l'historique de Geotrek associées à ce compte.

-  **Statut équipe** : si la case est cochée l'utilisateur pourra accéder à l'interface d'administration de Geotrek-Admin

-  **Statut super-utilisateur** : permet d'octroyer toutes les permissions à un utilisateur sans avoir à les définir explicitement

Il est possible pour un utilisateur, de lui donner des permissions spécifiques. Celles-ci sont déterminées par type d'objet. 
  Pour cela il faut sélectionner les permissions dans l'écran de gauche pour les positionner dans l'écran de droite.
  Par exemple sur la capture ci-dessous l'utilisateur possède les permissions pour consulter uniquement et exporter les informations relatives aux 
  signalétiques sans possibilité d'accéder aux autres modules ou de modifier les contenus.

|image10|

Cette gestion fine des droits permet de déterminer les différents accès aux modules pour chaque utilisateur. On retrouve généralement pour chaque type d'objet les permissions suivantes qu'il est possible de donner ou non à un utilisateur :
-  Lecture
-  Ecriture
-  Modification
-  Modification de la géométrie de l'objet
-  Publication
-  Export

Groupes
-------

Pour faciliter l'opération de création d'utilisateurs et d'affectation de permissions, il existe un système de groupes dans Geotrek.
Pour chaque groupe il est possible d'associer un certain nombre de permissions.

Ensuite, dans la vue de modification de cet utilisateur, il suffira d'associer un utilisateur à un groupe pour bénéficier des permissions correspondantes.

Certains groupes existent par défaut dans Geotrek (Geotrek-rando, Lecteurs, Outdoor, Rédacteurs, Référents communication, Référents ronçons, Référents sentiers), mais il est bien entendu possible d'en ajouter d'autres pour refléter l'organisation de votre territoire.


Structures
----------

Chaque utilisateur est obligatoirement rattaché à une structure. Lors de l'installation, Geotrek crée une structure à laquelle les premiers utilisateurs seront rattachés.
Il est possible d'ajouter de nouvelles structures, reflétant des partenaires territoriaux, entreprises, entités qui seront ammenés à travailler à vos côté sur Geotrek.

Les utilisateurs d'une structure ne peuvent travailler que sur les objets dans Geotrek liés à leur structure. Ils pourront consulter les objets des autres structures mais n'auront pas le droit de les modifier.

Exemple : Si on imagine un Geotrek déployé sur l'ensemble du territoire français, il serait alors envisageable d'avoir des structures correspondantes aux régions. Chaque utilisateur sera rattaché à sa région correspondante. 
 Il y aura alors la garantie qu'un utilisateur de Bretagne ne puisse pas modifier les objets saisis par un utilisateur de Normandie.

Cette notion de structures permet de segmenter les périmètres d'action des utilisateurs et de permettre à différentes entités de travailler sur un même Geotrek-Admin, tout en garantissant une cohérence des données.

Deux précisions :
- Un utilisateur d'une structure pourra tout de même tracer des itinéraires sur des tronçons tracés par une autre structure
- Pour qu'un utilisateur puisse modifier les objets d'une autre structure il y a deux possibilités : soit celui-ci est super-utilisateur, soit il devra posséder la permission "Can by structure" qui permet d'outrepasser la restriction des structures.


Configuration des portails
==========================

Geotrek permet de configurer un ou plusieurs portails. Ce terme est utilisé pour référencer un site grand public sur lequel seront visibles les objets publiés de Geotrek.

Ainsi, il est possible d'avoir plusieurs Geotrek-Rando branchés sur un seul Geotrek-Admin. Grâce à leur distinction sous forme de portail, il sera alors aisé de choisir sur quel Geotrek-Rando on souhaite faire apparaitre une information.

Avec le widget Geotrek (https://github.com/GeotrekCE/geotrek-rando-widget) il est également possible d'utiliser cette fonctionnalité pour distinguer les contenus à afficher dans un widget ou dans un autre (https://makina-corpus.com/logiciel-libre/developpement-geotrek-widget-finance-parc-naturel-regional-haut-jura).

Pour configurer un ou pluseurs portails, il faut se rendre dans l'interface d'administration sur la section "Portails cibles".

|image11|

Il est possible de choisir de publier sur un ou plusieurs portails les objets suivants : itinéraires, contenus et évènements touristiques, pages statiques. Pour cela il suffit de sélectionner la valeur souhaitée dans le champ "portail" à l'édition de l'objet.


Pictogrammes
============

Les pictogrammes contribués dans Geotrek doivent être au format :

* SVG (de préférence, cela permet de conserver la qualité en cas de redimensionnement) ou PNG,
* SVG pour les thèmes (afin de permettre un changement de couleur pour les thèmes sélectionnés),

Il doivent :

* Avoir un viewport carré afin de ne pas être déformés sur le portail,
* Ne pas déborder du cercle inscrit pour les pratiques et les catégories de contenus touristiques, en prévoyant une
  marge si nécessaire.
* Avoir une dimension minimale de 56x56 pixels en ce qui concerne les PNG

Si vous utilisez Inkscape, vous devez définir une viewBox. Voir http://wiki.inkscape.org/wiki/index.php/Tricks_and_tips#Scaling_images_to_fit_in_webpages.2FHTML

Afin de s'intégrer au mieux dans le design standard, les couleurs suivantes sont recommandées :

* Blanc sur fond transparent pour les pratiques et les catégories de contenus touristiques,
* Gris sur fond transparent pour les thèmes,
* Blanc sur fond orange pour les types de POI.


.. |image4| image:: /images/admin/django-admin-params-itineraires.png
.. |image5| image:: /images/admin/django-admin-ajout-pratique.png
.. |image6| image:: /images/admin/django-admin-params-tourisme.png
.. |image7| image:: /images/admin/django-admin-categorie-contenu-touristique.png
.. |image8| image:: /images/admin/contenu-touristique-categorie-sous-type.png
.. |image9| image:: /images/admin/django-admin-params-users.png
.. |image10| image:: /images/admin/django-admin-user-right.png
.. |image11| image:: /images/admin/portals.png
