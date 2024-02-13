.. _les-troncons:

Les tronçons
============

C'est le socle essentiel et central de Geotrek. Un tronçon est un objet linéaire, entre deux intersections. Le mécanisme de segmentation dynamique permet de ne pas devoir le recouper pour y rattacher des informations.

Les tronçons peuvent être soit numérisés dans Geotrek-admin, soit importés directement dans l'outil via :

- la commande décrite `ici <https://geotrek.readthedocs.io/en/latest/install/import.html#import-paths>`_, après avoir préalablement nettoyé la géométrie des lignes à l'aide du plugin GRASS dans QGIS. Cette procédure est à privilégier car elle a l'avantage de faire des vérifications topologiques sur les données.

- l'outil Qgis en suivant ce `tutoriel <https://makina-corpus.com/sig-webmapping/importer-une-couche-de-troncons-dans-geotrek>`_ pour charger des tronçons dans la base de données PostGIS Geotrek à partir d'un réseau de sentiers. Il faut s'assurer en amont que les lignes à insérer sont topologiquement propres. 


Si ils sont numérisés directement dans Geotrek-admin, il est possible d'afficher sur la carte un fichier GPX ou GeoJSON pour faciliter leur localisation.

Quand un nouveau tronçon intersecte un tronçon existant, ce dernier est découpé automatiquement à la nouvelle intersection.

En plus de leur géométrie, quelques informations peuvent être associées à chaque tronçon (nom, départ, arrivée, confort, source, enjeu d'entretien, usage et réseaux).

Comme pour les autres objets, les informations altimétriques sont calculées automatiquement grace au MNT présent dans la base de données.

Idem pour les intersections automatiques avec les zonages (communes, secteurs, zonages réglementaires) et les objets des autres modules qui sont intersectés automatiquement à chaque ajout ou modification d'un objet.

Comme pour tous les modules, il est possible d'exporter la liste des tronçons affichés (CSV, SHP ou GPX) ou bien la fiche complète d'un tronçon (ODT, DOC ou PDF).

Comme pour tous les modules, il est aussi possible d'attacher des documents à chaque tronçon depuis sa fiche détail (images, PDF, tableurs, ZIP...).

Enfin, toujours depuis la fiche détail d'un tronçon, il est possible d'en afficher l'historique des modifications.
