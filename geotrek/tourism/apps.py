from django.apps import AppConfig
from django.core.checks import Tags, register
from django.utils.translation import gettext_lazy as _


class TourismConfig(AppConfig):
    name = "geotrek.tourism"
    verbose_name = _("Tourism")

    def ready(self):
        from .forms import TouristicContentForm, TouristicEventForm

        def check_hidden_fields_settings(app_configs, **kwargs):
            # Check all Forms hidden fields settings
            errors = TouristicContentForm.check_fields_to_hide()
            errors.extend(TouristicEventForm.check_fields_to_hide())
            return errors

        register(check_hidden_fields_settings, Tags.security)
