##################
TESTS FONCTIONNELS
##################

Ce document a pour objectif de recetter les stories réalisées pendant les
sprints. 

À chaque story correspond un scénario de validation des fonctionnalités et 
du comportement attendu.


========================
Sprint 1 - Version 0.1.0
========================

#88 - Automatiser l'installation
--------------------------------

Se référer à la section deployment du fichier ``README.rst`` à la racine
du projet.

Le processus d'installation demande la saisie des paramètres nécessaires.

Le projet est ensuite accessible à l'URL du serveur.

:Problèmes connus:

    ``supervisord`` ne démarre pas tout seul au reboot.
    Le paramètre ``rooturl`` non vide pose problème (404) dans la partie *admin*.


#90 - Fournir spécifications serveur
------------------------------------

c.f. ``README.rst``.


#84 - Afficher l'interface dans la langue de l'utilisateur
----------------------------------------------------------

Dans l'interface d'administration, créer un utilisateur. La langue par défaut
est le français, les choix sont EN, FR, IT.

Se connecter avec cet utilisateur, vérifier que l'interface s'affiche dans 
sa langue. 

:note: 

    Un changement de langue dans le profil n'est pris en compte qu'après reconnexion.

#10 - Éditer les listes de choix avec l'AdminSite Django
--------------------------------------------------------

- Scénario 1 - CRUD et liaison à une structure

    * Connexion avec un compte admin.
    * CRUD prestataire (par exemple)
    * Association avec une structure précise

- Scénario 2 - CRUD et traduction

    * Connexion avec un compte admin.
    * Changer la langue du compte.
    * Vérifier que les menus et les formulaires des objets sont bien traduits dans
      la langue de l'utilisateur

- Scénario 3 - CRUD et champs multilingues

    * CRUD "usages" (par exemple)
    * Traduction d'un même enregistrement en anglais/francais/italien
    * Vérification de la bonne traduction de cet élement dans l'interface en fonction de la langue
      de l'utilisateur


#15 - Limiter les listes de choix à ceux de la structure de l'utilisateur
-------------------------------------------------------------------------

Créer plusieurs objets, associés à des structures différentes (ex: prestataires).

Vérifier que la liste (temporaire au sprint 1) affichée dans l'interface contient 
bien les objets crées.

Si je change la structure de l'utilisateur. La liste des objets associés à la structure change.

Si je change la structure d'un objet, il n'apparait plus dans la liste.


#30 - Montrer la carte globale sur la page d'accueil
----------------------------------------------------

La page d'accueil affiche une carte avec les tronçons. 

:note:

    Pour l'instant, la carte est en projection 4326 (attente fin POC #12).
    
    Les performances ne sont pas au rendez-vous (6 sec. pour générer le fichier, 11 millisec. pour l'afficher)


#94 - Activer le système de cache Django
----------------------------------------

Pas de test spécifique, à part vérifier que les réponses du serveur sont
extrèmement plus rapides que lorsque le cache est vide (i.e. après déploiement).


#28 - Paramétrer l'étendue du territoire
----------------------------------------

La carte de la page d'accueil est restreinte à la zone du parc en fonction
du setting ``SPATIAL_EXTENT``.

Ce dernier doit être exprimé dans le système de coordonnées du setting ``SRID``.

:note:

    Pour l'instant, le paramètre est exprimé en dur, en coordonnées 4326 (attente fin POC #12).


#27 - Affecter automatiquement le zonage/commune/secteurs aux objets crées/modifiés
-----------------------------------------------------------------------------------

Les notions d'évènement n'étant pas disponible dans l'interface, il faut tester
avec PgAdmin et/ou QGIS.

* Éditer un tronçon (ajout/suppression/modification)
* Dans PgAdmin, on peut constater que les tables permettant l'association avec
  les communes/secteurs/zonages ont été mises à jour. (Ces tables sont :
  evenements_troncons, evenements et zonage/commune/secteur).

#104 - Recalculer la longueur des tronçons et évènements par trigger
--------------------------------------------------------------------

L'édition des tronçons et évènements n'étant pas disponible dans l'interface,
il faut tester le trigger avec QGis et PgAdmin.

Éditer la géométrie d'un tronçon existant, ou créer un nouveau tronçon, 
vérifier que le champ ``longueur`` est bien (re)calculé.

La géométrie (et longueur) de l'évènement n'est pas mise à jour pour le moment,
ce sera fait dans un second temps.


#86 Implémenter logique simple de base de l'affichage / édition des entités
---------------------------------------------------------------------------
Créer un petit workflow CRUD : liste -> affichage -> édition pour les troncons


#17 - Gérer les permissions d'accès aux modules en fonction des groupes
-----------------------------------------------------------------------

Lorsque je me connecte en tant que "référents sentiers" ou en tant
qu'administrateur, les boutons pour ajouter/modifier/supprimer un sentier sont
actifs.

Lorsque je me connecte avec un autre utilisateur, les boutons sont inactifs et
si j'essaye de forcer l'accès en allant directement à l'URL :

    http://server/path/edit/73/

Je suis redirigé vers la vue de détail (en lecture seule) de cet objet.

Les utilisateurs de tests sont :

* sentiers/sentiers (référent sentier - autorisé)
* admin/admin (administrateur - autorisé)
* comm/comm (référent communication - non autorisé)
* redacteur/redacteur (rédacteur - non autorisé)

:note:

    La notion de droit incrémental sera implémentée plus tard, lorsque
    nous travaillerons sur la connexion avec le système de gestion des
    utilisateurs du parc.

:note:

    Les droits ne sont gérés que pour les sentiers pour le moment. La
    gestion module par module arrivera plus tard.


#16 - Gérer la projection de l'application dans un settings
-----------------------------------------------------------

c.f. procédure d'installation.


#97 - Pouvoir éditer les structures associées des modèles dans l'AdminSite Django
---------------------------------------------------------------------------------

c.f. story #10


#98 - Marquer pour traduction (et traduire) chaque champs et méthode unicode
----------------------------------------------------------------------------

c.f. story #84


#105 - Créer certains helpers de tests indispensables
-----------------------------------------------------

*(interne)*


#2 - Valider le MCD
-------------------

cf. CCTP_annexe1-MCD.pdf


#14 - Maquettes admin sentiers (Anaïs)
--------------------------------------

N/A


#9 - Lister et numéroter tous les triggers nécessaires
------------------------------------------------------

Cf. sentiers-triggers.rst


#31 - Éditer plusieurs langues pour un même champ texte
-------------------------------------------------------

N/A


#12 - [POC Carto] Édition Lambert93 dans Leaflet
------------------------------------------------

N/A


#85 - Implémenter le squelette du MCD
-------------------------------------

N/A



========================
Sprint 2 - Version 0.2.0
========================

#95 - Draper les tronçons sur le MNT
------------------------------------

* Visualiser le profil altimétrique d'un tronçon.
* Modifier sa géométrie.
* Vérifier que le profil a changé.

:notes:

    Toutes les informations pour charger le DEM sont dans le fichier README.


#18 - Gérer les permissions d'édition des objets en fonction de la structure
----------------------------------------------------------------------------

* Se logger avec un utilisateur du groupe *Référant sentiers* de la structure PNE.
* Vérifier que l'édition des tronçons est accessible.
* Changer la structure d'un tronçon.
* Vérifier qu'il n'est plus possible d'accéder au formulaire d'édition avec ce même utilisateur.

:question:

    Doit-on permettre le changement de structure depuis le formulaire au risque
    que l'utilisateur perde accès à l'objet ?


#36 - Charger la liste des tronçons en asynchrone
-------------------------------------------------

* Ouvrir la page des tronçons, la liste est vide pendant une fraction de secondes.
* Vérifier que la liste se charge correctement en asynchrone. Par exemple
  avec l'inspecteur Firebug, vérifier que les données JSON sont reçues et la 
  liste est raffraichie.


#45 - Afficher la carte centrée des objets dans la fiche détails
----------------------------------------------------------------

* Afficher la fiche d'un tronçon.
* Une carte en lecture seule se charge, centrée sur le tronçon.
* La couche avec les autres tronçons se charge en asynchrone.


#118 - Ajouter un formulaire de filtres basique sur les tronçons
----------------------------------------------------------------------------

* connexion avec un utilisateur
* la liste est complète
* remplissage du formulaire: filtre sur longueur des troncons
* vérification que la liste est bien filtrée
* vérification que la carte est bien filtrée


#117 - Servir le profil altimétrique d'un tronçon en JSON
---------------------------------------------------------

* ouvrir la vue de détail d'un troncons
* dans l'URL, ajouter "profile/" à la fin
* le fichier reçu est encodé en JSON, il contient des paires (distance
  cumulée, altitude) pour chaque point du chemin

Cela sert à tracer le profil altimétrique à l'aide d'une bibliothèque de
dessin de courbes.

#21, #108 - Modifier la géométrie d'un tronçon
----------------------------------------------

* Afficher la fiche d'un tronçon, passer en mode édition.
* Le champ géometry dans le formulaire a été remplacé par une carte.
* Il est possible de modifier la géométrie en ajustant les points.
* La sauvegarde enregistre les valeurs des champs du formulaire et la géométrie.
* Si une erreur de saisie est levée sur un champ du formulaire, la géométrie saisie précedemment est conservée.

#87 - Découper l'application en modules
---------------------------------------

Seuls Tronçons et Interventions ne sont activés pour l'instant.

:notes:

    Cette story consistat à écrire tout le code source pour activer facilement les modules
    de manière générique.

#119 - Servir le graphe du réseau de sentiers
---------------------------------------------

Ce graphe représente toutes les connexions entre les tronçons du sentier.
Il servira à calculer les itinéraires au sain du parc, notamment pour la saisie
multi-tronçons à-la Google Maps.

Il est accessible en JSON à l'url ``/data/graph.json``.

#107 - Ajouter un tronçon
-------------------------

* Lors de l'ajout d'un tronçon, l'utilisateur peut le dessiner sur la carte
* Seul le mode linéaire est autorisé
* L'utilisateur peut supprimer son précédent tronçon pour en recréer un
* La suppression d'un tronçon intervient lorsque l'utilisateur dessine le
  premier point d'un nouveau tronçon
* Le tronçon créé doit pouvoir être édité.


#56 - Snapper les tronçons lors de la saisie
--------------------------------------------

* Ouvrir l'édition d'une géomtrie
* Bouger les point d'accroche, noter qu'ils s'attachent aux tronçons au deça
  d'une certaine distance. Leur couleur change quand ils sont attachés.
* À l'ouverture d'une géométrie existante, les point d'accroche attachés aux
  tronçons sont colorés.

:notes:

    Le snap n'est disponible qu'à un certain niveau de zoom afin de garantir
    une fluidité sur l'accroche. En effet, à chaque mouvement des point d'accroche,
    les objets présents à l'écran doivent être itérés pour calculer les distances 
    d'accroche. Un niveau de zoom élevé garanti un nombre restreint d'objets
    affichés (<1000).

#34 - Inverser un tronçon
-------------------------

Aller sur le formulaire d'un tronçon. Cocher "inverser". Sauvegarder.
Noter que le profil altimétrique est inversé.


#109 - Ajouter une intervention ponctuelle
------------------------------------------

Lors de l'ajout d'une intervention, l'utilisateur peut choisir entre un point
et une saisie multi-tronçons.

:notes:

    Les boutons actuels des controles sont trop petits.


#113 - Passer les cartes en tuiles L93
--------------------------------------

Les cartes de l'application sont désormais en Lambert-93, avec les Scan
par défaut.

:notes:

    L'orthophoto ne fonctionne pas.
    Le cache de tuiles n'est pas déployé avec le projet. C.f. story #112.


#124 - Ajouter un cache intelligent
-----------------------------------

* Visualiser la couche des tronçons une 1ère fois. Cela prend plusieurs secondes.
* Visualiser la couche des tronçons une 2ème fois, c'est instantané.
* Modifier un tronçon.
* Visualiser la couche des tronçons. Cela prend à nouveau plusieurs secondes.

On peut forcer le raffraichissement en vidant le cache (Ctrl+F5 du navigateur).


#130 - Intégrer les onglets
---------------------------

Les onglets s'activent en fonction du module et de la page visitée.


#114 - Ajouter une intervention liée à X tronçons
-------------------------------------------------

Depuis le formulaire d'édition d'intervention.

Choisir le controle "Multipaths", au dessous du controle d'ajout de point.

* Cliquer un premier tronçon, puis un deuxième.
* Les tronçons intermédiaires se sélectionnent (plus court chemin). 
  La géométrie stockée est l'union des tronçons sélectionnés.

Si je reclique sur le controle, l'ancien tracé s'efface et je peux à nouveau refaire faire un calcul d'itinéraire

:notes:

    Problème connu: le tracé d'une intervention existante n'est pas chargée à l'ouverture
    du formulaire.

    À l'avenir, nous aurons un sélecteur d'itinéraires à-la Google Maps.


========================
Sprint 3 - Version 0.3.0
========================

#137 - Améliorer la navigation
------------------------------

Désormais, la liste des modules n'est présente que dans l'onglet recherche.


#127 - Séparer le code d'un futur django-mapentity
--------------------------------------------------

Story purement technique (pour réutilisabiliter notamment).

Création d'une app dans caminae, mapentity (pas de repo git à part pour l'instant)
contenant les différents aspects génériques (MapEntityMixin et création d'url principalement).

Le code JS présent dans formfieldmap.html fera aussi l'objet d'une extraction dans un JS à part
pour pouvoir être réutilisable.

Les Widgets ne sont pas concernés (ils seront intégrés éventuellement plus tard comme contrib à floppyforms)


#40 - Filtrer les objets de la liste en fonction de l'étendue de la carte affichée
----------------------------------------------------------------------------------

** recette **

En plus des filtres déjà présents, je peux filtrer géographiquement par l'étendue courante visible de carte.
Lors de chaque déplacement, la liste est mise à jour pour n'afficher que les objets visibles sur la carte.
La réinitialisation du formulaire réinitialise de plus la carte à son étendue de départ.
Un 'spinner' sur la carte représentera l'avancement du filtrage.

:notes:

    Détail d'implémentation 1: la bbox n'est pas fournie conventionnellement selon ?bbox=minx,miny,maxx,maxy mais comme un WKT.
    C'est un choix plus pratique car les fonctions de conversion (côté js et django) existent déjà
    qui peuvent éviter de potentiels problèmes  (ex: gestion de la coordonnée Z, de la projection, etc.).
    La gestion du filtrage via une géométrie quelconque est de plus réutilisable (ex. secteurs, communes, etc.)

    Détail d'implémentation 2: lorsque le tri est purement géographique (mouvement de carte uniquement),
    les objets présents sur la carte (contrairement à la liste des résultats) ne sont pas retirés
    (mais ne sont pas visibles bien sûr) pour des raisons de performance.


#138 - Lister les dernières fiches consultées
---------------------------------------------

Les onglets listent les dernières fiches consultées dans la session de l'utilisateur.

Une fiche n'apparait toujours qu'une seule fois. L'onglet le plus à gauche est
celui de la fiche en cours, puis suivent les fiches consultées précedemment,
s'il y en a.

Un setting détermine le nombre maximal à afficher (``HISTORY_ITEMS_MAX``).


#139 - Conserver la dernière recherche effectuée
------------------------------------------------

* Effectuer une recherche en choisissant un module
* Le nombre de résultats s'affiche dans l'onglet
* Consulter une fiche, retourner à la recherche. Le module sélectionné précédement est actif.

* Appliquer des filtres.
* Consulter une fiche et revenir à la recherche. Les filtres saisis sont restaurés.

* Vérifier que l'étendue de la carte et les couches affichées sont également restaurées.


#141 - Implémenter l'ensemble des modules
-----------------------------------------

L'ensemble des entités manipulées dans l'application sont disponibles.

:notes: 

    Bien entendu, tout n'est pas fonctionnel. Mais cette étape permet de
    valider la navigation dans l'application.


#142 - Distinguer les formulaires d'ajout et de modification des interventions
------------------------------------------------------------------------------

À la création, le formulaire de demande d'intervention contient un minimum
de champ, et seul le status "souhaitée" est disponible.


#148, #149 - Afficher les fiches sentiers
-----------------------------------------

Il est désormais possible d'accéder à la fiche d'un sentier. Ces objets
ne sont cependant pas éditables.


#37 - Sélectionner un objet sur la carte le sélectionne dans la liste. Et vice-versa
------------------------------------------------------------------------------------

Dans la vue de liste de chaque entité:
- un clic de l'entité sur la carte sélectionne dans la liste ajax (avec changement de page)
- vice-versa, un clic sur une ligne dans la liste ajax sélectionne l'entité sur la carte

Une seule entité peut être sélectionnée à la fois, une nouvelle sélection (clic carte ou liste)
entraine la déselection de la précédente entité selectionnée.

Un clic carte ou liste sur une entité déjà sélectionnée entraine sa déselection.

Une sélection se traduit dans le tableau et dans la carte par un style spécifique.

Un double clic de l'entité sur la carte affiche la fiche détail.
Un clic sur le lien de la 1ere colonne (ex. nom) affiche la fiche détail.


#159 - Afficher la couche des tronçons sur tous les modules
-----------------------------------------------------------

Dans le sélecteur de couches, il est désormais possible d'afficher la couche des tronçons. 
Les objets de celle-ci ne sont pas clickables.

Décocher la couche. Elle disparait. Raffraichir la page. La couche n'est toujours pas affichée.

Aller sur la page des tronçons. La couche apparait. Revenir sur un autre module, la 
couche est redevenue visible.

#127 - Ajouter une intervention sur un aménagement
--------------------------------------------------

Aller sur la fiche d'un aménagement (ou signalétique).

La liste des interventions est vide. Ajouter une intervention.

La géométrie de l'aménagement est affichée, en lecture seule.

Sauvegarder le formulaire.

Retourner sur la fiche de l'aménagement, l'intervention apparait.


#135, #161, #162, #135, #160 - Saisie des topologies
----------------------------------------------------

Ajouter une nouvelle intervention. 

Il y a deux contrôles disponibles : ligne et point. 

Saisir un point revient à poser un marqueur. Saisir une line revient à placer
deux marqueurs.

Sauvegarder.

Éditer l'intervention précedemment crée. Le(s) marqueur(s) est présent à l'endroit saisi.


#122 - Mettre à jour la géométrie des évènements
------------------------------------------------

Pour créer un évènement, on pourra utiliser SQL ou l'interface :

* via l'interface, créez un évènement quelconque en cliquant une ou deux fois
  sur la carte.

* en SQL via PgAdmin3, ajoutez d'abord un enregistrement dans la table
  ``evenements`` puis ajoutez un ou plusieurs enregistrements dans la table de
  jointure ``evenements_troncons``, les tronçons existent déjà quant à eux.

De même pour consulter la géométrie, on pourra utiliser QGIS, PgAdmin3 ou
l'interface, dans la fiche détail.

Après chaque insertion, modification ou suppression dans la table
troncons_evenements, on pourra constater avec QGIS ou PgAdmin3 que l'évènement
lié porte bien une géométrie reflétant sa description (liste de tronçon avec PK
début et PK fin + décallage).

Après modification ou suppression d'un tronçon, on peut également vérifier que
les évènements liés portent bien une géométrie reflétant leur description.

Après modification du décallage d'un évènement, on peut également vérifier que
sa géométrie est modifiée pour refléter sa description.


Évènements invalides :

* Lorsque les tronçons forme une ligne discontinue, seul le
  premier morceau apparait dans la géométrie de l'évènement.
* Lorsqu'un évènement ponctuel est associé à plusieurs tronçons, la
  géométrie est laissée en l'état.


#81 - Activer la saisie des topologies pour toutes les entités
--------------------------------------------------------------

Seules les lignes sont autorisées pour les itinéraires et la gestion foncière.

Seuls les points sont autorisés pour les POI.

Pour tout le reste (aménagements, interventions), les lignes et points sont autorisés.


#160 - Calculer la géométrie d'une topologie
--------------------------------------------

Lors de l'ajout, édition ou détail d'une topologie sa géométrie exacte est affichée.

Une topologie de point est représenté par un marqueur.

Une topologie de ligne est représentée par des tronçons coloriés en jaune encadrés par des marqueurs de début et de fin.
Le décalage (offset) n'est pas pris en compte pour la topologie de ligne.


#136 - Utiliser des marqueurs pour le départ et l'arrivée de la saisie multitronçons
------------------------------------------------------------------------------------

Lors de la saisie multitronçon, un clic sur un tronçon pose un marqueur de début (vert),
un second clic sur un tronçon pose un marqueur de fin (rouge) et révèle le trajet le plus
court (en jaune) du début à la fin.

Ces marqueurs sont automatiquements "snappés" sur les tronçons.
Je peux déplacer les marqueurs (de début ou de fin):

- si les marqueurs sont tous les deux "snappés" à un tronçon pendant le mouvement ou après,
  la saisie est considérée comme valide et le trajet le plus court est mis à jour en temps réel.
- si un des deux marqueurs n'est pas sur un tronçon, la saisie est invalide et le trajet le plus
  court n'est pas visible.




==========================
Sprint 3.1 - Version 0.3.1
==========================

#125 - Compresser les medias
----------------------------

* Ouvrir la source HTML d'une page

* Vérifier que les Javascript et CSS requis dans la balise ``<head>`` ont
  des noms générés (ex: c28e793a0354.js)

* Ouvrir l'un de ces fichiers, vérifier que le contenu est compressé.


#102 - Calculer automatiquement l'enjeux par défaut d'une intervention
----------------------------------------------------------------------

* Définir l'enjeu d'un tronçon au maximum

* Créer une intervention et un aménagement sur ce tronçon (en y incluant d'autres éventuellement)

* Créer une intervention sur l'aménagement créé.

* Vérifier que les enjeux des deux interventions créées correspondent bien à l'enjeu du tronçon.

* Modifier l'enjeu d'une intervention, vérifier que cette valeur est conservée.


#32 - Éditer en Wysiwyg les champs texte
----------------------------------------

* Ouvrir n'importe quel formulaire, chaque champ texte contient un petit éditeur
  Wysiwyg (TinyMCE) avec les options de base.

* Le champ est sauvegardé avec le texte au format HTML.


#47 - Accéder facilement aux fiches des objets liés à un objet
--------------------------------------------------------------

* S'assurer qu'il existe au moins quelques données de démonstration pour les
  types d'objets "tronçon", "intervention", "chantier", "signalétique",
  "aménagement", "foncier", "itinéraire" et "POI"

* Aller sur la fiche d'un tronçon et suivre les liens vers les tronçons
  fonciers, les interventions, les chantiers, les signalétiques et les
  aménagements.

* Aller sur la fiche d'une intervention et suivre les liens vers les tronçons.
  La fiche indique également si l'intervention porte sur un aménagement ou
  signalétique et si elle fait partie d'un chantier.

* Aller sur la fiche d'un chantier et suivre les liens vers les tronçons, les
  signalétiques et les aménagements.

* Aller sur la fiche d'une signalétique et suivre les liens vers les tronçons
  et les interventions.

* Aller sur la fiche d'un aménagement et suivre les liens vers les tronçons et
  les interventions.

* Aller sur la fiche d'un itinéraire et suivre les liens vers les tronçons et
  les POIs.

* Aller sur la fiche d'un POI et suivre le lien vers les itinéraires.

#146 - Enlever les types liées à la signalétique dans le formulaire infrastructure
----------------------------------------------------------------------------------

* Aller sur le formulaire de création d'un aménagement. Le champs type ne doit
  lister que les types non-associés à la signalétique


# 147 - Enlever les types liées aux infrastructures dans le formulaire signalétique
-----------------------------------------------------------------------------------

* Aller sur le formulaire de création d'une signalétique. Le champs type ne
  doit lister que les types associés à la signalétique


#166 - Champ structure automatique dans les formulaires
-------------------------------------------------------

Les formulaires de création et d'édition n'ont plus de champ "structure".

* Créer une intervention, sauvegarder. Dans la fiche détail, vérifier que la structure
  est celle de l'utilisateur.

* Se connecter avec un utilisateur d'une autre structure. 

* Créer une intervention et vérifie que la structure correspond bien.

:notes:

    Dans la partie Admin, ce n'est pas implémenté.


#120 - Filtrer les listes de choix par structure
------------------------------------------------

Les formulaires ont des listes de choix limitées aux éléments de la structure
de l'utilisateur.

* Vérifier avec les tronçons : ouvrir le formulaire d'ajout de tronçon avec
  un utilisateur. Observer la liste des choix d'enjeu par exemple.

* Changer la structure de l'utilisateur. Se déconnecter puis se reconnecter.

* Observer que la liste des choix des enjeux a changé.


#151 - [BUG] Certains boutons de l'adminsite ne sont pas traduits
-----------------------------------------------------------------

Pas reproduit : 

* Passer l'utilisateur en langue It

* Se déconnecter, se reconnecter

* L'application est en italien. L'adminsite est totalement traduit ("Aggiungi", "Modifica"), 
  l'application sentier en l'est que partiellement (ex: "cerca", "filtra")


#152 - [BUG] Dans l'adminsite, les objets multilingues ne sont pas traduits en fonction de la langue de l'utilisateur
---------------------------------------------------------------------------------------------------------------------

Pas reproduit : 

* Se connecter à l'adminsite avec un utilisateur italien.

* Visualiser la liste des "Physical Types" par exemple. Elle contient les noms en français.

* Éditer un élément, renseigner le champ italien, sauvegarder.

* Visualiser la liste, le nom italien apparaît pour l'élément où la valeur est renseignée.


#143 - Ajouter des placeholders aux formulaire de filtres
---------------------------------------------------------

Plutôt que d'utiliser des labels, les champs des filtres affichent une valeur
qui disparait lors de la saisie. Cela permet d'économiser de l'espace à l'écran.


#132 - [BUG] Afficher clairement l'état échoué d'une couche de la carte
-----------------------------------------------------------------------

Si le chargement de la couche vectorielle échoue, alors la carte apparaît
en rouge, et un message est ajouté dans la console du navigateur.

#78 - Mesurer une distance sur la carte
---------------------------------------

* Aller sur une page comportant une carte.

* Cliquer sur l'icône montrant une règle.

* Cliquer sur la carte pour dessiner la distance à mesurer. La distance
  s'affiche dynamiquement.

* Désactiver l'outil de mesure en recliquant sur l'icône.


#168 - Champ traduction par défaut
----------------------------------

Pour les champs traduisibles, il y a, en plus de la colonne, autant de colonnes en base que de langues
déclarées dans les paramètres du projet.

Par exemple: description, description_fr, description_it, description_en

Lorsque l'utilisateur qui saisit est italien, c'est la valeur de ``description_it`` qui sera stockée
dans le champ ``description`` en base.


#51 - Attacher des fichiers à un objet
--------------------------------------

Je peux attacher des documents à n'importe quelle entité ou à un projet :

* Lors de la création d'une entité, l'ajout de document n'est pas possible

* La vue d'édition d'une entité contient un formulaire pour ajouter un nouveau document à la fois.
  À l'ajout valide d'un document, je suis redirigé sur la même page (page d'édition de l'entité).

* La vue d'édition d'une entité liste les documents liés existants et un bouton
  permettant de supprimer chaque document.
  Lors d'un clic sur un de ces boutons, une demande de confirmation de
  suppression m'est demandée qui poursuit ou annule l'action.
  Lors d'une suppression confirmée, je suis redirigé sur la même page (page
  d'édition de l'entité).

* La vue de détail d'une entité liste les documents liés et un lien
  permettant de télécharger chaque document.

* La modification d'un document est pour le moment impossible (il faut
  supprimer/recréer le document).


#54 - Créer automatiquement les vignettes des fichiers attachés de type photo
-----------------------------------------------------------------------------

Dans la liste des fichiers attachés, un aperçu est disponible pour tous les
fichiers attachés de type image.

Pour les autres, le nom de fichier est présenté avec un icône selon son type.


#112 - Tuiler les fonds PNE en L93
----------------------------------

* TileCache est servi par gunicorn/nginx

* Supervisor lance le process

* La conf Tilecache est construite automatiquement a partir des
  valeurs du settings.ini

* La conf des couches Django est construite automatiquement.



#178 - [BUG] Afficher tous les status lors de la création d'une intervention
----------------------------------------------------------------------------

Fixé.


#187 - [BUG] le champ NOM est vide, même si le tronçon a bien un nom
--------------------------------------------------------------------

Pas reproduit. 

Attention, le nom affiché dans la liste est construit à partir de la
clé primaire uniquement quand le nom est vide. En saisissant un nom, le champ
du formulaire fonctionne bien. 

#190 - [BUG] Lors de l’édition d’un tronçon, les valeurs choisies pour USAGES et RESEAUX ne sont pas enregistrées.
------------------------------------------------------------------------------------------------------------------

Fixé.


#164 - [BUG] Saisie topologie - les tronçons ne correspondent pas au trajet le plus court
-----------------------------------------------------------------------------------------

Corrigé.


#171 - [BUG] Saisie topologie - sélection multitronçon sur un même tronçon ne fonctionne que dans un sens
---------------------------------------------------------------------------------------------------------

Corrigé.


========================
Sprint 4 - Version 0.4.0
========================

#26 - Changer l'état publié d'un itinéraire
-------------------------------------------

* Le champ s'appelle désormais 'publié'.


#180 - Inverser l'ordre des champs désordres et type dans le formulaire
-----------------------------------------------------------------------

Fixé.


#184 - Conserver l'étendue de la carte recherche lors de l'ajout
----------------------------------------------------------------

Lorsque je suis sur une vue de liste d'entité et que j'ajoute une entité,
je souhaite que l'état de la carte (zoom, étendue) soit conservé entre ces deux vues.


#211 - Évenement type point : trigger modification
--------------------------------------------------

Ajouter un évènement de type point (un aménagement par exemple) à proximité
d'une intersection en s'assurant que le snapping relie bien l'évènement à
l'extrêmité d'un des tronçons.

Aller sur la fiche de détail de l'évènement ainsi créé. La liste des objets liés
doit montrer tout les tronçons partant ou arrivant à cette intersection.

#207 - Modifier un tronçon et déclencher les triggers
-----------------------------------------------------

Aller sur la page d'édition des tronçons et modifier la géométrie. Si la
nouvelle géométrie s'auto-intersecte, le formulaire doit indiquer une erreur lors
de la validation. S'il n'y a pas d'auto-intersection, le formulaire doit valider
normalement.

Après validation du formulaire, vous pouvez constater que les évènements ont été
mis à jour :

* Les évènements faisant le lien avec les couches SIG reflètent bien les
  relations actuelles entre le tronçon et les différentes entités des couches
  SIG.
* Les évènements linéaires associés ont vu leur géométrie mise à jour pour
  suivre la nouvelle géométrie du tronçon.
* Les évènements ponctuelles associés ont vu leurs PK début/fin et leur
  décallage mis à jour mais sont rester à la même position géographique.


#167 - Refactor de la relation "Topology kind"
----------------------------------------------

Pour simplifier énormément la gestion des types d'évènements, le type d'évènement 
est désormais une colonne texte. Idéalement, il aurait fallu un type ENUM, 
mais Django ne les gère pas facilement.

En utilisant une relation 1-N, cela compliquait l'accès à un type particulier, 
puisqu'une jointure était nécessaire pour éviter d'utiliser la clé primaire.


#186 - Rappeler sur quel aménagement ou signalétique on est en train d'ajouter une intervention.
------------------------------------------------------------------------------------------------

Désormais lors de la création ou l'édition d'une intervention sur un aménagement ou une 
signalétique, le nom est rappellé dans le titre du formulaire, avec un lien pour le consulter.


#182 - Ajouter une intervention depuis un tronçon
-------------------------------------------------

* Consulter la fiche d'un tronçon

* Cliquer sur "Ajouter une intervention"

* Le formulaire d'ajout d'intervention s'ouvre avec la carte placée sur le 
  tronçon précédemment consulté.

:notes: 

    Dans la mesure où l'utilisateur n'a pas encore choisi s'il allait créé
    un point ou une ligne, nous nous contentons de centrer la carte sur le
    tronçon.


#23 - Associer des thématiques aux itinéraires indépendamment des types des POI
-------------------------------------------------------------------------------

Il est désormais possible d'associer des thèmes aux itinéraires.

Ils sont gérés dans l'AdminSite.

#153 - [BUG] La carte n'est pas ajustée à la hauteur de l'écran
---------------------------------------------------------------

Afficher une page, la partie droite doit occuper toute la hauteur de la page
(pas de blanc en bas).

Redimmensionner la fenêtre du naviagteur, la partie droite doit toujours occuper
toute la hauteur de la page, tous les éléments de la partie droite restent
visibles et c'est l'élément carte qui est ajusté aux nouvelles dimensions.



#101 - Ajouter la notion de thème(s) majeur(s) pour les itinéraires
-------------------------------------------------------------------

Il est désormais possible d'associer des thèmes majeurs aux itinéaires.

La liste des choix proposés est réduite aux thèmes choisis dans l'itinéraire.

* Choisir des thèmes pour l'itinéraire

* La liste des choix des thèmes majeurs est réduite.

* Sélectionner un thème majeur.

* Ajouter des thèmes pour l'itinéraire, la liste des majeurs est raffraichie, 
  la sélection est conservée.

Dans la fiche détail, les thèmes majeurs sont décorés d'une étoile.


#53 - Ajouter des liens Web à un itinéraire
-------------------------------------------

Un bouton "ajouter" est désormais disponible sur la liste des choix des liens Web
dans le formulaire de création et d'édition des itinéraires.

Lors de l'ajout, une popup avec le formulaire s'ouvre. À la fermeture, le 
lien est automatiquement ajouté à la liste, et sélectionné.


#208 - Implémenter les filtres (story #82) pour chaque type d'évènement
-----------------------------------------------------------------------

* Tronçons
  - Type de réseau
  - Recherche sur le nom du tronçon (contient une partie de la saisie)
  - Recherche sur le commentaire (contient une partie de la saisie)
  - Liste déroulante des sentiers
* Interventions
  - Suivi
  - Type d'intervention
  - Année
  - Enjeu
* Chantier
  - Année (retourne les chantiers qui sont/étaient en cours pendant cette année)
* Signalétique
   - Type
   - Année de travaux (retourne les signalétiques dont au moins une intervention
     s'est déroulée pendant l'année saisie)
* Aménagement
   - Type
   - Année de travaux (retourne les signalétiques dont au moins une intervention
     s'est déroulée pendant l'année saisie)


#179 - Ajouter les infos comptables sur les interventions et chantiers
-----------------------------------------------------------------------

Il est désormais possible d'ajouter des hommes-jours aux interventions et
des financements aux chantiers.

* Créer une intervention, ne pas ajouter d'hommes-jours, sauvegarder. 
  L'intervention est créée sans erreur.

* Créer une intervention, ajouter des hommes-jours, sauvegarder. L'intervention
  est créée avec des hommes-jours.

* Éditer l'intervention, enlever les hommes-jours, sauvegarder. L'intervention
  n'a plus d'homme-jours.

* Éditer l'intervention, ajouter des hommes-jours, sauvegarder. L'intervention
  a bien les hommes-jours saisis.

Recommencer avec les financements sur les chantiers.


#210 - Ajouter les attributs nécessaires au portail rando dans la couche itinéraires geojson
--------------------------------------------------------------------------------------------

La liste des itinéraires est accessible à l'adresse :

http://geobi.makina-corpus.net/ecrins-sentiers/api/trek/trek.geojson

Bien qu'au format GeoJSON, la liste reste lisible, on peut y retrouver les
attributs permettant le filtrage ainsi que l'affichae tabulaire et
cartographique.

Note: suels les itinéraires avec le statut "publié" sont inclus dans
cette liste.


#212 - Supprimer un évènement et déclencher les triggers
--------------------------------------------------------

Lors de la suppression d'un évènement, seul son statut "supprimé" change. Les
informations associées continuent à lui être attachées et à être maintenues (mise à
jour de la géométrie en cas de modification des tronçon notamment).

Les interventions éventuellement liées à l'évènement sont supprimées en cascade,
c'est-à-dire que leur statut "supprimé" devient vrai.

Les évènements faisant le lien automatique entre tronçons et couches SIG sont
en revanche supprimés au niveau base de données.


#41 - Exporter la liste obtenue au format tableur (CSV)
-------------------------------------------------------

Sur la vue liste de chaque entité, je peux exporter la liste courante au format CSV.
Les colonnes présentes dans le CSV seront celles de la liste en cours.

#43 - Exporter l'itinéraire au format GPX
-----------------------------------------

Sur la vue de chaque entité, je peux exporter la liste courante au format GPX.
Un point seul (un évènement de type point) est ajouté comme un "Way Point".
Une liste de point (une ligne - évènement ou tronçon -) est ajouté comme une route.

Ne sont exportés au format GPX que les géométries (aucune autre donnée pour le moment).
Les géométries seront reprojetées en projection GPS (WGS 84).

Cas particulier:

* Un sentier est une union de tronçons: un sentier est ajouté comme une seule route
* Un projet correspond à un ensemble d'intervention, donc d'évènements:
  tous les évènements (ligne et point) sont fusionnés au sein d'une unique route

#42 - Exporter la liste obtenue au format Shape
-----------------------------------------------

Sur la vue de chaque entité, je peux exporter la liste courante au format shape.

Un fichier shape est composé de 4 fichiers différents (shp, shx, prj, dbf).
Il ne peut contenir qu'un seul type de géometrie, ainsi, un fichier shape
distinct sera créer par type de géométrie (point, ligne, ...).

Les géométries resteront dans leur projection initiale (epsg:2154 - lambert 93).

L'export entrainera la création et le téléchargement d'un zip comprenant
l'ensemble de ces fichiers.

Les données attributaires seront pour l'instant celles de la liste en cours.

Cas particulier:

* Un projet correspond à un ensemble d'intervention, donc d'évènements.
  Or, un évènement peut être un point ou une ligne, nous obtenons
  donc un projet qui peut être réparti sur des fichiers shapes différents.
  Les données attributaires d'un projet seront celle de la liste en cours
  ainsi qu'un élément (id, nom) permettant de distinguer l'intervention
  correspondant à la géometrie.


#50 - Exporter la fiche au format bureautique
---------------------------------------------

Il est désormais possible d'accéder à la version OpenDocument (OpenOffice) 
de la fiche.

Pour l'instant la fiche ne contient aucune information à part les dates d'insertion,
de modification et une image avec une carte centrée sur l'objet.

:notes:

    * il n'y a pas de mise en cache, et l'obtention de la carte en image est
      assez longue.

    * il faudra décliner la fiche pour chaque type d'objet, ou utiliser tout
      simplement les mêmes informations que ce qui est présenté dans la version
      Web.

    * pour les itinéraires, il faudra prévoir autant de versions que de langues,
      avec à chaque fois la distinction avec/sans POI.



========================
Sprint 5 - Version 0.5.0
========================

#209 - Exporter tous les attributs d'un itinéraire en JSON
----------------------------------------------------------

Les propriétés d'un itinéraire sont accessibles à l'adresse :

http://geobi.makina-corpus.net/ecrins-sentiers/api/trek/trek-<ID>.json

(Remplacez ``<ID>`` par l'identifiant de l'itinéraire désiré.

Note: seuls les itinéraires avec le statut "publié" sont consultable à cette
adresse.

#206 - Exporte le profil altimétrique d'un itinéraire en JSON
-------------------------------------------------------------

Le profile d'un itinéraire est accessible à l'adresse :

http://geobi.makina-corpus.net/ecrins-sentiers/api/trek/profile-<ID>.json

(Remplacez ``<ID>`` par l'identifiant de l'itinéraire souhaité).

Note: seuls les profiles des itinéraires avec le statut "publié" sont
consultable à cette adresse.

#251 - Ajouter/éditer/supprimer des éléments des couches SIG et déclencher les triggers
---------------------------------------------------------------------------------------

Lors de l'ajout, de la modification ou de la suppression d'un élément dans les
couches SIG (secteur, commune, zonage), les relations avec les tronçons sont
maintenues à jour.

On pourra plus facilement le vérifier avec PgAdmin.

#170 - Définir les couleurs de couche : tronçons et entité
----------------------------------------------------------

Sur toutes les cartes, les tronçons apparaissent d'une couleur et les autres objets métiers d'une autre couleur.

Ces couleurs sont paramétrables dans les settings Django.


#240 - Ajouter une intervention depuis un sentier
-------------------------------------------------

La fiche sentier affiche désormais la liste des interventions associées 
aux tronçons qui le composent.

Il est possible d'ajouter une intervention sur le sentier, le comportement
est similaire à l'ajout d'une intervention sur un tronçon : il s'agit juste
du centrage de la carte sur le sentier.

#35 - Supprimer un tronçon et déclencher les triggers
-----------------------------------------------------

Si un itinéraire emprunte le tronçon supprimé, il est dépublié.

Si un événement est composé de ce troncon uniquement, son statut supprimé
devient vrai.

#231 - Snapper sur les noeuds des tronçons (en plus des segments)
-----------------------------------------------------------------

Lors du déplacement des marqueurs, le snapping s'effectue sur les tronçons et
sur les points qui composent sa ligne brisée (extrémités et points intermédiaires).

#192 - Quand on est sur une fiche, reprendre le picto qui correspond au type d'objet pour bien identifier sur quel type d'objet je travaille.
---------------------------------------------------------------------------------------------------------------------------------------------

Le picto est désormais affiché dans l'ongle, la fiche et le formulaire.

#198 - Configuration des langues
--------------------------------

L'usage de différentes langues est bien paramétrable et non figé en nombre ?
............................................................................

Oui, il est possible de rajouter des langues. La procédure est la suivante :

1. Ajouter les langues dans ``settings.LANGUAGES``

2. Extraire les évolutions des modèles pour les applications faisaint usage des
   traductions ::

    bin/django schemamigration common --auto
    bin/django schemamigration trekking --auto
    bin/django schemamigration land --auto

3. Mettre à jour la base de données ::

    bin/django syncdb --noinput --migrate

Vérifier que les champs des formulaires sont bien automatiquement ajoutés
.........................................................................

Lorsqu'un champs traduit est insérée dans un formulaire, il est automatiquement
répliqué autant de fois qu'il y a de langues définie dans
``settings.LANGUAGES``.

On peut le constater en affichant le formulaire d'édition des itinéraires après
avec rajouté une langue (voir ci-dessus).

#185 - Ajouter une option ZOOMER SUR L'OBJET depuis la liste
------------------------------------------------------------

En double-cliquant sur une ligne de la liste, la carte se centre sur l'objet.

Cela fonctionne aussi pour des points.

:notes:

    Afin de rester cohérent avec le comportement actuel, la liste se restreint
    alors aux objets affichés sur la carte. 
    Dans la mesure où cette fonctionnalité pourrait s'avérer pertubante, puisqu'elle
    vide la liste, nous avons décidé de ne pas l'exposer aux utilisateurs avec un bouton.


#269 - Gérer l'ajout de nouveaux settings lors de l'upgrade
-----------------------------------------------------------

En lançant le process ``./install.sh`` les settings du fichier ``etc/settings.ini`` sera
complété avec toutes les valeurs par défaut des paramètres apparus depuis le dernier
déploiement.

#49 - Exporter la fiche au format PDF
-------------------------------------

Il est désormais possible d'obtenir la version PDF de la fiche d'un objet.

#236 - Envoyer un mail aux admins sur exception (internal error)
----------------------------------------------------------------

Configurer l'envoi d'email dans le fichier ``etc/settings.ini`` et un mail sera
envoyé à chaque erreur interne.

Pour tester, arrêter le service postgresql par exemple.


#250 - Topologie : calcul en JS d'un lat/lng d'un point sur un tronçon à partir de debut/fin
--------------------------------------------------------------------------------------------

Partie purement technique.

#249 - Topologie : dé/sérialization des contraintes de point de passage
-----------------------------------------------------------------------

Partie purement technique.

#248 - Calcul du plus court chemin : prendre en compte la position du point sur le tronçon
------------------------------------------------------------------------------------------

Sur la page d'ajout d'une intervention, lors d'une saisie multitronçons, le calcul
du plus court chemin prend en compte la position du point sur le tronçon
(et non pas une des deux extrémités du tronçon comme point).
Le tronçon original est séparé par le point en deux autres tronçons 'virtuels'
dont le poids est réparti proportionnellement à leur longueur.


#134 - Ajouter des points de passage forcés à la saisie multitronçons
---------------------------------------------------------------------

Ajout de passage forcés 'à la Google Maps' :

- Au survol de l'itinéraire calculé, un marqueur intermédiaire apparait
- Le démarrage d'une action de drag sur ce marqueur l'ajoute comme une contrainte intermédiaire
- Lors du drag sur un marqueur intermédiaire, le marqueur se "snappe" au réseau existant et l'itinéraire
  le plus court est recalculé à la volée
- Un clic sur le marqueur intermédiare, supprime le marqueur et la contrainte
- La sauvegarde ainsi que l'édition d'un itinéraire possédant de telles contraintes fonctionne.



#205 - Liste des POI d'un itinéraire au format GeoJSON
------------------------------------------------------

Pour un itinéraire, la liste de ses POIs est disponible à l'adresse 
``http://server/api/trek/<id>/pois.geojson``. 

Cela servira au portail rando, pour afficher les POIs sur la fiche détail d'un itinéraire.


#224 - Afficher les couches des secteurs et communes
----------------------------------------------------

Dans le sélecteur de couches, il est désormais possible d'afficher les secteurs
et les communes. L'état affiché/caché de chaque couche est conservé d'une session à l'autre.

#66 - Exporter l'itinéraire au format GPX
-----------------------------------------

Pour un itinéraire, sa trace GPX est disponible à l'adresse 
``http://server/api/trek/trek-<id>.gpx``. 



#79 - Authentification sur table/vue externe
--------------------------------------------

Lors de l'exécution de ``./install.sh``, des nouveaux paramètres vont
être ajoutés au fichier de configuration ``etc/settings.ini``. Pour avoir
leur description, reportez vous au nouveau fichier d'exemple situé dans *caminae/conf/settings.ini.sample*.

Un paragraphe a également été ajouté au README décrivant la structure de la
table/vue attendue.

Si le paramètre ``authent_dbname`` est non vide, l'identification des utilisateurs
se fait à travers la table externe. Les autres paramètres (``authent_XXX``) deviennent alors
obligatoires.

* Activer l'authent en configurant le fichier de settings.
* Vérifier que le login fonctionne (password en md5 dans la vue, cf. README)
* Vérifier que la gestion des utilisateurs est bien désactivée dans l'admin.
* Vérifier que l'utilisateur a bien les droits adéquats en fonction de la colonne *level*
* Vérifier que les droits sont bien raffraichis à chaque déconnexion-reconnexion
* Vérifier qu'un changement de password dans la table fait bien échouer le login

#228- Gestion des utilisateurs
------------------------------

Pour désactiver l'identification des utilisateurs sur une table distante. Enlever
la valeur de ``authent_dbname`` et exécuter ``make deploy``.


#243 - [BUG] Le CSV contient de l'html pour les noms
----------------------------------------------------

Corrigé.

#242 - [BUG] Le CSV n'a pas de headers
--------------------------------------

Corrigé.

Le header du CSV est créé à partir du nom des colonnes, i.e.:
ils seront identiques aux headers du tableau dans la vue liste de chaque entité.


#238 - Afficher les liens vers les objects liés plutot que oui/non
------------------------------------------------------------------

Détail projet: ajout d'un lien vers intervention
Détail intervention: ajout de lien sur projet, infrastructure et signage


#55 - Exporter la carte assemblée au format image
-------------------------------------------------

Cliquer sur le bouton "Screenshot". Une image est proposée au téléchargement,
le nom de fichier contient la date. L'image respecte la position de la carte
et les couches affichées.

Déplacer la carte, décocher des couches, observer que l'image exportée est correcte.

:notes:

    Problèmes connus:
    
    * les objects vectoriels sont décalés sur l'image.
    * l'obtention de l'image est longue, cela est dû au cache qui n'est pas actif pour l'impression.


#241 - Filtres sur foncier
--------------------------

Je peux filtrer de nombreuses entités en fonction de filtre de type foncier.

Types de filtre:

    * Organisme compétent
    * Organisme en charge de la gestion signalétique
    * Organisme en charge de la gestion travaux

Entités pouvant être filtrées:

    * Tronçon
    * Intervention
    * Projet
    * Itinéraire
    * POI
    * Signage
    * Infrastructure

:notes:

    Problème connu : Les performances sont catastrophiques à cause d'un problème sur notre algorithme.


#225 - Minimiser l'espace occupé par les filtres
------------------------------------------------

*Travail en cours*

Un essai de pop-up a été tenté pour confiner les filtres dans un panneau.
Si celui-ci ne s'avère pas concluant, nous utiliserons un panneau pliable.

:notes: 

    Problème connu : la popup ne s'affiche pas en face du bouton.
    
    Le bouton de filtre devrait changer de couleur quand un filtre est appliqué.
    
    Les champs de filtres ne sont pas bien disposés à l'intérieur.


========================
Sprint 6 - Version 0.6.0
========================

#280 - Nombre de jour/agent - Décimales
---------------------------------------

Il est désormais possible de saisir des chiffres avec décimales dans le 
champ nombre d'homme-jours des interventions.

#203 - Champs a ajouter
-----------------------

* Tronçons: Départ + Arrivée (défaut: vide)

* Tronçons: Niveau de confort, liste éditable dans l'Admin.

* Chantiers: Type, liste éditable dans l'Admin.

* Chantiers: Domaine, liste éditable dans l'Admin.

* Fonctions: Coût jour, éditable dans l'Admin pour chaque fonction.
  Le coût total affiche dans la fiche détail d'une intervention utilise ce facteur.


#266 - Date de l'intervention
-----------------------------

Étiquette du champ du formulaire changée.


#281 - Fiche tronçon / Commentaire
----------------------------------

Le commentaire n'est plus écrit en HTML complet sur les fiches tronçons
et sentiers.

:notes:

    Les autres fiches n'affichent pas encore tous les champs (attente specs. Écrins)
    donc ne sont pas (encore) concernées.


#318 - [BUG] AMENAGEMENT - La carte ne se charge pas completement et tourne sans arrêt
--------------------------------------------------------------------------------------

Fixé.

#285 - Saisie des champs textes multilingues
--------------------------------------------

Dans la story #168 il est indiqué que si l'utilisateur logué est italien, 
c'est le champ texte italien qui est stocké. Cela veut dire qu'il ne peut pas saisir la description française ?

    Si évidemment. Il s'agissait juste de la colonne 'description' en base, 
    qui n'est pas utilisée dans l'application. On utilise les colonnes 
    traduites (_fr, _en, _it).


#191 - [BUG] On ne voit pas bien quand on a sélectionné l’outil DESSIN.
-----------------------------------------------------------------------

Désormais l'outil sélectionné s'illumine.


#327 - [BUG] ENJEU - Calcul automatique de l'enjeu des interventions.
---------------------------------------------------------------------

L'enjeu d'une intervention est bel et calculé si au moins un des tronçons
a un enjeu.


#67 - Exporter l'itinéraire au format KML
-----------------------------------------

Les itinéraires sont désormais exportables en KML. Des liens sont disponibles
depuis la fiche détail. 

Le KML contient la ligne de l'itinéraire et les POIs.


#276 - Attribut districts (liste de pk des secteurs) dans le détail JSON itinéraire
-----------------------------------------------------------------------------------

Le JSON des itinéraires contient désormais la liste des secteurs traversés (pk + nom)


#312 - Publier certains settings de l'admin en JSON pour portail rando
----------------------------------------------------------------------

Certains settings, accessibles sur ``api/settings.json`` serviront au portail de l'offre randonnée.


#338 - [BUG] Extent de la carte perdu au changement de type d'objet dans la recherche
-------------------------------------------------------------------------------------

Fixé.


#29 - Paramétrer le logo de l'application
-----------------------------------------

Pour l'instant, seuls deux logos sont définis : 

* ``logo-login.png`` : affiché sur la page de connexion

* ``logo-header.png`` : affiché dans la barre d'outils de l'application

Leur emplacement est ``var/media/upload/`` dans l'arborescence du projet.


#305 - Fichiers liés / Nouvel onglet
------------------------------------

Les fichiers liés s'ouvrent dans un nouvelle fenêtre/onglet.


#310 - [BUG] Synchroniser listes déroulantes "Centrer sur ..."
--------------------------------------------------------------

Elles sont désormais exclusives : le choix sur une désactive les autres.


#290 - [BUG] DROITS lecture
---------------------------

Il ne s'agissait pas d'un bug des droits, mais d'une erreur de configuration
au niveau du déploiement.


#320 - Nom de la couche sentiers
--------------------------------

Fixé

#343 - [BUG] (Javascript) Edition trek : drag point intermédiaire sans activer outil multipath
----------------------------------------------------------------------------------------------

Corrigé.
Nouveau comportement:

- Le multipath doit être désactivé manuellement en cliquant sur le contrôle multipath où le contrôle point.
  (elle était désactivée de façon buggée à la suite du calcul d'une nouvelle topologie multipath).
- La désactivation du multipath entraîne la suppression des évènements drag, click etc. sur la topologie multipath.
- L'activation d'un multipath n'entraîne plus la suppression de la topologie multipath existante si elle existe.
  Elle réintroduit les évènements drag, click, etc. rendant la topologie modifiable
- Le multipath est activé automatiquement lors de l'ouverture de la vue d'édition d'une topologie multipath


#378 - [BUG] Fiche détail signalétique : les tronçons ne sont uniques dans la liste
-----------------------------------------------------------------------------------

Fixé.

#288 - [BUG] Saisie topologie point : mauvaise geométrie calculée
-----------------------------------------------------------------

Fixé, avec le #378.

Je créé un élément de signalétique sur un tronçon, proche d'un croisement. 
Une fois enregistré, celui-ci est désormais bien positionné au bon endroit.


#372 - [BUG] Impression : choix zones visibles sur l'image exportée
-------------------------------------------------------------------

Les listes déroulantes ne sont plus visibles sur l'image exportée.


#230 - [BUG] Déploiement écrins : saisie marqueur, image manquante
------------------------------------------------------------------

Fixé.


#374 - [BUG] Impression : parfois certaines tuiles ne sont pas chargées complètement
------------------------------------------------------------------------------------

Fixé.

========================
Sprint 7 - Version 0.7.0
========================


#335, #328 - [BUG] Evenement linéaire différent en édition.
-----------------------------------------------------------

Le problème était lié au trigger qui calcule la géométrie résultante, lorsque
des marqueurs intermédiaires étaient placés, ainsi qu'au composant d'édition de topologies, 
qui ignorait les marqueurs intermédiaires lorsque ceux-ci étaient placés à des intersections (début ou fin à 0.0 ou 1.0).

* Vérifier que les géométries des saisies multi-tronçons sans marqueurs sont bien calculées
  et sont bien restaurées en édition.

* Vérifier que les saisies avec marqueurs intermédiaires sont bien calculées
  et restaurées.

* Vérifier que les saisies avec marqueurs sur intersections sont bien calculées 
  et restaurées.


#379 - [BUG] Édition topologie point à un croisement : mauvais marqueur utilisé pour l'edition
----------------------------------------------------------------------------------------------

Fixé.


#375 - [BUG] (Javascript) Ajouter une signalétique, la carte ne s'affiche pas
-----------------------------------------------------------------------------

* Vider le cache du navigateur (localstorage inclus)

* Accéder au formulaire d'ajout directement (ex: ``path/add/`` ou ``signage/add/``)

* La carte s'affiche bien sur la zone globale du parc


Pour vérifier que le comportement est conservé :

* Retourner sur la vue liste, zoomer, aller sur ajout : la carte est positionnée sur la zone

* Éditer un objet existant, vérifier que la carte est positionnée sur l'objet


#314 - [BUG] Itinéraires - affichage sur la carte
-------------------------------------------------

Fixé.


#329 - [BUG] (Javascript) Edition Topology : ajout d'un point n'efface pas le précédent
---------------------------------------------------------------------------------------

Sur un formulaire d'ajout (ex: signalétique)

* Ajouter un point

* Ajouter un autre point : le premier point est effacé. Le second est ajouté.

* Ajouter un point;

* Ajouter une topologie ligne : le point précédent est effacé, la ligne est ajoutée.

* Ajouter un point : la topologie ligne précédente est effacée.


Sur un formulaire d'édition :

* Si l'objet est un point, le marqueur est déplaçable au chargement de la page

* Si l'objet est un chemin, les marqueurs sont déplaçables, l'outil topologie est activé.

* Le fonctionnement du formulaire d'ajout s'applique.


#340 - Topologies : Sélectionner l'outil multipath devrait désactiver l'outil point
-----------------------------------------------------------------------------------

Désormais il n'est plus possible d'activer l'outil point lorsque l'on est
en train de saisir une ligne multi-tronçons.


#341 - [BUG] Edition trek : Cannot read property '_leaflet_mousedown1' 
----------------------------------------------------------------------

Erreur liée au marqueur du champ parking, désormais fixée. Le marqueur de parking
est bien restauré en édition.


#279, #331 - Découpage de tronçons et association des évènements
----------------------------------------------------------------

Voici la liste des cas qui sont gérés et testés.
Les cas qui ne sont pas supportés sont explicités plus bas.

::

               C
        A +----+----+ B
               |
               +      AB exists. Add CD.
               D      or CD exists and add AB.

               C
               +
               |
        A +----+----+ B
               |
               +      AB exists. Add CD.
               D      

             C   D
             +   +
             |   |
        A +--+---+--+ B
             |   |
             +---+ 


             C   E   G   I
             +   +   +   +
             |   |   |   |
        A +--+---+----------+ B
             |   |   |   |
             +   +   +   +
             D   F   H   J

                                       + E
                                       :
        A +----+----+ B         A +----+----+ B
                                       :
        C +----+ D              C +----+ D
        
                                    AB and CD exist.
                                    CD updated into CE.


Avec des évènements linéaires sur les tronçons :

::

                 C
        A +---===+===---+ B
             A'  |  B'
                 +      AB exists with topology A'B'.
                 D      Add CD.
                 
                     C
        A +---+---=====--+ B
              |   A'  B'
              +           AB exists with topology A'B'.
              D           Add CD          
                 

                    C
        A +--=====--+---+ B
             A'  B' |   
                    +    AB exists with topology A'B'.
                    D    Add CD

                B   C   E
        A +--===+===+===+===--+ F
                    |   
                    +    AB, BE, EF exist.
                    D    Add CD.

             C   D
             +   +
             |   |
      A +--==+===+==--+ B
             |   |
             +---+ 


Et lors de la mise à jour :

::

                                          + E
                                          :
                                         ||
        A +-----------+ B         A +----++---+ B
                                         ||
        C +-====-+ D              C +--===+ D
             
                                          + E
                                          :
                                          :
        A +-----------+ B         A +-----+---+ B
                                          :
        C +-==------+ D           C +--===+ D

                                           + E
                                          ||
                                          ||
        A +-----------+ B         A +-----+---+ B
                                          :
        C +------==-+ D           C +-----+ D


Avec des évènements ponctuels :

::

                C
        A +-----X----+ B
                |   
                +    AB exists with topology at C.
                D    Add CD.
                C
    
        A +--X--+----+ B
                |   
                +    AB exists.
                D    Add CD.
                C
    
        A +-----+--X--+ B
                |   
                +    AB exists.
                D    Add CD.
                C
    
        A X-----+----+ B
                |   
                +    AB exists.
                D    Add CD.
    
                C
        A +-----+----X B
                |   
                +    AB exists.
                D    Add CD.
    

Et lors de la mise à jour :

::

                                      + E
                                      :
                                      :
    A +-----------+ B         A +-----+---+ B
                                      :
    C +-X-----+ D              C +--X-+ D
    
                                      + E
                                      X
                                      :
    A +-----------+ B         A +-----+---+ B
                                      :
    C +-----X-+ D              C +----+ D

                                      + E
                                      :
                                      :
    A +-----------+ B         A +-----+---+ B
                                      :
    C X-------+ D              C X----+ D

                                      X E
                                      :
                                      :
    A +-----------+ B         A +-----+---+ B
                                      :
    C +-------X D              C +----+ D


Les cas suivants sont mal supportés :

::
    
    BUG: AF segment not associated to X
    
                                      + E
                                      :
                                     F:
    A +-----------+ B         A +-----X---+ B
                                      :
    C +---X---+ D              C +----+ D
    
    
    BUG: AD,DB segment not associated to X
    
                                      D
    A +-----------+ B         A +-----X---+ B
                                      :
    C +-------X D                     :
                                      +
                                      C
                
    BUG: AC,CB segment not associated to X
          
                                      C
    A +-----------+ B         A +-----X---+ B
                                      :
    C X-------+ D                     :
                                      + D
    
    
    BUG: AB, EF, CD are split into 3 parts instead of 5.
    
               C              D
               +            +
             E  \          /  F
        A +---+--+--------+--+---+ B
               \  \      /  /   AB exists. Create EF. Create CD.
                \  \    /  /
                 +--+--+--+ 
                     \/


Le cas suivant n'est pas géré volontairement :

::

    AB et CD se superposent. Seuls les intersections ponctuelles sont gérées.
    
    C +---+
          |      
    A +---+---+---+ B
              |      
              +---+ D



========================
Sprint 8 - Version 0.8.0
========================

#323, #289 - Affichage des informations SIG dans les fiches objet
-----------------------------------------------------------------

Tous les objets ont désormais une section "Foncier" qui liste les propriétés liées
aux couches SIG, ainsi qu'au module foncier.

Les couches du module foncier (nature, status, protection) seront implémentées
avec la story #386.

#334 - Type foncier
-------------------

* Créer un objet de type foncier

* Retourner sur la recherche, il apparait dans la liste, et sur la carte

* Cliquer sur son nom, puis sur Éditer

* Modifier la géométrie ou les attributs, retourner sur la liste, vérifier que
  tout s'est bien mis à jour.

#357 - BUG - ADMIN - Perte des résultats de la recherche
--------------------------------------------------------

Fixé.

#194 - Fixer certains labels
----------------------------

Fixé.

#221 - [BUG] Parking perdu (marqueur) si erreur de saisie formulaire itinéraire
-------------------------------------------------------------------------------

Fixé.


#309 - Préparer les fichiers de traduction pour le PNAM
-------------------------------------------------------

Les fichiers de traduction des différents modules du projet ont été fusionnés 
un un seul, grâce à la commande ``msgcat``. 

::

    msgcat caminae/*/locale/fr/LC_MESSAGES/django.po > caminae-fr.po

#254 - Gérer les langues depuis settings.ini
--------------------------------------------

Désormais, il est possible de configurer les langues du projet depuis le
fichier de configuration ``settings.ini``.

Voici les valeurs dans le fichier d'exemple :

::

    # Default language and list of available
    language = fr
    languages = en,fr,it

#316 - Modifier le terme TERRAIN par SCAN
-----------------------------------------

Fait.


#368 - Raffraichir la carte quand on fait un recherche dans la liste
--------------------------------------------------------------------

* Afficher la liste
* Taper un mot-clé, la liste se filtre, la carte aussi.
* Effacer le mot-clé, la liste s'affiche entièrement, les objets réapparaissent sur la carte


#315, #356, #225 - Filtres de liste
-----------------------------------

* Afficher la liste
* Cliquer sur le bouton de *Filtre*. Le panneau s'affiche sous le bouton.
* Remplir un champ, celui-ci apparaît en gras, son label apparait en infobulle.
* Valider le formulaire, la liste est filtrée, la carte aussi. Le bouton *Filtre* change de couleur.
* Cliquer sur le bouton *Filtre*. Le panneau se ferme.

* Survoler le bouton *Filtre*. Un encart apparait avec un récapitualitif des filtres appliqués.

* Raffraîchir la page ou naviguer dans l'application, pour constater que les filtres sont conservés.
  Le bouton *Filtre* est restauré dans l'état "actif".

* Ouvrir le panneau de filtre, réinitializer le formulaire. La carte et la liste sont
  raffraichis, le bouton *Filtre* reprend son état inactif.


#295 - Sentiers, itinéraire et tronçons / Départ et arrivée
-----------------------------------------------------------

Pour les objets dont la géometrie est de type Ligne, des marqueurs départ
et arrivée sont placés aux extrémités.


========================
Sprint 9 - Version 0.9.0
========================


#313 - Retrait de la notion de thématiques majeures
---------------------------------------------------

Le formulaire ne contient plus le champ, la base non plus.

#396 - [BUG] Formulaire POI : controle marqueur cassé
-----------------------------------------------------

Fixé.

#244, #400 - [BUG] À la première visite la carte est vide
---------------------------------------------------------

Fixé.


==========================
Sprint 10 - Version 0.10.0
==========================


#353, #347, #399 - Champs offre rando
-------------------------------------

* Champs *Transfontalier*, *Destination* supprimés.

* Champ *Accès* ajouté (traduisible).

* Champ *Pictogramme* ajouté aux usages.

* Champ aperçu supprimé sur lien supprimé.

* Bibliothèque de catégories de liens avec picto ajoutée.

#393 - [BUG] Les itinéraires non publiés n'apparaissent pas sur la carte recherche
----------------------------------------------------------------------------------

Fixé.

#388 - [BUG] kml / gpx ne sont pas accessibles si itinéraire n'est pas publié
-----------------------------------------------------------------------------

Fixé.

#390 - [BUG] Formulaire itinéraire - champs obligatoires
--------------------------------------------------------

Ne sont désormais obligatoires que les champs suivants :

* Nom dans la langue par défaut
* Topologie (trajet)

#387 - Améliorer formulaire itinéraire
--------------------------------------

La carte de saisie parking s'ajuste à la position de la carte de saisie itinéraire (à terme, il serait évidemment
préferrable de n'avoir qu'une seule carte).

Si une erreur de saisie survient sur l'onglet "Avancé", alors l'onglet s'affiche en rouge et s'active par défaut.

#385 - Découpage de tronçons - superposition
--------------------------------------------

Si lors de la saisie du tronçon, une partie est superposée avec un tronçon existant, une erreur est levée et le
champ carte du formulaire est marqué invalide.


#337 - OFFRE RANDO - Filtres sliders
------------------------------------

On peut modifier les valeurs minimum et maximum, et mettre les deux sur le même cran.

#61 - OFFRE RANDO - Accéder aux fiches randonnées via une URL (permalink)
-------------------------------------------------------------------------

Chaque fiche a sa propre URL, bien que la navigation s'effectue en Ajax sur les navigateurs modernes.

#73 - OFFRE RANDO - Présenter la liste des POI d'un itinéraire
--------------------------------------------------------------

Sur la fiche détaillée, les itinéraires s'affichent sous forme d'accordéon.

#74 - OFFRE RANDO - Sélectionner un POI dans la liste ou sur la carte pour afficher sa description
--------------------------------------------------------------------------------------------------

Au survol d'un POI sur la carte, sa description s'affiche (accordéon ouvert).

À l'ouverture de la description d'un POI, le marqueur s'anime sur la carte pour le répérer.

#76 - OFFRE RANDO - Paramétrer étendue géographique
---------------------------------------------------

L'étendue géographique du portail public est obtenue automatiquement à partir de la configuration de l'admin sentiers.

#72 - OFFRE RANDO - Afficher le profil altimetrique de l'itinéraire
-------------------------------------------------------------------

Le profil altimétrique (basique) s'affiche sur la fiche détail d'un itinéraire.

#70 - OFFRE RANDO - Afficher l'ensemble des itinéraires sur la carte d'accueil
------------------------------------------------------------------------------

L'ensemble des itinéraires publiés sur l'admin sentiers s'affiche sur la page d'accueil, dans la liste et sur la carte.

#345 - OFFRE RANDO - Itineraire dans le coeur
---------------------------------------------

Si l'itinéraire est dans le coeur, un encart d'avertissement s'affiche sur la fiche de l'itinéraire, et présente un lien vers la réglementation.

:notes:

    Attention! Le lien pointe la première des pages statiques. Il faut que la réglementation soit la première !


#75 - OFFRE de RANDO - Filtrer les itinéraires
----------------------------------------------

Par défaut, tous les itinéraires sont affichés.

Lors du filtrage, les itinéraires disparaissent de la liste. Ils disparaitront de la carte avec la story #405.

Pour les thèmes et les usages, si aucun n'est sélectionné, le critère est ignoré.

#367 - OFFRE de RANDO - Recherche par mot-clé
---------------------------------------------

La recherche textuelle s'effectue dans les champs suivants : 

* Nom
* Chapeau
* Descriptif
* Ambiance
* Depart
* Arrivee
* Accès
* Recommandation
* Nom Pois
* Commentaire des Pois
* Type des Pois
* Secteur
* Commune

Elle est insensible à la casse. Si plusieurs termes sont saisis, il faut que l'itinéraire réponde à au moins un terme pour s'afficher.


#405 - OFFRE de RANDO - Filtrer les objets de la carte
------------------------------------------------------

Fait.


#71 - OFFRE RANDO - Filtrer la liste en fonction de l'étendue de la carte
-------------------------------------------------------------------------

Fait.

#403 - OFFRE RANDO - Filtres par commune
----------------------------------------

Fait.

#410 - OFFRE RANDO - Popup carte
--------------------------------

Première implémentation effectuée.

#420 - [BUG] Supprimer un troncon ne fonctionne pas
---------------------------------------------------

Le dernier objet modifié sert de date de cache. 

En attendant que les tronçons soient gérés avec la colonne ``supprimé``, lors de la suppression, le dernier objet modifié est mis à jour pour forcer la mise à jour du cache.

#422 - Limiter le nombre de point du profil altimétrique (échantillonage)
-------------------------------------------------------------------------

Sur les itinéraires très longs, le profile altimétrique était très volumineux (une valeur par segment de la lignestring).
Désormais, un profil altimétrique a au plus 100 valeurs (paramètre ``PROFILE_MAXSIZE``).


#391 - [BUG] Étendue carte recherche après consultation de la fiche
-------------------------------------------------------------------

Le comportement est corrigé.

* Faire un aller-retour sur les pages liste / détail.
* Vérifier que l'emprise de la liste est conservée.
* Ajouter un tronçon depuis la vue liste, vérifier que c'est l'emprise de la liste qui est utilisée.
* Renseigner l'organisme compétent (ou ajouter une intervention) depuis la fiche détail d'un tronçon, vérifier que c'est l'emprise de la fiche détial qui est utilisée.




==========================
Sprint 11 - Version 0.11.0
==========================

#444 - Internal Server Error: /ecrins-sentiers/trek/add/
--------------------------------------------------------

Fixé.

#398, #402, #421, #442 - Internal Server Error sur le filtrage
--------------------------------------------------------------

Fixé.

#443 - Internal Server Error: /ecrins-sentiers/document/landedge-956752.odt
---------------------------------------------------------------------------

Problème de déploiement.

#458 - Vignettes itinéraires
-----------------------------

Les vignettes nécessaires au portail rando sont créées automatiquement. Actuellement, l'illustration d'un itinéraire est construite à partir de la première image trouvée dans les fichiers attachés à l'itinéraire.

:note:

    Celles-ci ne sont pas encore utilisé côté portail rando.


#441 - Données initiales (minimal, basic, example)
--------------------------------------------------

Il est possible de charger des données dans l'application, avec la commande suivante :

::

    make load_data

Désormais cette commande ne charge plus les données d'exemple du Parc des Écrins. Pour celles-ci, il faut désormais utiliser :

::

    bin/django loaddata development-pne

:note:

    Le réseau de tronçons d'exemple du PNE peut éventuellement échouer à cause des clés primaires dupliquées. **En attendant une mise à jour de celui-ci**, il faut désactiver au préalable le trigger de découpage des tronçons (``ALTER TABLE troncons DISABLE TRIGGER troncons_split_geom_iu_tgr;``). On peut ensuite charger le réseau, réactiver le trigger, et le déclencher sur chaque objet (``UPDATE troncons SET geom = geom;``).


#456 - [BUG] Positionnement des POIs après sauvegarde
-----------------------------------------------------

Désormais, les geométries des événement de type point ne sont pas recalculées à partir des décallages et pk, si le décalage est supérieur à 0.

De cette manière, la géométrie des objets qui est enregistrée est celle qui est saisie.

Dans le cas du snapping, le décallage est à 0, l'évènement évolue avec le tronçon.


#447, #394, #418 - [BUG] Forcer le raffraichissement de la carte après ajout/modification/suppression
-----------------------------------------------------------------------------------------------------

Les couches des objets ne sont plus mises en cache côté client sur la page liste et lors de la saisie d'une topologie.

Elle est en cache côté serveur en fonction de la colonne date_update.

:note:

    Initialement, le comportement était basé sur les entêtes HTTP ``Last-Modified``. Désormais, dans certains cas, nous forçons le raffraichissement du cache du navigateur à l'aide un paramètre GET ``?_u=<timestamp>``.


#423 - [BUG] Défilement liste des interventions
-----------------------------------------------

Désormais les lignes du tableau sur sur un ligne de texte.

#115 - Respecter les noms de tables et de champs en fonction du MLR
-------------------------------------------------------------------

Fait.


#302 - PK début / fin - affichage
---------------------------------

Les pk début et fin sont affichés sur les listes de tronçons.

Si le premier tronçon n'est pas couvert complètement, alors sera affiché le point de départ en mètres (ainsi que les pk au survol). De même pour le dernier.

Si le décallage est différent de zéro, il est affiché aussi pour l'ensemble des tronçons.

Pour les évènements ponctuels, une seule valeur est affichée.


#377 - Liste des tronçons sur intervention
------------------------------------------

La liste des tronçons s'affiche en colonnes.

::

    4 5 6 7
    0 1 2 3


#364 - ADMIN - Liste des fichiers liés
--------------------------------------

Les fichiers liés sont triés par date d'ajout (décroissant).


#431 - Sélecteur d'emprise : trier par ordre alphanum
-----------------------------------------------------

Les valeurs dans les sélecteurs d'emprise sont désormais triés par ordre alphanumérique.


#344 - [BUG] Edition trek : la topologie existante perd en précision (=décalage) après chargement
-------------------------------------------------------------------------------------------------

Le snapping ne s'active plus tout seul au chargement de la topologie.


#463 - [BUG] Saisie d'une topologie linéraire
---------------------------------------------

Certains problèmes persistent, notammé liés au bug #457. Mais la plupart des situations ont été fixées.

#461 - [BUG] Saisie d'une topologie circulaire
----------------------------------------------

Fixé. Elle n'apparait plus comme non valide.

#418 - [BUG] Ajout de tronçon - apparait en double
--------------------------------------------------

Pas reproduit. Remis au backlog.

#481 - ITINERAIRE - Remonter le champ booléen EN CŒUR DE PARC en haut de page sous le champs PUBLIE.
----------------------------------------------------------------------------------------------------

Fait.

#468 - Intégrer la couche ZONES REGLEMENTAIRES fournie par le PNE
-----------------------------------------------------------------

Fait.

#273 - Terminologie INTERVENTIONS Status
----------------------------------------

Désormais "Statut". 

#466 - [INTERROGATION] Découpage tronçon et attributs.
------------------------------------------------------

Les attributs sont dupliqués/conservés.

#454 - FICHIERS LIES - auteur
-----------------------------

L'auteur par défaut est le nom d'utilisateur, mais il est possible de le changer.

#350 - OFFRE DE RANDO - Titre de l'application
----------------------------------------------

Voir fichier de configuration d'exemple.

#469 - OFFRE RANDO - Templates 404 et 500
-----------------------------------------

Pages basiques. Des photos d'avalanches, d'hélicopters seraient sympas :)

#407 - OFFRE RANDO - Enlever filtre accessibilité
-------------------------------------------------

Fait.

#479 - OFFRE de RANDO - Filtres secteurs et communes
----------------------------------------------------

Nous utilisons désormais des listes avec complétion.


[BUG] - Intervention sur infrastructure
---------------------------------------

Fixé.

#429 - [BUG] Les chantiers disparaissent quand on les associe à une intervention
--------------------------------------------------------------------------------

Fixé.

#464 - [BUG] Erreur interne - export list treks Shapefile
---------------------------------------------------------

Fixé.

#457 - [BUG] Positionnement sur tronçon inversé (début/fin)
-----------------------------------------------------------

Fixé.