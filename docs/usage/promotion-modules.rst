=======================
Modules de valorisation
=======================

.. todo::

    Détailler le fonctionnement des modules de valorisation (itinéraires, POI, contenus et évenements touristiques, services, signalement et zones de sensibilité).

Itinérance
==========

Il est possible de créer des randonnées itinérantes (sur plusieurs jours) et d'y associer des étapes comme sur cet exemple : http://www.grand-tour-ecrins.fr/a-pied/tour-de-la-berarde/.

Pour cela il faut créer un itinéraire parent (séjour itinérant complet) puis y ajouter des itinéraires enfants (étapes) de manière ordonnée, dans le champs `Enfants` présent dans l'onglet `Avancé` du formulaire itinéraire du séjour complet.

Le séjour complet ainsi que chaque sont donc chacunes des randonnées comme les autres. La seule différence est que les étapes (itinéraires enfants) sont rattachées à l'itinéraire parent.

Si vous ne souhaitez pas que les étapes soient affichées dans la page de Recherche de Geotrek-rando, il ne faut pas les publier. Il suffit alors de publier l'itinéraire parent, pour que toutes les étapes qui y sont rattachées apparaissent uniquement dans sa fiche détail de Geotrek-rando.

Points des références
=====================

Lorsque l'on localise un itinéraire, il est aussi possible de localiser le parking de la randonnée et de placer des points de référence numérotées sous forme de puces rouges sur la carte.

Ces derniers servent à y faire référence dans le champs Description de l'itinéraire (Pas à pas) :

.. image :: /images/user-manual/references-geotrek-rando.jpg

Pour que des puces numérotées sous forme de pastilles rouges soient affichées dans la description, il suffit de les saisir en tant que Liste numérotées dans le champs Description :

.. image :: /images/user-manual/references-geotrek-admin.jpg

**Ordre des catégories** :

Dans le portail Geotrek-rando, les différents types de contenus sont éclatés en catégories.

Pour définir leur ordre d'affichage, il est possible de le définir dans la base de données pour certains contenus (ordre des pratiques et des catégories de contenus touristiques) en renseignant leur champs ``ordre`` depuis l'Adminsite de Geotrek-admin.

Pour l'ordre d'affichage des catégorie Randonnées, Itinérance et Evènements touristiques, il est possible de modifier les valeurs par défaut définies dans le fichier ``geotrek/settings/base.py`` en surcouchant les paramètres correspondant dans le fichier de configuration avancée ``geotrek/settings/custom.py`` :

- ``TREK_CATEGORY_ORDER = 1``
- ``ITINERANCY_CATEGORY_ORDER = 2``
- ``TOURISTIC_EVENT_CATEGORY_ORDER = 99``

Il est aussi possible d'éclater les randonnées pour que chaque pratique soit une catégorie en surcouchant le paramètre ``SPLIT_TREKS_CATEGORIES_BY_PRACTICE = False``, d'éclater les types d'accessibilité en catégories avec le paramètre ``SPLIT_TREKS_CATEGORIES_BY_ACCESSIBILITY = False`` et de séparer les randonnées itinérantes dans une catégorie avec le paramètre ``SPLIT_TREKS_CATEGORIES_BY_ITINERANCY = False``.

Gestion et valorisation des activités outdoor
=============================================

**Sites et parcours**

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

**Arborescence**

Les fiches détail des sites et des parcours présentent les liens entre eux sous forme d'une arborescence. Pour ne pas surcharger,
tous les éléments ne sont pas repris, mais uniquement :

- le site/parcours courant,
- le site auquel il appartient (parent), ainsi que le grand-parent, etc. jusqu'à remonter au plus haut niveau,
- les différents sous-sites et/ou parcours (enfants) le cas échéant.

Des liens permettent d'ajouter des sites ou parcours en les positionnant directement dans l'arborescence.

**Nomenclatures**

En déroulant le menu en haut à droite de l'écran et en cliquant sur « Admin » il est possible de modifier les nomenclatures.

* Filières : elles servent à regrouper les pratiques pour pouvoir filtrer rapidement les sites ou parcours.
  Par exemple la filière « eau vive » peut regrouper « kayak » et « canyoning ».
* Pratiques : les pratiques sportives. Vous pouvez préciser à quelle filière elle appartient.
* Types de sites : ces catégories permettent d'étiqueter et de filtrer les sites. Elles sont spécifiques à chaque pratique.
  Par exemple « Site école » pour l'escalade.
* Échelle de cotation : permet de regrouper les cotations faisant partie de la même échelle. Elles sont spécifiques à chaque pratique.

**Escalade** :

La notion de site est naturelle. Elle peut être définie géographiquement par un polygone.
Il est possible (mais pas obligatoire) de créer des sous-sites pour représenter des secteurs.
Ou pour des falaises, elles-mêmes divisées en sous-sous sites pour les différents secteurs.

Chaque voie correspond à un parcours. La voie étant verticale et la carte horizontale,
le plus pertinent est de définir géographiquement la voie par un simple point.
Une grande voie peut être décrite simplement par un parcours mais, pour plus de détails,
il est également possible de créer autant de parcours que de longueurs dans la grande voie.
Lors de la saisie de la grande voie, il faudra préciser les différentes longueurs dans le champ « Enfants », dans le bon ordre.
Le nom de chaque longueur pourra reprendre le nom de la voie suffixé par « longueur 1 », « longueur 2 », etc.

**Vol libre**

La zone de vol n'est pas définie géographiquement de manière précise mais fait quand même l'objet d'un site avec un nom
(ex: « massif de … ») et un polygone approximatif ou bien un point (de préférence celui de départ). Cela n'a pas une importance
déterminante. Ce qui compte c'est 1) de rendre cela lisible sur une carte et 2) d'être cohérent entre les différents sites.

Pour chaque zone de vol, les différentes aires de décollage et d'atterrissage sont définies à l'aide de sous-sites.
Afin de les identifier, il faut créer les types de site « Aire de décollage » et « Aire d'atterrissage » pour la catégorie
« Vol libre » dans la nomenclature et associer ces types aux aires.
Comme le vol est libre, il n'est pas nécessaire de définir des parcours. Cependant, il est possible d'en définir pour donner
des exemples de trajectoires.

**Eau vive**

Le site est généralement constitué par une rivière ou une portion de rivière. Il est possible d'y adjoindre des affluents.
La géométrie du site est donc un linéraire correspondant à un réseau hydrographique.

Les aires d'embarquement/débarquement sont définies par des sous-sites. Leur géométrie peut être définie sous forme d'un point
ou d'un polygone.
Les parcours sont automatiquement attachés à une aire d'embarquement et une aire de débarquement qui sont les aires les plus
proches respectivement du début et de la fin du parcours.

