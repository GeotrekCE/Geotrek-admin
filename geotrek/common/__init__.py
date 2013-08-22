"""

    Geotrek startup script.

    This is executed only once at startup.

"""
from south.signals import post_migrate
from django.conf import settings

from mapentity.helpers import api_bbox

from geotrek.common.utils.postgresql import load_sql_files


"""
    http://djangosnippets.org/snippets/2311/
    Ensure South will update our custom SQL during a call to `migrate`.
"""

def run_initial_sql(sender, **kwargs):
    app_label = kwargs.get('app')
    load_sql_files(app_label)


post_migrate.connect(run_initial_sql, dispatch_uid="geotrek.core.sqlautoload")

