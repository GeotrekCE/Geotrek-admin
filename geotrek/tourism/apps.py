from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from geotrek.appconfig import GeotrekConfig


class TourismConfig(GeotrekConfig):
    name = 'geotrek.tourism'
    verbose_name = _("Tourism")
