from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuthentConfig(AppConfig):
    name = "geotrek.authent"
    verbose_name = _("Authent")
