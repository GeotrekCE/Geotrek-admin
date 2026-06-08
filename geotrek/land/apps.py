from django.apps import AppConfig
from django.core.checks import Tags, register
from django.utils.translation import gettext_lazy as _


class LandConfig(AppConfig):
    name = "geotrek.land"
    verbose_name = _("Land")

    def ready(self):
        from .forms import OnNetworkLandEdgeForm, OffNetworkLandEdgeForm

        def check_hidden_fields_settings(app_configs, **kwargs):
            # Check all Forms hidden fields settings
            errors = OnNetworkLandEdgeForm.check_fields_to_hide()
            errors.extend(OffNetworkLandEdgeForm.check_fields_to_hide())
            return errors

        register(check_hidden_fields_settings, Tags.security)
