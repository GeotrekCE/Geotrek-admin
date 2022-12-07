from django.apps import AppConfig
from django.conf import settings
from django.contrib.gis.gdal import SpatialReference
from django.core.checks import Error, register
from django.utils.translation import gettext_lazy as _


class CommonConfig(AppConfig):
    name = 'geotrek.common'
    verbose_name = _("Common")

    def ready(self):
        import geotrek.common.lookups  # NOQA
        import geotrek.common.signals  # NOQA


@register()
def srid_check(app_configs, **kwargs):
    if SpatialReference(settings.SRID).units[1] != 'metre':
        return [
            Error(
                'Unit of SRID EPSG:%s is not meter.' % settings.SRID,
                id='geotrek.E001',
            )
        ]
    return []
