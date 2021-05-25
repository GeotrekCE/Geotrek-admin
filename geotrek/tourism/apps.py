from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TourismConfig(AppConfig):
    name = 'geotrek.tourism'
    verbose_name = _("Tourism")
