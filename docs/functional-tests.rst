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
