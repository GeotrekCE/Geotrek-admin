==================
8. Pages statiques
==================

.. contents::
   :local:
   :depth: 2


.. danger::
    Depuis Geotrek-Rando V3, le composant Bootstrap n'est plus utilisé pour gérer les différentes tailles d'écran. Cela signifie que la mise en page créée dans Geotrek-Admin n'est pas reproduite sur le site public. Cette documentation n'est valable que pour Geotrek-Rando V2 en attendant sa mise à jour expliquant le fonctionnement actuel. Voir le ticket : https://github.com/GeotrekCE/Geotrek-rando-v3/issues/466


Les pages statiques sont les pages d'information et de contextualisation de votre portail web Geotrek-rando. Comme pourraient l'être les premières pages d'un topo-guide papier. Elles peuvent aussi être consultées dans votre application Geotrek-mobile.

.. figure :: /images/user-manual/flatpages-gtecrins.jpg

    Exemple de page statique (http://www.grand-tour-ecrins.fr/informations/le-grand-tour-des-ecrins/)

Elles permettent de fournir à l'internaute et futur randonneur des informations génériques : présentation de votre structure, votre projet de randonnée, recommandations, informations pratiques, etc.

Elles sont gérées depuis l'Adminsite de Geotrek-admin et sont ensuite publiées sur Geotrek-rando à chaque synchronisation du contenu. 

.. image :: /images/user-manual/flatpages-adminsite.jpg

8.1 Créer une page statique
============================

Depuis l'Adminsite de Geotrek, sélectionnez "Pages statiques" dans la rubrique "Flatpages".

.. image :: /images/user-manual/flatpages-flatpages.png

Vous accédez alors à la liste des pages statiques. 
Cliquer sur "Ajouter Page statique" en haut à droite de l'écran pour créer une première page.

8.2 Construire une page statique
================================

Sélectionnez la langue du contenu que vous souhaitez saisir : en / fr / it...

Saisissez :

* un titre (sans guillemets, parenthèses, etc.)
* un ordre optionnel (pour définir l'ordre d'apparition dans le menu de votre Geotrek-rando)
* cochez « publié » lorsque vous souhaiterez mettre en ligne votre page
* définissez la « source » (comprendre ici la destination d'affichage et donc votre Geotrek-rando)
* sélectionnez une cible (Geotrek-rando et/ou Geotrek-mobile ou cachée pour créer une page qui ne sera pas listée dans le menu).

Attention, à chaque fois que cela vous est demandé, veillez à sélectionner la langue de votre contenu.

.. image :: /images/user-manual/flatpages-form.jpg

L'interface permet de construire sa page en responsive design, c'est-à-dire qu'il est possible de disposer les blocs de contenu pour s'adapter aux différentes tailles d'écrans des utilisateurs.

.. image :: /images/user-manual/flatpages-bootstrap-responsive.jpg

Choisissez le gabarit sur lequel vous souhaitez construire votre page : 12 / 6-6 / 4-4-4 / etc. Ce sont des formats prédéfinis d'assemblage de blocs basés sur 12 colonnes qui occupent 100% de la largeur de l'écran (Bootstrap).

.. image :: /images/user-manual/flatpages-bootstrap-grids.jpg

Vous pouvez aussi utiliser ou vous inspirer des 2 gabarits d'exemple (Gabarit 1 et Gabarit 2).

.. image :: /images/user-manual/flatpages-blocks.jpg

Vous pouvez ajouter autant de gabarits que vous le souhaitez sur une seule page.

Une fois que vous avez ajusté vos blocs de contenu pour un affichage sur ordinateur (Desktop), vous devez basculer sur l'affichage sur mobile (Phone) pour l'adapter à de plus petits écrans (en cliquant sur les + et - bleus de chaque bloc). Privilégiez alors des blocs sur une colonne faisant 100% de large.

.. image :: /images/user-manual/flatpages-blocks-edit.jpg

8.3 Ajouter du contenu dans un bloc
===================================

En cliquant dans la zone de texte, une barre d'édition apparaît. Sur un format classique comme dans les logiciels de traitement texte, plusieurs menus et outils sont alors disponibles :

* File : (fichier)
* Edit : retour, copier-coller,
* Insert : Insérer une image, un lien, des caractères spéciaux

.. image :: /images/user-manual/flatpages-wysiwyg.jpg

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

8.4 Astuces
============

1. Ne jamais utiliser la touche retour du clavier [ ? ] sans avoir le curseur sélectionné dans une zone de texte. Cela équivaut à revenir à la page précédente et vous perdrez tout votre contenu sans le sauvegarder.
2. Pour reproduire une page dans une langue différente : copier le Code Source et coller-le Code Source de votre nouvelle langue. Vous n'aurez plus qu'à traduire votre texte ! Idem pour traduire un contenu dans une autre langue.
3. Si deux de vos pages ont le même numéro d'ordre d'apparition, une seule des deux sera affichée sur la plate-forme numérique.
