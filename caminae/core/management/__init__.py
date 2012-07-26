"""
    http://djangosnippets.org/snippets/2311/
    Ensure South will update our custom SQL during a call to `migrate`.
"""
import logging
import traceback

from south.signals import post_migrate

logger = logging.getLogger(__name__)


def run_initial_sql(sender, **kwargs):
    app_label = kwargs.get('app')
    import os
    from django.db import connection, transaction, models
    app_dir = os.path.normpath(os.path.join(os.path.dirname(
                    models.get_app(app_label).__file__), 'sql'))
    backend_name = connection.settings_dict['ENGINE'].split('.')[-1]
    sql_files = [os.path.join(app_dir, "%s.%s.sql" % (app_label, backend_name)),
                 os.path.join(app_dir, "%s.sql" % app_label)]
    cursor = connection.cursor()
    for sql_file in sql_files:
        try:
            if os.path.exists(sql_file):
                logger.info("Loading initial SQL data from '%s'" % sql_file)
                f = open(sql_file)
                sql = f.read()
                f.close()
                cursor.execute(sql)
        except Exception, e:
            logger.error("Failed to install custom SQL file '%s': %s\n" %
                         (sql_file, e))
            traceback.print_exc()
            transaction.rollback_unless_managed()
        else:
            transaction.commit_unless_managed()
post_migrate.connect(run_initial_sql)
