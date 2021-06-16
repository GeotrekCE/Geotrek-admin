from django.apps import AppConfig
from django.core.checks import register, Tags
from django.utils.translation import gettext_lazy as _


class CoreConfig(AppConfig):
    name = 'geotrek.core'
    verbose_name = _("Core")

    def ready(self):
        from .forms import PathForm

        def check_hidden_fields_settings(app_configs, **kwargs):
            return PathForm.check_fields_to_hide()

        register(check_hidden_fields_settings, Tags.security)
