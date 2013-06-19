from django.conf import settings as settings_  # import the settings file

from mapentity import registry


def settings(request):
    return dict(
        TITLE=getattr(settings_, 'TITLE'),
        DEBUG=settings_.DEBUG,
        VERSION=getattr(settings_, 'VERSION'),
        registry=registry,
    )
