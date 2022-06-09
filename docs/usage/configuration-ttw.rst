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


Exemple : catégorie de contenu touristique et ses sous-type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|image7|


Pour chaque catégorie il est possible de définir deux listes de
sous-type et leur nom.

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