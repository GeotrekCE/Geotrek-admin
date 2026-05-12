from django.apps import AppConfig
from django.core.checks import Tags, register
from django.utils.translation import gettext_lazy as _


class TrekkingConfig(AppConfig):
    name = "geotrek.trekking"
    verbose_name = _("Trekking")

    def ready(self):
        from .forms import POIForm, ServiceForm, TrekForm

        def check_hidden_fields_settings(app_configs, **kwargs):
            # Check all Forms hidden fields settings
            errors = TrekForm.check_fields_to_hide()
            errors.extend(POIForm.check_fields_to_hide())
            errors.extend(ServiceForm.check_fields_to_hide())
            return errors

        register(check_hidden_fields_settings, Tags.security)
