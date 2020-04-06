from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ZoningConfig(AppConfig):
    name = 'geotrek.zoning'
    verbose_name = _("Zoning")
