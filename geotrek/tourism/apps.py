from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TourismConfig(AppConfig):
    name = 'geotrek.tourism'
    verbose_name = _("Tourism")
