from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from geotrek.appconfig import GeotrekConfig


class InfrastructureConfig(GeotrekConfig):
    name = 'geotrek.infrastructure'
    verbose_name = _("Infrastructure")
