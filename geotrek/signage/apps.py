from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from geotrek.appconfig import GeotrekConfig


class SignageConfig(GeotrekConfig):
    name = 'geotrek.signage'
    verbose_name = _("Signage")
