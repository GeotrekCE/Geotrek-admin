from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from geotrek.core.appconfig import GeotrekConfig


class CommonConfig(GeotrekConfig):
    name = 'geotrek.common'
    verbose_name = _("Common")
