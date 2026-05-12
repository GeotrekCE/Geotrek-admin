from django.apps import AppConfig
from django.core.checks import Tags, register
from django.utils.translation import gettext_lazy as _


class InfrastructureConfig(AppConfig):
    name = "geotrek.infrastructure"
    verbose_name = _("Infrastructure")

    def ready(self):
        from .forms import InfrastructureForm

        def check_hidden_fields_settings(app_configs, **kwargs):
            # Check all Forms hidden fields settings
            errors = InfrastructureForm.check_fields_to_hide()
            return errors

        register(check_hidden_fields_settings, Tags.security)
