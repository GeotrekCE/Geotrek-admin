from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FlatpagesConfig(AppConfig):
    name = 'geotrek.flatpages'
    verbose_name = _("Flatpages")
