from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from geotrek.appconfig import GeotrekConfig


class FlatpagesConfig(GeotrekConfig):
    name = 'geotrek.flatpages'
    verbose_name = _("Flatpages")
