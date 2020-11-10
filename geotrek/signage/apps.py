from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SignageConfig(AppConfig):
    name = 'geotrek.signage'
    verbose_name = _("Signage")
