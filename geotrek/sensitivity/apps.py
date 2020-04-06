from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SensitivityConfig(AppConfig):
    name = 'geotrek.sensitivity'
    verbose_name = _("Sensitivity")
