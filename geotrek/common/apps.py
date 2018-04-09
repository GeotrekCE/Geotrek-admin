from django.utils.translation import ugettext_lazy as _

from geotrek.appconfig import GeotrekConfig


class CommonConfig(GeotrekConfig):
    name = 'geotrek.common'
    verbose_name = _("Common")
