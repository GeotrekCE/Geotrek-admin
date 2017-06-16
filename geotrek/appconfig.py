from __future__ import unicode_literals

from django.apps import AppConfig
from django.db.models.signals import post_migrate, pre_migrate

from common.utils.signals import pm_callback, check_srid_has_meter_unit


class GeotrekConfig(AppConfig):
    def __init__(self, *args, **kwargs):
        pre_migrate.connect(check_srid_has_meter_unit, sender=self, dispatch_uid='geotrek.core.checksrid')
        super(GeotrekConfig, self).__init__(*args, **kwargs)

    def ready(self):
        post_migrate.connect(pm_callback, sender=self, dispatch_uid='geotrek.core.movetoschemas')
