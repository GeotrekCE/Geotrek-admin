from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FlatpagesConfig(AppConfig):
    name = "geotrek.flatpages"
    verbose_name = _("Flatpages")

    def ready(self):
        # Apply the treebeard 5/modeltranslation compatibility patch during app startup.
        import geotrek.flatpages.compat  # NOQA
