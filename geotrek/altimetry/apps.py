from django.utils.translation import ugettext_lazy as _

from geotrek.appconfig import GeotrekConfig


class AltimetryConfig(GeotrekConfig):
    name = 'geotrek.altimetry'
    verbose_name = _("Altimetry")
