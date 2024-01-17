==========================
3. Modules de valorisation
==========================

.. contents::
   :local:
   :depth: 2

.. _itineraires:

3.1 Itinéraires
===============

Les itinéraires sont des tracés présentés au grand public : l’itinéraire est défini selon la géométrie des tronçons empruntés.
L’ajout, la modification ou la dé-publication sont fréquents.

3.1.1 Fiche détaillée
---------------------

3.1.1.1 Basique
~~~~~~~~~~~~~~~

**Structure liée** ~ requis

- Description : nom de la structure d'appartenance de l'itinéraire
- Type : liste déroulante
- Choix : unique
- URl de configuration : `/admin/authent/structure/ </admin/authent/structure/>`_
- Visibilité : interne
- Exemple : CD09

**Nom [fr]** ~ requis

- Description : nom de l'itinéraire
- Type : champ libre
- Multilingue : oui
- Visibilité : publique
- Exemple : GR09 Boucle du Pic des Trois Gentilhommes

**En attente de publication**

- Description : itinéraire en attente d'être publié
- Type : case à cocher
- Valeur par défaut (décoché) : itinéraire publiable 
- Visibilité : publique

**Publié [fr]**

- Description : Itinéraire publié ou en brouillon
- Type : case à cocher
- Valeur par défaut (décoché) : brouillon 
- Visibilité : interne

**Départ [fr]** ~ Recommandé

- Description : description du lieu de départ
- Type : champ libre
- Visibilité : publique
- Exemple : Refuge de les Caussis

**Arrivée [fr]** ~ Recommandé

- Description : description du lieu de l'arrivée
- Type : champ libre
- Visibilité : publique
- Exemple : Refuge de les Caussis

**Durée** ~ Recommandé

- Description : durée de l'itinéraire (en heures (1.5 = 1 h 30, 24 = 1 jour, 48 = 2 jours))
- Type : numérique
- Visibilité : publique
- Exemple : 1.5

**Difficulté** ~ Recommandé

- Description : niveau de difficulté de l'itinéraire
- Type : liste déroulante
- Choix : unique
- Valeurs de champ paramétrables dans l'outil d'administration : oui
- Chemin d'accès dans l'outil d'administration : `/admin/trekking/difficultylevel/ </admin/trekking/difficultylevel/>`_ 
- Visibilité : publique
- Exemple : Intermédiaire

**Pratique** ~ Recommandé

- Description : type de pratique de l'itinéraire
- Type : liste déroulante
- Choix : unique
- Valeurs de champ paramétrables dans l'outil d'administration : oui
- Chemin d'accès dans l'outil d'administration : `/admin/trekking/practice/ </admin/trekking/practice/>`_  
- Visibilité : publique
- Exemple : Pédestre

**Échelle de cotation**

- Description : définition d'une cotation de l'itinéraire spécifique à la pratique
- Type : liste déroulante
- Choix : unique
- Conditionnel : selon la pratique choisie
- Valeurs de champ paramétrables dans l'outil d'administration : oui
- Chemin d'accès dans l'outil d'administration : `/admin/trekking/ratingscale/ </admin/trekking/ratingscale/>`_ 
- Visibilité : publique
- Exemple : Technicité : 3 - Moyen

**Description de cotation [fr]**

- Description : précision sur la valeur de cotation de l'itinéraire spécifique à la pratique
- Type : champ libre
- Visibilité : publique
- Exemple : La technicité de cet itinéraire est moyenne car elle ne comprend pas de passages délicats.

**Parcours**

- Description : type de parcours
- Type : liste déroulante
- Choix : unique
- Valeurs de champ paramétrables dans l'outil d'administration : oui
- Chemin d'accès dans l'outil d'administration : `/admin/trekking/route/ </admin/trekking/route/>`_ 
- Visibilité : publique
- Exemple : Boucle

**Accès routier [fr]**

- Description : accès routier jusqu'au point de départ
- Type : champ libre
- Visibilité : publique
- Exemple : Depuis Savines-Le-Lac (17km), prendre la D41 jusqu'à Réallon. Suivre ensuite la D241 jusqu'au hameau des Gourniers au fond de la vallée.

**Chapeau [fr]** ~ Recommandé

- Description : bref résumé de l'itinéraire avec accroche
- Type : champ libre
- Visibilité : publique
- Exemple : Une agréable randonnée familiale en boucle avec un beau point de vue sur la vallée de Réallon.

**Ambiance [fr]**

- Description : attractions principales et intérêts
- Type : champ libre
- Visibilité : publique
- Exemple : La montée commence dans la fraîcheur d'un bois de hêtre puis d'une belle forêt de mélèzes avant d'arriver à d'anciens près de fauche, témoignage des activités passées. Les ruines d'anciens chalets d'alpage rappellent ce qu'était la vie en montagne. Quand le sentier passe en balcon le paysage s'ouvre en un large point de vue sur la vallée de Réallon.

**Description [fr]**

- Description : description technique pas à pas de l'itinéraire (liste numérotée conseillée)
- Type : champ libre
- Visibilité : publique
- Exemple : Du parking, traverser le pont, au carrefour du hameau prendre la direction de Chargès, remonter la rue jusqu'à la dernière maison.

1. Prendre le sentier à droite direction l'Oussella
2. Après la marmite de Géant et le pont, continuer à gauche direction l'Oussella.

3.1.1.2 Avancé
~~~~~~~~~~~~~~

**Parking conseillé [fr]**

- Description : nom du lieu recommandé pour se garer en voiture
- Type : champ libre
- Visibilité : publique
- Exemple : Parking du refuge de les Caussis.

**Transport en commun [fr]**

- Description : indications du ou des transports en commun pour se rendre au départ
- Type : champ libre
- Visibilité : publique
- Exemple : Ce GR est accessible en train, il démarre de la gare SNCF de Boussenac (ligne Seix - Boussenac).

**Recommandations [fr]**

- Description : recommandations sur les risques, danger ou meilleure période pour pratiquer l'itinéraire
- Type : champ libre
- Visibilité : publique
- Exemple : Attention en cas d'orage. Fortement déconseillé par mauvais temps!

**Matériel [fr]**

- Description : matériel nécessaire ou conseillé
- Type : champ libre
- Visibilité : publique
- Exemple : Chaussures de randonnées

**Thèmes**

- Description : thématiques principales de l'itinéraire
- Type : liste déroulante
- Choix : multiple
- Valeurs de champ paramétrables dans l'outil d'administration : oui
- Chemin d'accès dans l'outil d'administration : `/admin/common/theme/ <//admin/common/theme/>`_
- Visibilité : publique
- Exemple : Lacs et glaciers, Géologie, Point de vue

**Étiquettes**

- Description : éléments de recommandation ou utiles à connaître
- Type : liste déroulante
- Choix : multiple
- Valeurs de champ paramétrables dans l'outil d'administration : oui
- Chemin d'accès dans l'outil d'administration : `/admin/common/label/ </admin/common/label/>`_ 
- Visibilité : publique
- Exemple : Chien autorisé

**Réseaux**

- Description : nom du réseau de balisage de l'itinéraire
- Type : liste déroulante
- Choix : multiple
- Valeurs de champ paramétrables dans l'outil d'administration : oui
- Chemin d'accès dans l'outil d'administration : `/admin/core/network/ </admin/core/network/>`_ 
- Visibilité : publique
- Exemple : GR

**Liens web**

- Description : liens web apportant des compléments d'informations utiles
- Type : liste déroulante
- Choix : multiple
- Valeurs de champ paramétrables dans l'outil d'administration : oui
- Chemin d'accès dans l'outil d'administration : `/admin/trekking/weblink/ </admin/trekking/weblink/>`_ 
- Visibilité : publique
- Exemple : `Consulter la météo locale de Boussenac <https://meteofrance.com/previsions-meteo-france/boussenac/09320>`_ 

**Lieux de renseignement**

- Description : lieux de renseignements utiles
- Type : liste déroulante
- Choix : multiple
- Valeurs de champ paramétrables dans l'outil d'administration : oui
- Chemin d'accès dans l'outil d'administration : `/admin/tourism/informationdesk/ </admin/tourism/informationdesk/>`_
- Visibilité : publique
- Exemple : Office de tourisme de Seix, Office du tourisme de Boussenac

**Source**

- Description : nom de l'organisme auteur de l'itinéraire
- Type : liste déroulante
- Choix : multiple
- Valeurs de champ paramétrables dans l'outil d'administration : oui
- Chemin d'accès dans l'outil d'administration : `/admin/common/recordsource/ </admin/common/recordsource/>`_
- Visibilité : publique
- Exemple : Conseil départemental de l'Ariège

**Portail**

- Description : site web grand public sur lequel sera publié l'itinéraire
- Type : liste déroulante
- Choix : multiple
- Valeurs de champ paramétrables dans l'outil d'administration : oui
- Chemin d'accès dans l'outil d'administration : `/admin/common/targetportal/ </admin/common/targetportal/>`_
- Visibilité : publique
- Exemple : CD09

**Enfants**

- Description : ensemble des itinéraires étapes constituant l'itinérance
- Type : liste déroulante
- Choix : multiple
- Visibilité : publique
- Exemple : Etape GR09 Refuge les Caussis-Étang Rond, Etape GR09 Étang Rond-Refuge les Caussis.

**ID externe**

- Description : identifiant de l'itinéraire dans sa base de données source (dans le cas d'un import)
- Type : numérique
- Visibilité : interne
- Exemple : 15715

**Deuxième id externe**

- Description : identifiant secondaire de l'itinéraire dans sa base de données source (dans le cas d'un import)
- Type : numérique
- Visibilité : interne
- Exemple : 15716

**Système de réservation**

- Description : nom du système de réservation
- Type : liste déroulante
- Choix : unique
- Valeurs de champ paramétrables dans l'outil d'administration : oui
- Chemin d'accès dans l'outil d'administration : `/admin/common/reservationsystem/ </admin/common/reservationsystem/>`_ 
- Visibilité : publique
- Exemple : Open system

**ID de réservation**

- Description : identifiant de l'itinéraire dans son système de réservation
- Type : numérique
- Visibilité : interne
- Exemple : 157187456

**POI exclus**

- Description : liste des points d'intérêt associés à l'itinéraire à ne pas faire remonter sur celui-ci
- Type : liste déroulante
- Choix : multiple
- Visibilité : interne
- Exemple : les Estagnous

3.1.1.3 Accessibilité
~~~~~~~~~~~~~~~~~~~~~~

**Type d'accessibilité**

- Description : type d'accessibilité
- Type : liste déroulante
- Choix : multiple
- Valeurs de champ paramétrables dans l'outil d'administration : oui
- Chemin d'accès dans l'outil d'administration : `/admin/trekking/accessibility/ </admin/trekking/accessibility/>`_ 
- Visibilité : publique
- Exemple : Fauteuil roulant, poussette

**Niveau d'accessibilité**

- Description : niveau d'accessibilité
- Type : liste déroulante
- Choix : unique
- Valeurs de champ paramétrables dans l'outil d'administration : oui
- Chemin d'accès dans l'outil d'administration : `/admin/trekking/accessibilitylevel/ </admin/trekking/accessibilitylevel/>`_  
- Visibilité : publique
- Exemple : Débutant

**Aménagements d'accessibilité [fr]**

- Description : infrastructure d'accessibilité spécifique à disposition
- Type : champ libre
- Visibilité : publique
- Exemple : Rampes d'accès amovibles.

**Pente accessibilité [fr]**

- Description : description de la pente : supérieure à 10 % (Nécessite une assistance quand la pente est supérieure à 8%) 
- Type : champ libre
- Visibilité : publique
- Exemple : Pente supérieure à 12%.

**Revêtement accessibilité [fr]**

- Description : description des revêtements rencontrés sur la totalité d’un itinéraire
- Type : liste déroulante
- Visibilité : publique
- Exemple : Piste ensablée à partir des Estagnous.

**Exposition accessibilité [fr]**

- Description : description des expositions et des zones ombragées
- Type : champ libre
- Visibilité : publique
- Exemple : Piste ombragée.

**Largeur accessibilité [fr]**

- Description : description des rétrécissements des sentiers et la largueur minimum
- Type : champ libre
- Visibilité : publique
- Exemple : Sentier étroit demandant une forte technique de conduite, avec un passage d'un mètre de large. Passage resserré sur le pont traversant la rivière.

**Conseil d'accessibilité [fr]**

- Description : éléments particuliers permettant d’apprécier le contexte de l’itinéraire pour les PMR (conseils, passages délicats, etc.)
- Type : liste déroulante
- Visibilité : publique
- Exemple : La montée du Saut du Laire, particulièrement les 150 derniers mètres, sont déconseillés aux joëlettes, notamment dans la perspective du retour en descente sur pavé pouvant être glissant.

**Signalétique accessiiblité [fr]**

- Description : description de taille, forme et couleurs des signalétiques d'accessibilité
- Type : liste déroulante
- Visibilité : publique
- Exemple : Panneau de signalisation PMR rampe d'accès amovible.


3.1.2 Itinérance
----------------

Il est possible de créer des randonnées itinérantes (sur plusieurs jours) et d'y associer des étapes comme sur cet exemple : https://www.grand-tour-ecrins.fr/trek/937571-GR%C2%AE54---Tour-de-l-Oisans-et-des-Ecrins.

Pour cela il faut créer un itinéraire parent (séjour itinérant complet) puis y ajouter des itinéraires enfants (étapes) de manière ordonnée, dans le champs `Enfants` présent dans l'onglet `Avancé` du formulaire itinéraire du séjour complet.

Le séjour complet ainsi que chaque étape sont donc chacunes des randonnées comme les autres. La seule différence est que les étapes (itinéraires enfants) sont rattachées à l'itinéraire parent.

Si vous ne souhaitez pas que les étapes soient affichées dans la page de Recherche de Geotrek-rando, il ne faut pas les publier. Il suffit alors de publier l'itinéraire parent, pour que toutes les étapes qui y sont rattachées apparaissent uniquement dans sa fiche détail de Geotrek-rando.

3.1.3 Points de référence
--------------------------

Lorsque l'on localise un itinéraire, il est aussi possible de localiser le parking de la randonnée et de placer des points de référence numérotées sous forme de puces rouges sur la carte.

Ces derniers servent à y faire référence dans le champs Description de l'itinéraire (Pas à pas) :

.. image :: /images/user-manual/references-geotrek-rando.jpg

Pour que des puces numérotées sous forme de pastilles rouges soient affichées dans la description, il suffit de les saisir en tant que Liste numérotées dans le champs Description :

.. image :: /images/user-manual/references-geotrek-admin.jpg

3.1.4 Ordre des catégories
---------------------------

Dans le portail Geotrek-rando, les différents types de contenus sont éclatés en catégories.

Pour définir leur ordre d'affichage, il est possible de le définir dans la base de données pour certains contenus (ordre des pratiques et des catégories de contenus touristiques) en renseignant leur champs ``ordre`` depuis l'Adminsite de Geotrek-admin.

Pour l'ordre d'affichage des catégorie Randonnées, Itinérance et Evènements touristiques, il est possible de modifier les valeurs par défaut définies dans le fichier ``geotrek/settings/base.py`` en surcouchant les paramètres correspondant dans le fichier de configuration avancée ``geotrek/settings/custom.py`` :

- ``TREK_CATEGORY_ORDER = 1``
- ``ITINERANCY_CATEGORY_ORDER = 2``
- ``TOURISTIC_EVENT_CATEGORY_ORDER = 99``

Il est aussi possible d'éclater les randonnées pour que chaque pratique soit une catégorie en surcouchant le paramètre ``SPLIT_TREKS_CATEGORIES_BY_PRACTICE = False``, d'éclater les types d'accessibilité en catégories avec le paramètre ``SPLIT_TREKS_CATEGORIES_BY_ACCESSIBILITY = False`` et de séparer les randonnées itinérantes dans une catégorie avec le paramètre ``SPLIT_TREKS_CATEGORIES_BY_ITINERANCY = False``.

.. _points-d-interets-poi:

3.2 Points d'intérêts (POI)
===========================

Pour importer automatiquement des éléments de POIs, se référer à la section :ref:`Import POIs <import-pois>`

.. _services:

3.3 Services
============

.. _contenus-touristiques:

3.4 Contenus touristiques
=========================

.. _evenements-touristiques:

3.5 Évènements touristiques
===========================

.. _signalements:

3.6 Signalements
================

Pour configurer Suricate, se référer à cette section :ref:`Suricate support <suricate-support>`

.. _zones-sensibles:

3.7 Zones sensibles
===================

Pour activer le module Zones sensibles, se référer à cette section :ref:`Sensitive areas <sensitive-areas>`

.. _sites-outdoor:

3.8 Sites outdoor
=================

Pour activer le module Zones sensibles, se référer à cette section :ref:`Outdoor <outdoor>`

.. _parcours-outdoor:

3.9 Parcours outdoor
====================

Pour activer le module Zones sensibles, se référer à cette section :ref:`Outdoor <outdoor>`

