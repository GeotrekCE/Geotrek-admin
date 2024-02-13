==================
Modules de gestion
==================

Geotrek-admin comporte un certain nombre de modules de gestion des sentiers (tronçons, sentiers, statuts, aménagements, signalétique, interventions et chantiers).

Les tronçons sont les éléments de base sur lesquels s'appuient l'ensemble des objets des autres modules, en utilisant la segmentation dynamique (https://makina-corpus.com/blog/metier/2014/la-segmentation-dynamique).

Les modules signalétique et aménagement ont initialement été conçus dans une logique d’inventaire avec des possibilités de description basiques et génériques. Pour tout complément, il est possible d’attacher un ou plusieurs fichiers joints à chaque objet (photos, PDF, tableurs…).

Les modules interventions et chantiers ont été conçus de façon à permettre à la fois un inventaire et un suivi des travaux (prévisionnel, administratif et financier).

En termes de structuration, le choix initial a été de concevoir, sur le volet gestion, la gestion des valeurs des listes déroulantes structure par structure pour que chaque structure travaillant sur une même instance Geotrek-admin puisse avoir des typologies différentes (types de signalétique, d’aménagements, d’organismes...). 

Néanmoins, depuis la version 2.20 de Geotrek-admin (voir le changelog : https://github.com/GeotrekCE/Geotrek-admin/releases/tag/2.20.0), il est possible de partager des typologies entre les différentes structures en ne renseignant pas ce champ.
Un compte utilisateur appartenant à une structure X n'aura accès qu'aux typologies associées à celle-ci, ainsi qu'aux typologies partagées. De même, ce compte utilisateur ne pourra pas modifier ou supprimer des objets appartenant à une autre structure (c'est-à-dire créés par un compte utilisateur appartenant à une autre structure), sauf à avoir des permissions particulières.

Lors de la saisie d'un objet sur la carte, il est possible d'afficher une couche SIG ou un relevé GPX sur la carte lors de la création d'un objet sur la carte pour pouvoir le visualiser et le localiser sur la carte (``Charger un fichier local (GPX, KML, GeoJSON)``).

.. toctree::
    :maxdepth: 3

    path
    trail
    status
    infrastructure
    signage
    intervention
    project
