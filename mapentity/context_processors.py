from django.conf import settings as settings_  # import the settings file

from . import app_settings, registry


def settings(request):
    return dict(
        TITLE=app_settings['TITLE'],
        DEBUG=settings_.DEBUG,
        VERSION=getattr(settings_, 'VERSION', 'unknown'),
        registry=registry,
    )
