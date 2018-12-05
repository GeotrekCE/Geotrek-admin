from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import connection

from geotrek.common.utils.postgresql import load_sql_files, move_models_to_schemas


def pm_callback(sender, **kwargs):
    """
    Post Migrate callbghack Re/load sql files and move models to schemas
    """
    load_sql_files(sender.label)
    move_models_to_schemas(sender.label)


def check_srid_has_meter_unit(sender, **kwargs):
    if not hasattr(check_srid_has_meter_unit, '_checked'):
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                *
            FROM spatial_ref_sys
            WHERE
                 srtext ILIKE '%%meter%%'
            AND srid=%s;""", [settings.SRID])
        results = cursor.fetchall()
        if len(results) == 0:
            err_msg = 'Unit of SRID EPSG:%s is not meter.' % settings.SRID
            raise ImproperlyConfigured(err_msg)
    check_srid_has_meter_unit._checked = True
