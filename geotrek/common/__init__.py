"""

    Geotrek startup script.

    This is executed only once at startup.

"""
from south.signals import post_migrate
from django.conf import settings
from django.db.models.signals import post_syncdb

from mapentity.helpers import api_bbox

from geotrek.common.utils.postgresql import load_sql_files


"""
    http://djangosnippets.org/snippets/2311/
    Ensure South will update our custom SQL during a call to `migrate`.
"""

def run_initial_sql_post_migrate(sender, **kwargs):
    app_label = kwargs.get('app')
    load_sql_files(app_label)


def run_initial_sql_post_syncdb(sender, **kwargs):
    app = kwargs.get('app')
    models_module = app.__name__
    app_label = models_module.rsplit('.')[-2]
    load_sql_files(app_label)


if settings.TEST and not settings.SOUTH_TESTS_MIGRATE:
    post_syncdb.connect(run_initial_sql_post_syncdb, dispatch_uid="geotrek.core.sqlautoload")
    # During tests, the signal is received twice unfortunately
    # https://code.djangoproject.com/ticket/17977
else:
    post_migrate.connect(run_initial_sql_post_migrate, dispatch_uid="geotrek.core.sqlautoload")


"""
    Computed client-side setting.
"""

settings.LEAFLET_CONFIG['SPATIAL_EXTENT'] = api_bbox(settings.SPATIAL_EXTENT, buffer=0.5)
