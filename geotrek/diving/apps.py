from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from geotrek.appconfig import GeotrekConfig


class DivingConfig(GeotrekConfig):
    name = 'geotrek.diving'
    verbose_name = _("Diving")
