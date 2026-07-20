from django.conf import settings
from django.contrib.gis.gdal import SpatialReference
from django.core.checks import Error, register


@register()
def srid_check(app_configs, **kwargs):
    if SpatialReference(settings.SRID).units[1] != "metre":
        return [
            Error(
                f"Unit of SRID EPSG:{settings.SRID} is not meter.",
                id="geotrek.E001",
            )
        ]
    return []
