from django.conf import settings as settings_ # import the settings file

from caminae import __version__


def settings(request):
    return dict(
        TITLE=settings_.TITLE,
        DEBUG=settings_.DEBUG,
        VERSION=__version__,
    )
