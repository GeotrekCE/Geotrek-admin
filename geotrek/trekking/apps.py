from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TrekkingConfig(AppConfig):
    name = 'geotrek.trekking'
    verbose_name = _("Trekking")
