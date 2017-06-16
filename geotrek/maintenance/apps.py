from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from geotrek.appconfig import GeotrekConfig


class MaintenanceConfig(GeotrekConfig):
    name = 'geotrek.maintenance'
    verbose_name = _("Maintenance")
