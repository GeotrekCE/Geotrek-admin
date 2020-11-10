from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InfrastructureConfig(AppConfig):
    name = 'geotrek.infrastructure'
    verbose_name = _("Infrastructure")
