=================
Activités outdoor
=================

Sites et parcours
=================

Geotrek-admin dédie 2 modules aux activités outdoor : les sites et les parcours. Un site correspond à une zone ou à un réseau hydrographique
à gérer et/ou à valoriser d'un seul tenant : site d'escalade, cours d'eau, zone de vol libre…

Les sites peuvent être subdivisés en sous-sites (dits enfants), qui peuvent eux-mêmes être subdivisés en sous-sites :
secteurs d'escalade (groupe de blocs ou falaise), aires de décollage ou d'atterrissage…

Chaque site (ou sous-site) peut contenir différents parcours : voie d'escalade, parcours d'eau vive…

Il est possible de regrouper un enchaînement de parcours sous forme d'un parcours particulier appelé itinérance :
grande voie d'escalade, enchainement entre différentes pratiques…

Les 2 modules outdoor permettent de :

- Lister, filtrer, créer, modifier et exporter des sites et des parcours outdoor de manière générique pour gérer tout type de pratiques (escalade, alpinisme, via ferrata, canyoning, kayak, vol libre, plongée...)
- Ajouter les pratiques que l'on souhaite de manière générique, et de définir leurs propres types et leurs propres niveaux et valeurs de cotation
- Lier des sites entre eux de manière hiérarchisée, pour avoir des sites, des sous-sites, des sous-sous-sites... Par exemple pour un site global avec différentes pratiques, pour un site d'escalade avec des secteurs, des sous-secteurs...
- Agréger des informations au niveau d'un site, en fonction des sous-sites qui lui sont rattachés. Par exemple les pratiques d'un grand site outdoor sont l'agrégation des pratiques des sous-sites qui le composent
- Lier des parcours à des sites et leur appliquer une cotation en fonction de la pratique du site auquel ils sont rattachés
- Lier des parcours entre eux pour faire de l'itinérance avec une fiche mère et des fiches enfants (étapes), comme c'est déjà la cas pour les itinéraires
- Associer des aménagements aux sites (parking, toilettes, banc...) automatiquement par intersection géographique
- Associer des interventions à des sites ou parcours, automatiquement par intersection géographique, ou explicitement en passant par le site ou le parcours sur lequel l'intervention a été réalisée
- Associer des POI à un site ou parcours, automatiquement par intersection géographique
- Associer des accès au site, automatiquement par intersection géographique des itinéraires à proximité

Arborescence
------------

Les fiches détail des sites et des parcours présentent les liens entre eux sous forme d'une arborescence. Pour ne pas surcharger,
tous les éléments ne sont pas repris, mais uniquement :

- le site/parcours courant,
- le site auquel il appartient (parent), ainsi que le grand-parent, etc. jusqu'à remonter au plus haut niveau,
- les différents sous-sites et/ou parcours (enfants) le cas échéant.

Des liens permettent d'ajouter des sites ou parcours en les positionnant directement dans l'arborescence.

Nomenclatures
=============

En déroulant le menu en haut à droite de l'écran et en cliquant sur « Admin » il est possible de modifier les nomenclatures.

* Filières : elles servent à regrouper les pratiques pour pouvoir filtrer rapidement les sites ou parcours.
  Par exemple la filière « eau vive » peut regrouper « kayak » et « canyoning ».
* Pratiques : les pratiques sportives. Vous pouvez préciser à quelle filière elle appartient.
* Types de sites : ces catégories permettent d'étiqueter et de filtrer les sites. Elles sont spécifiques à chaque pratique.
  Par exemple « Site école » pour l'escalade.
* Échelle de cotation : permet de regrouper les cotations faisant partie de la même échelle. Elles sont spécifiques à chaque pratique.

Filières
========

Escalade
--------

La notion de site est naturelle. Elle peut être définie géographiquement par un polygone.
Il est possible (mais pas obligatoire) de créer des sous-sites pour représenter des secteurs.
Ou pour des falaises, elles-mêmes divisées en sous-sous sites pour les différents secteurs.

Chaque voie correspond à un parcours. La voie étant verticale et la carte horizontale,
le plus pertinent est de définir géographiquement la voie par un simple point.
Une grande voie peut être décrite simplement par un parcours mais, pour plus de détails,
il est également possible de créer autant de parcours que de longueurs dans la grande voie.
Lors de la saisie de la grande voie, il faudra préciser les différentes longueurs dans le champ « Enfants », dans le bon ordre.
Le nom de chaque longueur pourra reprendre le nom de la voie suffixé par « longueur 1 », « longueur 2 », etc.

Vol libre
---------

La zone de vol n'est pas définie géographiquement de manière précise mais fait quand même l'objet d'un site avec un nom
(ex: « massif de … ») et un polygone approximatif ou bien un point (de préférence celui de départ). Cela n'a pas une importance
déterminante. Ce qui compte c'est 1) de rendre cela lisible sur une carte et 2) d'être cohérent entre les différents sites.

Pour chaque zone de vol, les différentes aires de décollage et d'atterrissage sont définies à l'aide de sous-sites.
Afin de les identifier, il faut créer les types de site « Aire de décollage » et « Aire d'atterrissage » pour la catégorie
« Vol libre » dans la nomenclature et associer ces types aux aires.
Comme le vol est libre, il n'est pas nécessaire de définir des parcours. Cependant, il est possible d'en définir pour donner
des exemples de trajectoires.

Eau vive
--------

Le site est généralement constitué par une rivière ou une portion de rivière. Il est possible d'y adjoindre des affluents.
La géométrie du site est donc un linéraire correspondant à un réseau hydrographique.

Les aires d'embarquement/débarquement sont définies par des sous-sites. Leur géométrie peut être définie sous forme d'un point
ou d'un polygone.
Les parcours sont automatiquement attachés à une aire d'embarquement et une aire de débarquement qui sont les aires les plus
proches respectivement du début et de la fin du parcours.

Représentation verticale : les vues HD
======================================

Pour aller au-delà de la localisation sur une carte dans la représentation des sites d'activité Outdoor, notamment celles verticales (escalade, via-ferrata, alpinisme...), nous avons la possibilité d'ajouter des photos très haute définition (gigapixel) sur les itinéraires et sites outdoor et d'annoter celles-ci pour les enrichir.

Le bloc "Vues HD" dans l'onglet "Fichier liés" permet d'associer une photo très haute définition (de plusieurs dizaines ou centaines de Mo) aux itinéraires, POI et sites Outdoor. Ces images sont tuilées automatiquement pour disposer de fichiers plus légers à charger dans un navigateur (en fonctionnant comme les fonds de carte tuilés). 

.. image :: /images/user-manual/hd_view_trek.png

Une fois l'image ajoutée, un formulaire d'annotation permet d'ajouter des objets (points, lignes, polygones, cercles...) et des textes pour enrichir les photos. 

.. image :: /images/user-manual/hd_view_annotations.png

Les annotations sont stockées en GeoJSON et peuvent donc être affichées par dessus la photo tuilée dans une librairie javascript de cartographie (comme Leaflet ou GeoJS) au niveau de Geotrek-rando-v3 ou autre. Pour cela, l'APIv2 expose pour chaque Vue HD l'adresse de récupération des tuiles ainsi que les annotations GeoJSON.

La vue HD est également associée à une localisation correspondant à l'emplacement de ce que l'on voit sur l'image. 

.. image :: /images/user-manual/hd_view_detail.png
