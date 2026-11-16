from django.conf import settings

from .common import (
    FlatPageViewSet,  # noqa
    SettingsView,  # noqa
)
from .trekking import TrekViewSet  # noqa

if "drf_yasg" in settings.INSTALLED_APPS:
    from .swagger import schema_view  # noqa
