from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from geotrek.appconfig import GeotrekConfig


class CoreConfig(GeotrekConfig):
    name = 'geotrek.core'
    verbose_name = _("Core")
