"""

    Geotrek startup script.

    This is executed only once at startup.

"""
from south.signals import pre_migrate, post_migrate
from django.conf import settings
from django.db import connection
from django.db.models.signals import pre_syncdb, post_syncdb
from django.core.exceptions import ImproperlyConfigured

from mapentity.helpers import api_bbox

from geotrek.common.utils.postgresql import load_sql_files, move_models_to_schemas


"""
    http://djangosnippets.org/snippets/2311/
    Ensure South will update our custom SQL during a call to `migrate`.
"""


def run_initial_sql_post_migrate(sender, **kwargs):
    app_label = kwargs.get('app')
    load_sql_files(app_label)
    move_models_to_schemas(app_label)


def run_initial_sql_post_syncdb(sender, **kwargs):
    app = kwargs.get('app')
    models_module = app.__name__
    app_label = models_module.rsplit('.')[-2]
    load_sql_files(app_label)
    move_models_to_schemas(app_label)


def check_srid_has_meter_unit(sender, **kwargs):
    if not hasattr(check_srid_has_meter_unit, '_checked'):
        cursor = connection.cursor()
        cursor.execute("""
            SELECT * FROM spatial_ref_sys
            WHERE srtext ILIKE '%%meter%%' AND srid=%s;""", [settings.SRID])
        results = cursor.fetchall()
        if len(results) == 0:
            err_msg = 'Unit of SRID EPSG:%s is not meter.' % settings.SRID
            raise ImproperlyConfigured(err_msg)
    check_srid_has_meter_unit._checked = True


if settings.TEST and not settings.SOUTH_TESTS_MIGRATE:
    pre_syncdb.connect(check_srid_has_meter_unit, dispatch_uid="geotrek.core.checksrid")
    post_syncdb.connect(run_initial_sql_post_syncdb, dispatch_uid="geotrek.core.sqlautoload")
    # During tests, the signal is received twice unfortunately
    # https://code.djangoproject.com/ticket/17977
else:
    pre_migrate.connect(check_srid_has_meter_unit, dispatch_uid="geotrek.core.checksrid")
    post_migrate.connect(run_initial_sql_post_migrate, dispatch_uid="geotrek.core.sqlautoload")


"""
    Computed client-side setting.
"""
settings.LEAFLET_CONFIG['SPATIAL_EXTENT'] = api_bbox(settings.SPATIAL_EXTENT, buffer=settings.VIEWPORT_MARGIN)
