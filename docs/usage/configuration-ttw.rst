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

Pour mettre en forme le contenu de l'étiquette, il est possible d'utiliser du ``HTML``. Pour cela, il est recommandé d'utiliser des outils permettant de formater du contenu et d'obtenir le résultat en HTML directement. Par exemple via l'outil libre `Summernote <https://summernote.org/>`_.

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


.. _user-management-section:

Users management
================

Geotrek-admin relies on `Django authentication and permissions system <https://docs.djangoproject.com/en/4.2/topics/auth/default/>`_.
Users belong to groups, and permissions can be assigned at user or group-level.

With groups, you can create and configure user profile, each owning specific permissions.

The whole configuration of users, groups and permissions is available in the *AdminSite*,
if you did not enable *External authent* (see below).

|image9|

Users and permissions
---------------------

A given user can have three basic status level:

-  **Active**: if checked, the user can connect to Geotrek-admin

  It is better to deactivate an account when the user won't user Geotrek anymore, instead of supress it.
  Deleting the account will delete also all entries created by this account.

-  **Staff**: if checked, the user is authorized to access Geotrek-Admin administration interface

-  **Superuser**: if checked, the user has all permission, without having to define them specifically

A user can get specific permissions by object type.

To do so, select permissions from left box and move them in the right box.
Snapshot below shows a user with permissions allowing him/her to view and export signage,
without the ability to access to others modules. or edit signage objects.

|image10|

Permissions fall into four main types of actions:

* add
* change
* delete
* read / view

Each data type is at least associated with the four basic actions (*add*, *change*, *delete*, *read*). One data type corresponds to  a database table (*signage_signage*, *trekking_trek*...)

Here is the signification of actions allowed through permissions:

* *view*: see the data in Django *AdminSite* (for data of "category" type such as POI types, or difficulty level)
* *read*: see the data in Geotrek-admin interface (button and data list)
* *add*: adding of a new data (trek, theme...)
* *change*: modify the data
* *change_geom*: modify the data geometry
* *publish*: publish the data
* *export*: export the data thrgough Geotrek-admin interface (CSV, JSON...)


Groups
------

Groups allows to manage easily users and permissions. Each group is associated
to some permissions.

In user modification view, you can associate a user to one ore more groupes to
get their permissions.

By default six groups are created:

* Readers ("Lecteurs")
* Path managers ("Référents sentiers")
* Trek managers ("Référents communication")
* Editors ("Rédacteurs")
* Geotrek-rando ("Geotrek-rando")
* Trek and management editors ("Rédacteurs rando et gestion")

Once the application is installed, it is possible to modify the default permissions
of these existing groups, create new ones etc.

If you want to allow the users to access the *AdminSite*, give them the *staff*
status using the dedicated checkbox. The *AdminSite* allows users to edit data categories such as *trek difficulty levels*, *POI types*, etc.

Structures
----------

Each user has to be linked to a structure. During the installation, Geotrek create a default structure to which first users are linked.
You can add new structures, according to territorial partners, companies, other organisations which work with you on Geotrek.

Users of a given structure can work only on objects related to the same structure in Geotrek.
They can view objects from others structures, but won't be able to edit them.

*Exemple : Imagine a Geotrek deployed in the whole french territory, there could be structure related to "regions".
Each user would be linked to its region, through the structure.
Thus it would guarantee that a user from Bretagne could not edit objects created by a user from Normandie.*

The structure concept allows to  divide users actions fields, and allows several organisation to work on a same Geotrek-admin,
while data keep coherence.

.. note ::

    A user of a given structure will be able to create treks on paths related to another structure

.. note ::

    To allow an user to modify objects from another structure, there are two ways:

    - this user has superuser rights
    - this user owns "Can bypass structure" permission, which allows him to override structure restriction


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
