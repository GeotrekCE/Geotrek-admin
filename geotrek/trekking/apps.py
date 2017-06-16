from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from geotrek.appconfig import GeotrekConfig


class TrekkingConfig(GeotrekConfig):
    name = 'geotrek.trekking'
    verbose_name = _("Trekking")
