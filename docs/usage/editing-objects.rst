==================
Edition d'un objet
==================

Segmentation dynamique
======================

Certains objets sont saisis et stockés relativement aux tronçons, en utilisant `la segmentation dynamique <https://makina-corpus.com/sig-webmapping/la-segmentation-dynamique>`_. Il s'agit des objets suivants : sentiers, statuts, aménagements, interventions, itinéraires et POI. Tous les autres objets sont indépendants et ont leur propre géométrie.

C'est pourquoi, modifier un tronçon peut entrainer des modifications des objets qui lui sont rattachés (interventions, itinéraires, POIs...). Supprimer un tronçon, supprime les objets qui lui sont rattachés par segmentation dynamique.

Les éléments ponctuels et linéaires des différents modules sont stockés sous forme d'évènements (PKdebut, PKfin et décalage dans la table ``geotrek.core_topology``) liés à un ou plusieurs tronçons (``geotrek.core_pathaggregation``).

Un objet peut ainsi être associé à un ou plusieurs tronçons, partiellement ou entièrement.

Les objets ponctuels ne sont associés qu'à un seul tronçon, sauf dans le cas où ils sont positionnés à une intersection de tronçons.

Chaque évènement dispose néanmoins d'une géométrie calculée à partir de leur segmentation dynamique pour faciliter leur affichage dans Geotrek ou dans QGIS. Il ne faut néanmoins pas modifier directement ces géométries, elles sont calculées automatiquement quand on modifie l'évènement d'un objet.

.. notes

    Des vues SQL sont disponibles pour accéder aux objets de manière plus lisible et simplifiée (``v_interventions`` par exemple).

Snapping - Aimantage - Accrochage
=================================

Quand vous créez un objet, il est possible de le snapper (aimanter) aux objets existants. C'est notamment utile pour bien raccorder les tronçons entre eux. Quand vous raccrochez un tronçon à un tronçon existant, ce dernier est coupé automatiquement à la nouvelle intersection.

Les fonctions d'aimantage ne sont pas disponibles lors de la création d'un nouvel objet (linéraire ou ponctuel). Il faut commencer par le créer puis le modifier pour disposer des fonctionnalités d'aimantage, activées automatiquement lorsque l'on se rapproche d'un objet existant. Par défaut la distance d'imantage est de 30 pixels mais elle est modifiable en configuration avancée.
