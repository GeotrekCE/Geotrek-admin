from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AuthentConfig(AppConfig):
    name = 'geotrek.authent'
    verbose_name = _("Authent")
