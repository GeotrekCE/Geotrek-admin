from django.conf import settings
from django.urls import path

from . import views

app_name = "altimetry"
urlpatterns = [
    path(
        "{}/profiles/<path:model_name>-<int:pk>.png".format(
            settings.MEDIA_URL.strip("/")
        ),
        views.serve_elevation_chart,
    ),
]
