==================
TESTS FONCTIONNELS
==================

Sprint 1 - Version 0.1.0
========================

#88 - Automatiser l'installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Se référer à la section deployment du fichier ``README.rst`` à la racine
du projet.

Le processus d'installation demande la saisie des paramètres nécessaires.

Le projet est ensuite accessible à l'URL du serveur.


#84 - Afficher l'interface dans la langue de l'utilisateur
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dans l'interface d'administration, créer un utilisateur. La langue par défaut
est le français, les choix sont EN, FR, IT.

Se connecter avec cet utilisateur, vérifier que l'interface s'affiche dans 
sa langue. 

    Note: Un changement de langue dans le profil n'est pris en compte qu'après reconnexion.

#10 - Éditer les listes de choix avec l'AdminSite Django
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Créer plusieurs objets, associés à des structures différentes (ex: prestataires).

Vérifier que la liste (temporaire au sprint 1) affichée dans l'interface contient 
bien les objets crées.

Si je change la structure de l'utilisateur. La liste des objets associés à la structure change.

Si je change la structure d'un objet, il n'apparait plus dans la liste.


#30 - Montrer la carte globale sur la page d'accueil
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

La page d'accueil affiche une carte avec les tronçons. 

:note:

    Pour l'instant, la carte est en projection 4326 (attente fin POC #12).
    
    Les performances ne sont pas au rendez-vous (6 sec. pour générer le fichier, 11 millisec. pour l'afficher)


#94 - Activer le système de cache Django
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pas de test spécifique, à part vérifier que les réponses du serveur sont
extrèmement plus rapides que lorsque le cache est vide (i.e. après déploiement).
