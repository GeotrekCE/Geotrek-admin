from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from geotrek.appconfig import GeotrekConfig


class AuthentConfig(GeotrekConfig):
    name = 'geotrek.authent'
    verbose_name = _("Authent")
