"""
    http://djangosnippets.org/snippets/2311/
    Ensure South will update our custom SQL during a call to `migrate`.
"""
from south.signals import post_migrate

from geotrek.common.utils.postgresql import load_sql_files


def run_initial_sql(sender, **kwargs):
    app_label = kwargs.get('app')
    load_sql_files(app_label)


post_migrate.connect(run_initial_sql, dispatch_uid="geotrek.core.sqlautoload")
