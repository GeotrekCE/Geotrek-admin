from django.utils.translation import ugettext_lazy as _

from geotrek.appconfig import GeotrekConfig


class SensitivityConfig(GeotrekConfig):
    name = 'geotrek.sensitivity'
    verbose_name = _("Sensitivity")
