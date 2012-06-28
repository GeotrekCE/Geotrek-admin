
L'approche initiale consistait à créer une application dédiée à la gestion des "compléments SQL" fournissant :

* Un model permettant de décrire le compléments SQL, les instances de ce model serait associé à une propiété de la classe Meta

* Une commande de management qui ferait le tour des models et analyserait leur .meta pour savoir s'il faut pousser du SQL dans la base ou non.

En cours de réflexion, je suis passé par : https://docs.djangoproject.com/en/dev/howto/initial-data/#initial-sql.

Ça a l'air d'être prévu pour mettre des données au départ mais ça supporte tout SQL. Il y a par ailleurs un snippet pour forcer South à rejouer les SQL à chaque migration.

À faire :

* Ajouter un test case ?
