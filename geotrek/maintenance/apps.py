from django.apps import AppConfig
from django.core.checks import Tags, register
from django.utils.translation import gettext_lazy as _


class MaintenanceConfig(AppConfig):
    name = "geotrek.maintenance"
    verbose_name = _("Maintenance")

    def ready(self):
        from .forms import InterventionForm, ProjectForm

        def check_hidden_fields_settings(app_configs, **kwargs):
            # Check all Forms hidden fields settings
            errors = InterventionForm.check_fields_to_hide()
            errors.extend(ProjectForm.check_fields_to_hide())
            return errors

        register(check_hidden_fields_settings, Tags.security)
