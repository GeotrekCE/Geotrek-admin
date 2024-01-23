=======
7. APIs
=======

.. contents::
   :local:
   :depth: 2

7.1 API interne
===============

Geotrek dispose d’une API (Application Programming Interface) qui sert à exposer les informations de Geotrek-Admin dans le but de pouvoir faire communiquer des systèmes entre eux pour échanger des données.

Cette API, désormais dans sa version 2 permet à toute structure tiers de récupérer des données et de les intégrer dans son système ou ses applications.

A ce jour de nombreux partenaires des structures utilisatrices de l’application Geotrek ont déjà utilisé cette API pour intégrer les données dans leurs outils.

C’est le cas des applications de :
    • Visorando
    • Kalkin
    • Apidae
    • IGNrando'
    • Outdooractive

Pour changer les paramètres d'accès de l'API, référez vous à cette section :ref:`API <api>`

7.2 APIs externes
==================

7.2.1 Geotrek et IGNrando'
--------------------------

Depuis la version 0.32.0, Geotrek-admin est capable de produire un flux des itinéraires et POIs présents dans sa BDD au format Cirkwi pour pouvoir les importer directement dans IGNrando' (https://makina-corpus.com/sig-webmapping/geotrek-et-lign-ca-fonctionne).

Exemple des randonnées et POIs du Parc national des Ecrins publiées sur IGNrando' depuis Geotrek-admin : https://ignrando.fr/fr/communautes/parc-national-des-ecrins 

Depuis cette version, 2 flux sont automatiquement générés par Geotrek-admin au format attendu par l'IGN :

- [URL_GEOTREK-ADMIN]/api/cirkwi/circuits.xml
- [URL_GEOTREK-ADMIN]/api/cirkwi/pois.xml

Il est possible d'exclure les POI du flux pour ne diffuser que les randonnées. Pour cela, ajouter le paramètre ``?withoutpois=1`` à la fin de l'URL (``http://XXXXX/api/cirkwi/circuits.xml?withoutpois=1``).

Il est possible de filtrer les POI du flux par structure. Pour cela, ajouter le paramètre ``?structures=<identifiant_de_la_structure>`` à la fin de l'URL (``http://XXXXX/api/cirkwi/pois.xml?structures=2``).
Vous pouvez filtrer avec plusieurs structures : en séparant les identifiants par des virgules (``http://XXXXX/api/cirkwi/pois.xml?structures=2,5,3``).

Il est également possible de filtrer les randonnées du flux par structure et par portail. Pour cela, ajouter le paramètre ``?structures=<identifiant_de_la_structure>``.
ou ``?portals=<identifian_de_la_structure>`` à la fin de l'URL (``http://XXXXX/api/cirkwi/circuits.xml?portals=3``).
Tout comme les pois Vous pouvez filtrer avec plusieurs structures et portails : en séparant les identifiants par des virgules.

Il est possible de filtrer les randonnées par portail et structure en même temps en séparant les 2 filtres par un ``&`` (``http://XXXXX/api/cirkwi/circuits.xml?portals=3&structures=1``).

Le référentiel CIRKWI a été intégré dans 3 tables accessibles dans l'interface d'administration Django (à ne pas modifier) :

.. figure:: ../images/user-manual/cirkwi-tables.png
   :alt: Ensemble des champs paramétrables pour le référentiel CIKWI
   :align: center

   Ensemble des champs paramétrables pour le référentiel CIKWI

Si vous ne souhaitez pas utiliser les valeurs par défaut ou avez créez vos propres typologies, il faut que vous renseigniez les correspondances entre les catégories de votre Geotrek et celles du référentiel IGN (Cirkwi) dans votre Adminsite. Comme indiqué ici : https://github.com/GeotrekCE/Geotrek-admin/issues/806.

* Pratique >> locomotion/loisirs
* Accessibilite >> thematiques/tags
* Themes >> thematiques/tags
* Types de POI >> Categories POI

Les correspondances avec les valeurs de ces 3 tables sont donc à renseigner dans les tables Geotrek des Pratiques, Accessibilités, Thèmes et Types de POI.

Ce même flux est aussi utilisable pour alimenter directement la plateforme Cirkwi : https://pro.cirkwi.com/importez-vos-donnees-geotrek-dans-cirkwi/.

:Note:

    Geotrek-admin dispose aussi d'une API générique permettant d'accéder aux contenus d'une instance à l'adresse : ``[URL_GEOTREK-ADMIN]/api/v2/``

7.2.2 Geotrek et APIDAE
---------------------------

Il existe plusieurs passerelles entre la plateforme d'informations touristiques APIDAE et Geotrek. 

7.2.2.1 APIDAE vers Geotrek
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Actuellement, certains contenus touristiques sont synchronisés automatiquement avec une base APIDAE, il s'agit des contenus situés dans les catégories suivantes :
- Hébergement
- Point info

Les autres contenus touristiques sont synchronisés avec un flux Esprit Parc National et sont situés dans une catégorie du même nom.

Il est également possible de mettre en place une passerelle pour les POIs, les Lieux de Renseignement, les Aménagements. Il est aussi possible d'enrichir le lien avec les contenus touristiques pour avoir par exemple d'autres catégories.

7.2.2.2 Geotrek vers APIDAE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Il existe aussi un lien dans l'autre sens, permettant d'envoyer vers APDIAE les itinéraires pédestres existants dans Geotrek.

L'API permet de connecter une instance Geotrek vers les "Équipements" contenant le critère "itinéraire de randonnée pédestre" dans APIDAE.

Les randonnées VTT, trail, vélo et les tours itinérants ne sont pas intégrés à ce jour dans la passerelle

Pour plus d'information, se référer à la documentation en ligne de `Sitourisme <https://github.com/GeotrekCE/Sitourisme#sitourisme-paca-api>`_. 
