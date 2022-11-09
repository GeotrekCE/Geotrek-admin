from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class CommonConfig(AppConfig):
    name = 'geotrek.common'
    verbose_name = _("Common")

    def ready(self):
        import geotrek.common.lookups  # NOQA
        import geotrek.common.signals  # NOQA

        import os
        session_dir = os.path.join(settings.CACHE_ROOT, "sessions")
        if not os.path.exists(session_dir):
            os.mkdir(session_dir)
