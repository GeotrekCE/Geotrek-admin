===========
USER MANUAL
===========

Screencasts
-----------

( **In French** )

* `Présentation de l'interface  <http://youtu.be/-iVe9cwBZ50>`_ :

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/-iVe9cwBZ50?rel=0" frameborder="0" allowfullscreen></iframe>

* `Création d'un itinéraire <http://youtu.be/d37WixqDs6c>`_ :

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/d37WixqDs6c?rel=0" frameborder="0" allowfullscreen></iframe>

* `Création d'un POI <http://youtu.be/PRY8y7y8WxM>`_ :

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/PRY8y7y8WxM?rel=0" frameborder="0" allowfullscreen></iframe>

* `Ajout de photos <http://youtu.be/n96O09284ao>`_ :

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/n96O09284ao?rel=0" frameborder="0" allowfullscreen></iframe>

* `Administration <http://youtu.be/P106bQCRZKk>`_ :

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/P106bQCRZKk?rel=0" frameborder="0" allowfullscreen></iframe>


Modules
-------

Geotrek est composé de différents modules.

**Gestion des sentiers** :

* Tronçons (linéaire entre 2 intersections)
* Sentiers (groupe de tronçons)
* Statuts (physique, foncier, organismes ayant la compétence sentiers, gestionnaires des travaux et de la signalétique)
* Aménagements (ouvrages et équipements)
* Signalétique
* Interventions (travaux)
* Chantiers (groupe d'interventions)

**Valorisation de l'offre touristique** :

* Itinéraires (randonnées)
* POI (points d'intérêt patrimoniaux)
* Services (informations pratiques comme les points d'eau, passages délicats... selon la typologie que vous souhaitez)
* Contenus touristiques (hébergements, restaurants, services, activités de pleine nature, musées, produits labellisés... Vous pouvez créer les catégories que vous souhaitez)
* Evènements touristiques (animations, expositions, sorties...)
* Signalements (problèmes signalés par les internautes sur un itinéraire depuis Geotrek-rando)
* Zones de sensibilité (module non activé par défaut permettant de gérer des zones de sensibilité de la faune sauvage pour les afficher sur Geotrek-rando ou les diffuser avec l'API de Geotrek-admin)

Chaque module est accessible depuis le bandeau vertical. 

Tous les modules sont construits de la même façon : 

* une liste paginée des objets du module
* la possibilité de filtrer la liste ou de faire une recherche libre
* la possibilité d'exporter les résultats en CSV (pour EXCEL ou CALC), en SHAPEFILE (pour QGIS ou ArcGIS) et en GPX (pour l'importer dans un GPS)
* une carte dans laquelle il est possible de naviguer (déplacer, zoomer), d'afficher en plein écran, de mesurer une longueur, d'exporter une image de la carte, de réinitialiser l'étendue, de zommer sur une commune ou un secteur et de choisir les couches à afficher

.. image :: images/user-manual/01-liste-fr.jpg

Au survol d'un objet dans la liste, celui-ci est mis en surbrillance sur la carte. 

Au survol d'un objet sur la carte, celui-ci est mis en évidence dans la liste.

La liste des résultats est filtrée en fonction de l'étendue de la carte affichée.

C'est aussi depuis un module qu'il est possible d'ajouter de nouveaux objets.

Un clic sur un objet dans la liste ou la carte permet d'accéder à la fiche détaillée de celui-ci.

Fiches détails
--------------

A partir de chaque module, il est possible d'afficher la fiche détail d'un objet en cliquant sur celui-ci dans la liste ou la carte du module. Les objets de chaque module peuvent ainsi être affichés individuellement dans une fiche détail pour en consulter tous les attributs, tous les objets des autres modules qui intersectent l'objet, les fichiers qui y sont attachés et l'historique des modifications de l'objet. 

Depuis la fiche détail d'un objet, il est aussi possible d'exporter celui-ci au format ODT, DOC ou PDF. 

Selon les droits dont dispose l'utilisateur connecté, il peut alors modifier l'objet. 

Edition d'un objet
------------------

**Segmentation dynamique** :

Tous les objets sont saisis et stockés relativement aux tronçons, en utilisant la segmentation dynamique (https://makina-corpus.com/blog/metier/2014/la-segmentation-dynamique), sauf les évènements et contenus touristiques, les services et les signalements qui sont indépendants et ont leur propre géométrie. 

C'est pourquoi, modifier un tronçon peut entrainer des modifications des objets qui lui sont rattachés (signalétique, interventions, itinéraires, POIs...). Supprimer un tronçon, supprime les objets qui lui sont rattachés. 

Les éléments ponctuels et linéaires des différents modules sont stockés sous forme d'évènements (PKdebut, PKfin et décalage dans la table ``geotrek.core_topology``) liés à un ou plusieurs tronçons (``geotrek.core_pathaggregation``).

Un objet peut ainsi être associé à un ou plusieurs tronçons, partiellement ou entièrement. 

Les objets ponctuels ne sont associés qu'à un seul tronçon, sauf dans le cas où ils sont positionnés à une intersection de tronçons.

Chaque évènement dispose néanmoins d'une géométrie calculée à partir de leur segmentation dynamique pour faciliter leur affichage dans Geotrek ou dans QGIS. Il ne faut néanmoins pas modifier directement ces géométries, elles sont calculées automatiquement quand on modifie l'évènement d'un objet.

A noter aussi que des vues dans les différents schémas permettent d'accéder aux objets de manière plus lisibles et simplifiée (``gestion.m_v_interventions`` par exemple).

**Snapping - Aimantage - Accrochage** :

Quand vous créez un objet, il est possible de le snapper (aimanter) aux objets existants. C'est notamment utile pour bien raccorder les tronçons entre eux. Quand vous raccrochez un tronçon à un tronçon existant, ce dernier est coupé automatiquement à la nouvelle intersection. 

Les fonctions d'aimantage ne sont pas disponibles lors de la création d'un nouvel objet (linéraire ou ponctuel). Il faut commencer par le créer sur puis le modifier pour disposer des fonctionnalités d'aimantage, activé automatiquement lorsque l'on se rapproche d'un objet existant. Par défaut la distance d'imantage est de 30 pixels mais elle est modifiable en configuration avancée.

**Itinérance** :

Il est possible de créer des randonnées itinérantes (sur plusieurs jours) et d'y associer des étapes comme sur cet exemple : http://www.grand-tour-ecrins.fr/a-pied/tour-de-la-berarde/.

Pour cela il faut créer un itinéraire parent (séjour itinérant complet) puis y ajouter des itinéraires enfants (étapes) de manière ordonnée, dans le champs `Enfants` présent dans l'onglet `Avancé` du formulaire itinéraire du séjour complet. 

Le séjour complet ainsi que chaque sont donc chacunes des randonnées comme les autres. La seule différence est que les étapes (itinéraires enfants) sont rattachées à l'itinéraire parent.

Si vous ne souhaitez pas que les étapes soient affichées dans la page de Recherche de Geotrek-rando, il ne faut pas les publier. Il suffit alors de publier l'itinéraire parent, pour que toutes les étapes qui y sont rattachées apparaissent uniquement dans sa fiche détail de Geotrek-rando. 

Gestion des sentiers
--------------------

Geotrek-admin comporte un certain nombre de modules de gestion des sentiers (tronçons, sentiers, statuts, aménagements, signalétique, interventions et chantiers).

Les tronçons sont les éléments de base sur lesquels s'appuient l'ensemble des objets des autres modules, en utilisant la segmentation dynamique (https://makina-corpus.com/blog/metier/2014/la-segmentation-dynamique).

Les modules signalétique et aménagement ont initialement été conçus dans une logique d’inventaire avec des possibilités de description basiques et génériques. Pour tout complément, il est possible d’attacher un ou plusieurs fichiers joints à chaque objet (photos, PDF, tableurs…).

Les modules interventions et chantiers ont été conçus de façon à permettre à la fois un inventaire et un suivi des travaux (prévisionnel, administratif et financier).

En termes de structuration, le choix initial a été de concevoir, sur le volet gestion, la gestion des valeurs des listes déroulantes structure par structure pour que chaque structure travaillant sur une même Geotrek-admin puisse avoir des typologies différentes (types de signalétique, d’aménagements, d’organismes...). Néanmoins depuis la version 2.20 de Geotrek-admin, il est possible de partager des typologies entre les différentes structures en ne renseignant pas ce champs. 

Lors de la saisie d'un objet sur la carte, il est possible d'afficher une couche SIG ou un relevé GPX sur la carte lors de la création d'un objet sur la carte pour pouvoir le visualiser et le localiser sur la carte (``Charger un fichier local (GPX, KML, GeoJSON)``).

**Les tronçons** :

C'est le socle essentiel et central de Geotrek. Un tronçon est un objet linéaire, entre 2 intersections. Le mécanisme de ségmentation dynamique permet de ne pas devoir le recouper pour y rattacher des informations.

Il peuvent être numérisés dans Geotrek-admin, mais il est conseillé des les importer, directement en SQL dans la base de données ou depuis QGIS (https://makina-corpus.com/blog/metier/2014/importer-une-couche-de-troncons-dans-geotrek).

Si ils sont numérisés directement dans Geotrek-admin, il est possible d'afficher sur la carte un fichier GPX ou GeoJSON pour faciliter leur localisation.

Quand un nouveau tronçon intersecte un tronçon existant, ce dernier est découpé automatiquement à la nouvelle intersection. 

En plus de leur géométrie, quelques informations peuvent être associées à chaque tronçon (nom, départ, arrivée, confort, source, enjeu d'entretien, usage et réseaux). 

Comme pour les autres objets, les informations altimétriques sont calculées automatiquement grace au MNT présent dans la base de données. 

Idem pour les intersections automatiques avec les zonages (communes, secteurs, zonages réglementaires) et les objets des autres modules qui sont intersectés automatiquement à chaque ajout ou modification d'un objet.

Comme pour tous les modules, il est possible d'exporter la liste des tronçons affichés (CSV, SHP ou GPX) ou bien la fiche complète d'un tronçon (ODT, DOC ou PDF). 

Comme pour tous les modules, il est aussi possible d'attacher des documents à chaque tronçon depuis sa fiche détail (images, PDF, tableurs, ZIP...).

Enfin, toujours depuis la fiche détail d'un tronçon, il est possible d'en afficher l'historique des modifications.

**Les sentiers** :

Il s'agit d'un ensemble linéaire composés d'un ou plusieurs tronçons (entiers ou partiels) grâce à la segmentation dynamique.

Les sentiers permettent d'avoir une vision de gestionnaire sur un linéaire plus complet que les tronçons (qui sont découpés à chaque intersection) pour en connaitre les statuts, la signalétique, les aménagements, les interventions ainsi que les itinéraires et POI. Il est d'ailleurs possible d'ajouter une intervention sur un sentier complet directement depuis la fiche détail d'un sentier.

A ne pas confondre avec le module Itinéraires qui permet de créer des randonnées publiées sur un portail Geotrek-rando. 

**Les statuts** :

Ils permettent de renseigner des informations sur le linéaire (type physique, statut foncier, organismes ayant la compétence sentiers, gestionnaires des travaux et de la signalétique) sans avoir à le faire tronçon par tronçon grâce à la segmentation dynamique qui permet de localiser le départ et l'arrivée sur un ou plusieurs tronçons. 

**Les aménagements** :

Ils permettent d'inventorier les aménagements sur les sentiers (passerelles, mains courantes, cunettes, soutenements, bancs, parkings...) en les localisant, les typant, les décrivant, renseignant leur état et leur année d'implantation.

Les types d'aménagement sont découpés en 2 catégories (Ouvrages et Equipements). Ce découpage n'est utilisé que pour filtrer les aménagements.

Il est possible de créer une intervention directement depuis la fiche détail d'un aménagement. 

Comme pour les autres modules, il sont intersectés avec les autres modules pour en connaitre l'altimétrie, les zonages (communes, réglementation...), les statuts (fonciers, physique, gestionnaire), les interventions, les itinéraires...

Il est aussi possible de les exporter, de leur attacher des fichiers (images, PDF, tableurs, ZIP...) et d'en consulter l'historique des modifications.

**La signalétique** :

Ils sont construits de la même manière que les aménagements et sont actuellement stockés dans la même table (``gestion.a_t_amenagement`` avec ``gestion.a_b_amenagement.type = S``). Ils ont donc les mêmes informations et fonctionnalités. 

**Les interventions** :

Les interventions permettent d'inventorier et suivre les travaux réalisés sur les sentiers. Chaque intervention correspond à une action sur un tronçon, sentier, aménagement ou signalétique. 

Les interventions peuvent être localisées directement sur le linéaire de tronçon en les positionnant grâce à la segmentation dynamique. Ou bien ils peuvent correspondre à un sentier, un aménagement ou une signalétique en les créant depuis leur fiche détail.

Une intervention peut être souhaitée (demandée par un agent), planifiée (validée mais à réaliser) ou réalisée. 

Un enjeu peut être renseigné pour chaque intervention. Il est calculé automatiquement si un enjeu a été renseigné au niveau du tronçon auquel l'intervention se raccroche. 

Chaque intervention correspond à un type. On peut aussi renseigner si celle-ci est sous-traitée, les désordres qui en sont la cause, la largeur et la hauteur. La longueur est calculée automatiquement si il s'agit d'une intervention linéaire mais est saisie si il s'agit d'une intervention ponctuelle. 

Plusieurs interventions peuvent être rattachées à un même chantier pour avoir une vision globale de plusieurs interventions correspondant à une opération commune. 

L'onglet Avancé du formulaire permet de renseigner des informations financières sur chaque intervention (coût direct et indirect lié au nombre de jours/agents dissocié par fonction).

**Les chantiers** :

Les chantiers permettent de grouper plusieurs interventions pour en avoir une vision globale et d'y renseigner globalement des informations administratives (Contraintes, financeurs, prestatires, cout global, maitrise d'ouvrage...) et éventuellement d'y attacher des documents (cahier des charges, recette, plans...).

Leur géométrie est la somme des géométries des interventions qui les composent.


Valorisation des sentiers
-------------------------

TODO : Détailler le fonctionnement des modules de valorisation (itinéraires, POI, contenus et évenements touristiques, services, signalement et zones de sensibilité).

**Points des références**

Lorsque l'on localise un itinéraire, il est aussi possible de localiser le parking de la randonnée et de placer des points de référence numérotées sous forme de puces rouges sur la carte. 

Ces derniers servent à y faire référence dans le champs Description de l'itinéraire (Pas à pas) :

.. image :: images/user-manual/references-geotrek-rando.jpg

Pour que des puces numérotées sous forme de pastilles rouges soient affichées dans la description, il suffit de les saisir en tant que Liste numérotées dans le champs Description : 

.. image :: images/user-manual/references-geotrek-admin.jpg

**Ordre des catégories** :

Dans le portail Geotrek-rando, les différents types de contenus sont éclatés en catégories. 

Pour définir leur ordre d'affichage, il est possible de le définir dans la base de données pour certains contenus (ordre des pratiques et des catégories de contenus touristiques) en renseignant leur champs ``ordre`` depuis l'Adminsite de Geotrek-admin.

Pour l'ordre d'affichage des catégorie Randonnées, Itinérance et Evènements touristiques, il est possible de modifier les valeurs par défaut définies dans le fichier ``geotrek/settings/base.py`` en surcouchant les paramètres correspondant dans le fichier de configuration avancée ``geotrek/settings/custom.py`` : 

- ``TREK_CATEGORY_ORDER = 1``
- ``ITINERANCY_CATEGORY_ORDER = 2``
- ``TOURISTIC_EVENT_CATEGORY_ORDER = 99``

Il est aussi possible d'éclater les randonnées pour que chaque pratique soit une catégorie en surcouchant le paramètre ``SPLIT_TREKS_CATEGORIES_BY_PRACTICE = False``, d'éclater les types d'accessibilité en catégories avec le paramètre ``SPLIT_TREKS_CATEGORIES_BY_ACCESSIBILITY = False`` et de séparer les randonnées itinérantes dans une catégorie avec le paramètre ``SPLIT_TREKS_CATEGORIES_BY_ITINERANCY = False``.

Pages statiques
---------------

Les pages statiques sont les pages d'information et de contextualisation de votre portail web Geotrek-rando. Comme pourraient l'être les premières pages d'un topo-guide papier. Elles peuvent aussi être consultées dans votre application Geotrek-mobile.

.. image :: images/user-manual/flatpages-gtecrins.jpg
*Exemple de page statique (http://www.grand-tour-ecrins.fr/informations/le-grand-tour-des-ecrins/)*

Elles permettent de fournir à l'internaute et futur randonneur des informations génériques : présentation de votre structure, votre projet de randonnée, recommandations, informations pratiques, etc.

Elles sont gérées depuis l'administe de Geotrek-admin et sont ensuite publiées sur Geotrek-rando à chaque synchronisation du contenu. 

.. image :: images/user-manual/flatpages-adminsite.jpg

**Créer une page statique**

Depuis l'Adminsite de Geotrek, sélectionnez "Pages statiques" dans la rubrique "Flatpages".

.. image :: images/user-manual/flatpages-flatpages.png

Vous accédez alors à la liste des pages statiques. 
Cliquer sur "Ajouter Page statique" en haut à droite de l'écran pour créer une première page.

**Construire une page statique**

Sélectionnez la langue du contenu que vous souhaitez saisir : en / fr / it...

Saisissez :

* un titre (sans guillemets, parenthèses, etc.)
* un ordre optionnel (pour définir l'ordre d'apparition dans le menu de votre Geotrek-rando)
* cochez « publié » lorsque vous souhaiterez mettre en ligne votre page
* définissez la « source » (comprendre ici la destination d'affichage et donc votre Geotrek-rando)
* sélectionnez une cible (Geotrek-rando et/ou Geotrek-mobile ou cachée pour créer une page qui ne sera pas listée dans le menu).

Attention, à chaque fois que cela vous est demandé, veillez à sélectionner la langue de votre contenu.

.. image :: images/user-manual/flatpages-form.jpg

L'interface permet de construire sa page en responsive design, c'est-à-dire qu'il est possible de disposer les blocs de contenu pour s'adaptera aux différentes tailles d'écrans des utilisateurs.

.. image :: images/user-manual/flatpages-bootstrap-responsive.jpg

Choisissez le gabarit sur lequel vous souhaitez construire votre page : 12 / 6-6 / 4-4-4 / etc. Ce sont des formats prédéfinis d'assemblage de blocs basés sur 12 colonnes qui occupent 100% de la largeur de l'écran (Bootstrap).

.. image :: images/user-manual/flatpages-bootstrap-grids.jpg

Vous pouvez aussi utiliser ou vous inspirer des 2 gabarits d'exemple (Gabarit 1 et Gabarit 2).

.. image :: images/user-manual/flatpages-blocks.jpg

Vous pouvez ajouter autant de gabarits que vous le souhaitez sur une seule page.

Une fois que vous avez ajusté vos blocs de contenu pour un affiche sur ordinateur (Desktop), vous devez basculer sur l'affichage sur mobile (Phone) pour l'adapter à des plus petits écrans (en cliquant sur les + et - bleus de chaque bloc). Privilégiez alors des blocs sur une colonne faisant 100% de large.

.. image :: images/user-manual/flatpages-blocks-edit.jpg

**Ajouter du contenu dans un bloc**

En cliquant dans la zone de texte, une barre d'édition apparaît. Sur un format classique comme dans les logiciels de traitement texte, plusieurs menus et outils sont alors disponibles :

* File : (fichier)
* Edit : retour, copier-coller, 
* Insert : Insérer une image, un lien, des caractères spéciaux

.. image :: images/user-manual/flatpages-wysiwyg.jpg
	
Insérer une image : cela ouvre une nouvelle fenêtre avec différents champs à remplir :

* Source : insérer l'URL de l'image (idéalement dans le répertoire /custom/public/images/ de votre Geotrek-rando)
* Image description : légender l'image pour optimiser son référencement
* Dimensions : ajuster le format et cocher « Constrain proportions »

Insérer un lien : cela ouvre une nouvelle fenêtre avec différents champs à remplir :

* URL : lien de destination
* Title : texte à afficher pour le lien
* Target : « New window » si vous souhaitez que le lien s'ouvre dans un nouvel onglet

- View : « Show blocks » permet de faire apparaître les différents paragraphes de votre texte. Elles sont utiles à la structure de votre texte. 
- Format : gras, italique, souligner, etc. Le sous-menu « Formats » permet de choisir un style prédéfini pour les titres (Heading 1, Heading 2, etc.). Pour que le style s'applique uniquement au titre et non pas à tout le texte, faire un retour à la ligne et vérifier sa prise en compte en activant « Shox blocks ».
- Table : insertion de tableau
- Tools : Afficher le code source de la page

**Astuces**

1. Ne jamais utiliser la touche retour du clavier [ ? ] sans avoir le curseur sélectionné dans une zone de texte. Cela équivaut à revenir à la page précédente et vous perdrez tout votre contenu sans le sauvegarder. 
2. Pour reproduire une page dans une langue différente : copier le Code Source et coller-le Code Source de votre nouvelle langue. Nous n'aurez plus qu'à traduire votre texte ! Idem pour traduire un contenu dans une autre langue.
3. Si deux de vos pages ont le même numéro d'ordre d'apparition, une seule des deux sera affichée sur la plate-forme numérique.

Pictogrammes
------------

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

Geotrek et IGNrando'
--------------------

Depuis la version 0.32.0, Geotrek-admin est capable de produire un flux des itinéraires et POIs présents dans sa BDD au format Cirkwi pour pouvoir les importer directement dans IGNrando'.

Exemple des randonnées et POIs du Parc national des Ecrins publiées sur IGNrando' depuis Geotrek-admin : https://ignrando.fr/fr/communautes/parc-national-des-ecrins

Depuis cette version, 2 flux sont automatiquement générés par Geotrek-admin au format attendu par l'IGN : 

- [URL_GEOTREK-ADMIN]/api/cirkwi/circuits.xml
- [URL_GEOTREK-ADMIN]/api/cirkwi/pois.xml

Il est possible d'exclure les POI du flux pour ne diffuser que les randonnées. Pour cela, ajouter le paramètre ``?withoutpois=1`` à la fin de l'URL (``http://XXXXX/api/cirkwi/circuits.xml?withoutpois=1``).

Le référentiel CIRKWI a été intégré dans 3 tables accessibles dans l'Adminsite (à ne pas modifier) : 

.. image :: images/user-manual/cirkwi-tables.png

Si vous ne souhaitez pas utiliser les valeurs par défaut ou avez créez vos propres typologies, il faut que vous renseigniez les correspondances entre les catégories de votre Geotrek et celles du référentiel IGN (Cirkwi) dans votre Adminsite. Comme indiqué ici : https://github.com/GeotrekCE/Geotrek-admin/issues/806

* Pratique >> locomotion/loisirs
* Accessibilite >> thematiques/tags
* Themes >> thematiques/tags
* Types de POI >> Categories POI

Les correspondances avec les valeurs de ces 3 tables sont donc à renseigner dans les tables Geotrek des Pratiques, Accessibilités, Thèmes et Types de POI.

:Note:

    Geotrek-admin dispose aussi d'une API générique permettant d'accéder aux contenus d'une instance à l'adresse : ``[URL_GEOTREK-ADMIN]/api/v2/``
