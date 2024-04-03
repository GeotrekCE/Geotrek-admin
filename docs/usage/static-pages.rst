=======================
Pages statiques & menus
=======================

.. contents::
   :local:
   :depth: 2

Les pages statiques sont les pages d'information et de contextualisation de votre portail web Geotrek-rando. Comme pourraient l'être les premières pages d'un topo-guide papier. Elles peuvent aussi être consultées dans votre application Geotrek-mobile.

.. figure:: /images/user-manual/flatpages-gtecrins.jpg

    Exemple de page statique (http://www.grand-tour-ecrins.fr/informations/le-grand-tour-des-ecrins/)

Les pages statiques permettent de fournir à l’internaute et futur randonneur des informations génériques : présentation de votre structure, votre projet de randonnée, recommandations, informations pratiques, etc.

Elles sont gérées depuis le site d'administration de Geotrek-admin et sont ensuite publiées sur Geotrek-rando via l'API.

Du point de vue d'un portail de valorisation comme Geotrek-rando on parle des pages statiques par opposition aux pages « dynamiques » qui correspondent à la page de recherche avec ses filtres et la carte, ainsi qu'aux pages de détails des résultats. Ces pages ne sont pas conçues manuellement mais sont un assemblage de multiples sources de données effectué par le logiciel Geotrek.

Pour rendre les pages statiques accessibles aux visiteurs Geotrek-admin permet de gérer les menus déroulants dans l'en-tête du portail. Les éléments du premier niveau sont toujours apparents (s'il y a assez d'espace d'affichage, ou dans un menu « Burger » sinon). Et il est possible de définir des éléments de menu dans un 2ème niveau, accessibles en déroulant les menus.

.. figure:: /images/user-manual/flatpages_header_menus_example.png

    Exemple de menus déroulants définis dans Geotrek-admin

La section correspondante et le type d'entités s'appelle Élément Menu, dans cette documentation on pourra parler de menu pour signifier les éléments de menu si ça ne porte pas à confusion.

Les exemples de présentation visuelle des menus et des pages statiques décrivent la manière dont Geotrek-rando peut exploiter ces données et paramètrages. La présentation pourrait être différente si le portail n'est pas propulsé par Geotrek-rando.

.. image:: /images/user-manual/flatpages-adminsite.jpg

Créer une page statique
========================

.. image:: /images/user-manual/flatpages_admin_section_pages_statiques.png

Le formulaire de création/modification d'une page statique contient les champs suivants :

- **Titre \***
- Publiée
- Portails
- Sources
- Image de couverture
- Auteur image couverture
- Contenu
- Position
- Relative à

Seul le champ Titre est obligatoire pour créer une page statique.

Les champs Titre, Publiée et Contenu peuvent recevoir une valeur différente pour chaque langue configurée.

*Titre*

    Il s'agit du titre de votre page qui sera visible et mis en avant sur la page elle-même. Le titre sert également à générer l'adresse web de la page.

*Publiée*

    Une page n'est visible sur le portail de valorisation que si elle a été publiée dans l'admin. On peut publier une page uniquement pour certaines langues.

*Portails*

    Ce champ ne concerne que les pages qui ne sont pas ciblée par un menu. Permet de rendre la page visible sur certains portails pour y faire référence en-dehors des menus de navigation (dans le bas de page, dans le contenu d'une autre page, etc).

*Sources*

    Permet d'attribuer une ou plusieurs sources au contenu de la page. Les sources peuvent être créées sur le site d'administration dans la section COMMUN ou directement avec le bouton + à côté de ce champ.

*Cover image*

    Permet de saisir une image grand format qui sera affichée en mode bandeau en haut de la page.

*Contenu*

    Le contenu de la page, sa mise en forme, les médias qui y sont insérés. Le contenu peut être traduit avec les valeurs spécifiques pour chaque langue configurée.

*Position* et *Relative à*

    Ces champs sont une alternative au glisser-déposer sur la liste des Pages Statiques et permettent de déplacer les pages dans l'arborescence (voir `Arborescence des pages statiques`_).

Mise en forme et médias
-----------------------

.. image:: /images/user-manual/flatpages_tinymce_tools.png

Le champ contenu expose un éditeur de texte riche (TinyMCE) permettant d'ajouter de la mise en forme et des médias dans le contenu de la page.

- mise en forme du texte : titres, styles du texte, couleur du texte
- insertion de listes
- encart "Information"
- lien sous forme de bouton
- citation

Médias :

- insérer une image
- insérer une vidéo YouTube
- insérer un lien vers une autre page
- encart de suggestion de contenu Geotrek

Insérer une image
-----------------

.. image:: /images/user-manual/flatpages_tinymce_tools_insert.png

L'outil *Insérer/modifier* une image permet d'insérer une image dans le contenu. Les champs suivants sont à renseigner :

- Source
- Description alternative : non-affichée, pour l'accessibilité et les formes de consultation alternatives du contenu
- Largeur et Hauteur de présentation de l'image en pixels
- checkbox Afficher le sous-titrage insère une zone de texte collée à l'image pour présenter un titre (le titre est à saisir dans le contenu une fois le formulaire validé)

Insérer des suggestions de contenu Geotrek
------------------------------------------

.. image:: /images/user-manual/flatpages_tinymce_tools_geotrek.png

Avec l'outil *Suggestions*, les champs suivants sont à renseigner :

- le type de contenu (itinéraires, contenu touristique, événements ou site d'activités de plein nature)
- les identifiants des contenus (séparés par des virgules. Par exemple : 12,8,73)
- un titre pour l'encart de suggestions

Après la validation du formulaire une zone récapitulant les informations saisies sous forme textuelle est placée dans le contenu de la page. Le site portail enrichira la présentation des suggestions avec les titres des contenus suggérés à la place des identifiants et les images associées.

Vérifier la mise en page du contenu
-----------------------------------

.. image:: /images/user-manual/flatpages_tinymce_tools_code.png

Les outils suivants sont disponibles :

- *Afficher les blocs* : permet de contrôler finement la séparation du contenu en blocs (pratique pour les paragraphes de texte)
- *Code source* : affiche et permet de modifier directement le contenu au format HTML (pour les utilisateurs avertis)

Publier une page
================

Une page créée n'est pas immédiatement visible sur un portail. Il faut d'abord la marquer comme Publiée pour chacune des langues souhaitées. Il faut ensuite lui donner un moyen d'être visitée sur le site portail. Plusieurs options :

- faire figurer un lien vers la page dans les menus déroulants (voir `Arborescence de menus`_)
- placer la page dans l'arborescence des pages (voir `Arborescence des pages statiques`_)
- placer un lien direct dans une autre section du site : dans une page d'accueil personnalisée, dans un bas de page, etc.

Arborescence de menus
=====================

.. image:: /images/user-manual/flatpages_admin_with_menuitems.png

La page liste des Éléments Menus indique la structure arborescente qui sous-tend les menus déroulants tels qu'ils apparaîtront sur le portail.

.. note::

    Un portail de type Geotrek Rando ne peut afficher que 2 niveaux de menus !

Chaque élément de menu a les champs suivants :

- *Titre*
- *Publié*
- *Portails*
- *Type de cible*
- [Si type de cible est "page"] la *page* cible
- [Si type de cible est "lien"] l'*URL du lien* (par langue) et checkbox *Ouvrir dans un nouvel onglet*
- *Position* et *Relative à*

Chaque Élément Menu peut avoir une cible ou non. S'il a une cible le clic sur le menu y accédera. Il y a trois possibilités de cibles :

- une page statique Geotrek, avec le type de cible = "page"
- avec le type de cible = "lien" :
  + une page web externe sur un autre site web, par exemple "https://fr.wikipedia.org/wiki/Randonnée". Auquel cas une bonne pratique web est d'ouvrir un nouvel onglet (checkbox cochée)
  + une page web interne au portail, typiquement une recherche pré-enregistrée, par exemple "/search?practices=4&difficulty=2&duration=1". Auquel cas une bonne pratique est de rester sur le même onglet (checkbox non-cochée)

Le champ *Plateforme* permet de différencier des menus destinés uniquement à un portail web ou uniquement à une app Geotrek Mobile. Cette possibilité de paramètrage sera bientôt supprimée.

Arborescence des pages statiques
================================

.. image:: /images/user-manual/flatpages_admin_with_flatpages.png

Les pages statiques sont organisées dans une structure arborescente, une page statique peut avoir des pages enfants et une unique page parente. L'arborescence des pages statiques permet d'organiser le contenu statique d'un portail d'une manière intelligible pour les visiteurs du site.

Les pages enfants sont accessibles depuis une page parente dans Geotrek-rando.

Compatibilité de contenu créé avec  l'ancien éditeur
====================================================

L'ancien éditeur de contenu des pages statiques (éditeur de grille avec Bootstrap) a été supprimé avec la déprécation de Geotrek-rando-v2.

Les pages statiques créées avec l'ancienne version de l'éditeur continueront de fonctionner sans changement sur le portail Geotrek-rando v3. Cependant il se peut que le balisage du contenu créé par l'ancien éditeur doive être retiré pour pouvoir utiliser à nouveau les styles et outils de mise en forme.

Comment procéder ?

- par précaution faire une copie du contenu, en incluant toutes les informations (URLs des images, etc)
- utiliser l'outil *code* ( ``< >`` ) pour obtenir une copie du contenu incluant les balises HTML
- retirer toutes les balises grâce à un outil en ligne (voir ci-dessous)
- remplacer l'ancien code avec le contenu nettoyé dans la fenêtre de l'outil *code*, valider
- refaire la mise en forme

Il existe beaucoup de service web pour nettoyer un contenu de ses balises HTML. Voici les deux premiers résultats provenant d'un moteur de recherche :

- https://striphtml.com/
- https://www.w3docs.com/tools/string-remove-tags
