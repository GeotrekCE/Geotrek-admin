from django.conf import settings

from .common import SettingsView  # noqa

if "geotrek.trekking" in settings.INSTALLED_APPS:
    from .trekking import TrekViewSet  # noqa
if "geotrek.flatpages" in settings.INSTALLED_APPS:
    from .common import FlatPageViewSet  # noqa
if "drf_yasg" in settings.INSTALLED_APPS:
    from .swagger import schema_view  # noqa
