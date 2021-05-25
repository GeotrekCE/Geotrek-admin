from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DivingConfig(AppConfig):
    name = 'geotrek.diving'
    verbose_name = _("Diving")
