from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class MaintenanceConfig(AppConfig):
    name = 'geotrek.maintenance'
    verbose_name = _("Maintenance")
