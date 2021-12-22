===============
Troubleshouting
===============

Geotrek-admin logs are stored in ``/opt/geotrek-admin/var/log/geotrek.log`` file.

But if Geotrek-admin does not start, take a look to systemd logs for each of the 3 Geotrek-admin services
(user web interface, API and asynchronous tasks):

::

   sudo journalctl -eu geotrek-ui
   sudo journalctl -eu geotrek-api
   sudo journalctl -eu geotrek-celery

The output is paginated. With -e option you are at the end of the logs but you can go up an down with arrows.
Type Q to quit. If you want to copy the log to a file, do:

::

   sudo journalctl -u geotrek-ui > systemd-geotrek-ui.log


Frequent problems encountered
-----------------------------

Error 500 with `django.db.utils.IntegrityError … NOT NULL for column "language"`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`django.db.utils.IntegrityError: ERREUR:  une valeur NULL viole la contrainte NOT NULL de la colonne « language »`

This means specific migrations for translated fields have not been executed on database during update.
You have to run them manually, classical migrations included:

::

    geotrek migrate
    geotrek sync_translation_fields
    geotrek update_translation_fields
    geotrek update_geotrek_permissions
    geotrek update_post_migration_languages

