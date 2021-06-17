from django.apps import AppConfig
from django.core.checks import register, Tags
from django.utils.translation import gettext_lazy as _


class CoreConfig(AppConfig):
    name = 'geotrek.core'
    verbose_name = _("Core")

    def ready(self):
        from .checks import check_fields_to_hide
        register(check_fields_to_hide, Tags.security)
