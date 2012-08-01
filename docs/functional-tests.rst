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

#18 - Gérer les permissions d'édition des objets en fonction de la structure
----------------------------------------------------------------------------

* Se logger avec un utilisateur du groupe *Référant sentiers* de la structure PNE.
* Vérifier que l'édition des tronçons est accessible.
* Changer la structure d'un tronçon.
* Vérifier qu'il n'est plus possible d'accéder au formulaire d'édition avec ce même utilisateur.


#36 - Charger la liste des tronçons en asynchrone
=================================================

* Ouvrir la page des tronçons, la liste est vide pendant une fraction de secondes.
* Vérifier que la liste se charge correctement en asynchrone. Par exemple
  avec l'inspecteur Firebug, vérifier que les données JSON sont reçues et la 
  liste est raffraichie.

:notes:

    L'implémentation est validée pour la liste des tronçons (environ 2000 objets)
    et sera appliquée aux autres modules.


:bonus sur cette story, sinon recréer une autre:

    * Si la liste n'affiche pas toutes les éléments, vérifier que des éléments 
      qui n'étaient pas affichés apparaissent lors du tri.

    * Infinite scroll ou pagination

    * Tri multi-colonnes


:details:

    * Réponse en JSON avec mixin serializer simple (cf view mixin django-geojson)
    
    * À terme devra être générique/simple (pas trop de code boiler plate)


#45 - Afficher la carte centrée des objets dans la fiche détails
----------------------------------------------------------------

* Afficher la fiche d'un tronçon.
* Une carte en lecture seule se charge, centrée sur le tronçon.
* La couche avec les autres tronçons se charge en asynchrone.
