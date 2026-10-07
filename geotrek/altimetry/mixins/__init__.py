from django.urls import path
from mapentity.registry import MapEntityOptions

from geotrek.altimetry.views import ElevationArea, ElevationChart, ElevationProfile


class AltimetryEntityOptions(MapEntityOptions):
    elevation_profile_view = ElevationProfile
    elevation_area_view = ElevationArea
    elevation_chart_view = ElevationChart

    def scan_views(self, *args, **kwargs):
        """Adds the URLs of all views provided by ``AltimetryMixin`` models."""
        views = super().scan_views(*args, **kwargs)
        altimetry_views = [
            path(
                f"api/<lang:lang>/{self.modelname}s/<int:pk>/profile.json",
                self.elevation_profile_view.as_view(model=self.model),
                name=f"{self.modelname}_profile",
            ),
            path(
                f"api/<lang:lang>/{self.modelname}s/<int:pk>/dem.json",
                self.elevation_area_view.as_view(model=self.model),
                name=f"{self.modelname}_elevation_area",
            ),
            path(
                f"api/<lang:lang>/{self.modelname}s/<int:pk>/profile.svg",
                self.elevation_chart_view.as_view(model=self.model),
                name=f"{self.modelname}_profile_svg",
            ),
        ]
        return views + altimetry_views
