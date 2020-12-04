from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class OutdoorConfig(AppConfig):
    name = 'geotrek.outdoor'
    verbose_name = _("Outdoor")
