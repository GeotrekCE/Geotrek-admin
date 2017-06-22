from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from geotrek.appconfig import GeotrekConfig


class CirkwiConfig(GeotrekConfig):
    name = 'geotrek.cirkwi'
    verbose_name = _("Cirkwi")
