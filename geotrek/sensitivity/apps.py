from django.apps import AppConfig
from django.core.checks import Tags, register
from django.utils.translation import gettext_lazy as _


class SensitivityConfig(AppConfig):
    name = "geotrek.sensitivity"
    verbose_name = _("Sensitivity")

    def ready(self):
        from .forms import RegulatorySensitiveAreaForm, SensitiveAreaForm

        def check_hidden_fields_settings(app_configs, **kwargs):
            # Check all Forms hidden fields settings
            errors = SensitiveAreaForm.check_fields_to_hide()
            errors.extend(RegulatorySensitiveAreaForm.check_fields_to_hide())
            return errors

        register(check_hidden_fields_settings, Tags.security)
