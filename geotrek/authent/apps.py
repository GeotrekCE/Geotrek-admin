import os

from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class AuthentConfig(AppConfig):
    name = 'geotrek.authent'
    verbose_name = _("Authent")

    def ready(self):
        session_dir = os.path.join(settings.CACHE_ROOT, "sessions")
        if not os.path.exists(session_dir):
            os.mkdir(session_dir)
