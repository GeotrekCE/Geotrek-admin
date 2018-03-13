from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.gis.gdal import SpatialReference

from geotrek.common.utils.postgresql import load_sql_files, move_models_to_schemas


def pm_callback(sender, **kwargs):
    """
    Post Migrate callbghack Re/load sql files and move models to schemas
    """
    load_sql_files(sender)
    move_models_to_schemas(sender)


def check_srid_has_meter_unit():
    if not hasattr(check_srid_has_meter_unit, '_checked'):
        if SpatialReference(settings.SRID).units[1] != 'metre':
            err_msg = 'Unit of SRID EPSG:%s is not meter.' % settings.SRID
            raise ImproperlyConfigured(err_msg)
    check_srid_has_meter_unit._checked = True
