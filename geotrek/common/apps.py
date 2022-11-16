from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CommonConfig(AppConfig):
    name = 'geotrek.common'
    verbose_name = _("Common")

    def ready(self):
        import geotrek.common.lookups  # NOQA
        import geotrek.common.signals  # NOQA
