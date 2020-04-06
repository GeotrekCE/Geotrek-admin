from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AltimetryConfig(AppConfig):
    name = 'geotrek.altimetry'
    verbose_name = _("Altimetry")
