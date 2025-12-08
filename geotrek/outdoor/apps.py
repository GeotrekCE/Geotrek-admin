from django.apps import AppConfig
from django.core.checks import Tags, register
from django.utils.translation import gettext_lazy as _


class OutdoorConfig(AppConfig):
    name = "geotrek.outdoor"
    verbose_name = _("Outdoor")

    def ready(self):
        from .forms import CourseForm, SiteForm

        def check_hidden_fields_settings(app_configs, **kwargs):
            # Check all Forms hidden fields settings
            errors = SiteForm.check_fields_to_hide()
            errors.extend(CourseForm.check_fields_to_hide())
            return errors

        register(check_hidden_fields_settings, Tags.security)
