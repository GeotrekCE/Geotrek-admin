from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LandConfig(AppConfig):
    name = 'geotrek.land'
    verbose_name = _("Land")
