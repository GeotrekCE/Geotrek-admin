==================
Edition d'un objet
==================

Segmentation dynamique
======================

Tous les objets sont saisis et stockés relativement aux tronçons, en utilisant la segmentation dynamique (https://makina-corpus.com/blog/metier/2014/la-segmentation-dynamique), sauf les évènements et contenus touristiques, les services et les signalements qui sont indépendants et ont leur propre géométrie. 

C'est pourquoi, modifier un tronçon peut entrainer des modifications des objets qui lui sont rattachés (signalétique, interventions, itinéraires, POIs...). Supprimer un tronçon, supprime les objets qui lui sont rattachés. 

Les éléments ponctuels et linéaires des différents modules sont stockés sous forme d'évènements (PKdebut, PKfin et décalage dans la table ``geotrek.core_topology``) liés à un ou plusieurs tronçons (``geotrek.core_pathaggregation``).

Un objet peut ainsi être associé à un ou plusieurs tronçons, partiellement ou entièrement. 

Les objets ponctuels ne sont associés qu'à un seul tronçon, sauf dans le cas où ils sont positionnés à une intersection de tronçons.

Chaque évènement dispose néanmoins d'une géométrie calculée à partir de leur segmentation dynamique pour faciliter leur affichage dans Geotrek ou dans QGIS. Il ne faut néanmoins pas modifier directement ces géométries, elles sont calculées automatiquement quand on modifie l'évènement d'un objet.

A noter aussi que des vues dans les différents schémas permettent d'accéder aux objets de manière plus lisibles et simplifiée (``gestion.m_v_interventions`` par exemple).

Snapping - Aimantage - Accrochage
=================================

Quand vous créez un objet, il est possible de le snapper (aimanter) aux objets existants. C'est notamment utile pour bien raccorder les tronçons entre eux. Quand vous raccrochez un tronçon à un tronçon existant, ce dernier est coupé automatiquement à la nouvelle intersection. 

Les fonctions d'aimantage ne sont pas disponibles lors de la création d'un nouvel objet (linéraire ou ponctuel). Il faut commencer par le créer sur puis le modifier pour disposer des fonctionnalités d'aimantage, activé automatiquement lorsque l'on se rapproche d'un objet existant. Par défaut la distance d'imantage est de 30 pixels mais elle est modifiable en configuration avancée.

Itinérance
==========

Il est possible de créer des randonnées itinérantes (sur plusieurs jours) et d'y associer des étapes comme sur cet exemple : http://www.grand-tour-ecrins.fr/a-pied/tour-de-la-berarde/.

Pour cela il faut créer un itinéraire parent (séjour itinérant complet) puis y ajouter des itinéraires enfants (étapes) de manière ordonnée, dans le champs `Enfants` présent dans l'onglet `Avancé` du formulaire itinéraire du séjour complet. 

Le séjour complet ainsi que chaque sont donc chacunes des randonnées comme les autres. La seule différence est que les étapes (itinéraires enfants) sont rattachées à l'itinéraire parent.

Si vous ne souhaitez pas que les étapes soient affichées dans la page de Recherche de Geotrek-rando, il ne faut pas les publier. Il suffit alors de publier l'itinéraire parent, pour que toutes les étapes qui y sont rattachées apparaissent uniquement dans sa fiche détail de Geotrek-rando. 
