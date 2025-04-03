from django.conf import settings
from django.urls import path
from mapentity.registry import MapEntityOptions

from geotrek.altimetry.views import (
    ElevationArea,
    ElevationChart,
    ElevationProfile,
    serve_elevation_chart,
)

app_name = "altimetry"
urlpatterns = [
    path(
        "%s/profiles/<path:model_name>-<int:pk>.png" % settings.MEDIA_URL.strip("/"),
        serve_elevation_chart,
    ),
]


class AltimetryEntityOptions(MapEntityOptions):
    elevation_profile_view = ElevationProfile
    elevation_area_view = ElevationArea
    elevation_chart_view = ElevationChart

    def scan_views(self, *args, **kwargs):
        """Adds the URLs of all views provided by ``AltimetryMixin`` models."""
        views = super().scan_views(*args, **kwargs)
        altimetry_views = [
            path(
                "api/<lang:lang>/{modelname}s/<int:pk>/profile.json".format(
                    modelname=self.modelname
                ),
                self.elevation_profile_view.as_view(model=self.model),
                name="%s_profile" % self.modelname,
            ),
            path(
                "api/<lang:lang>/{modelname}s/<int:pk>/dem.json".format(
                    modelname=self.modelname
                ),
                self.elevation_area_view.as_view(model=self.model),
                name="%s_elevation_area" % self.modelname,
            ),
            path(
                "api/<lang:lang>/{modelname}s/<int:pk>/profile.svg".format(
                    modelname=self.modelname
                ),
                self.elevation_chart_view.as_view(model=self.model),
                name="%s_profile_svg" % self.modelname,
            ),
        ]
        return views + altimetry_views
