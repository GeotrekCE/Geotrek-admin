from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from geotrek.appconfig import GeotrekConfig


class ZoningConfig(GeotrekConfig):
    name = 'geotrek.zoning'
    verbose_name = _("Zoning")
