from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SensitivityConfig(AppConfig):
    name = 'geotrek.sensitivity'
    verbose_name = _("Sensitivity")
