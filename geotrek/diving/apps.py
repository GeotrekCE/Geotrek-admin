from django.apps import AppConfig
from django.core.checks import Tags, register
from django.utils.translation import gettext_lazy as _


class DivingConfig(AppConfig):
    name = "geotrek.diving"
    verbose_name = _("Diving")

    def ready(self):
        from .forms import DiveForm

        def check_hidden_fields_settings(app_configs, **kwargs):
            # Check all Forms hidden fields settings
            errors = DiveForm.check_fields_to_hide()
            return errors

        register(check_hidden_fields_settings, Tags.security)
