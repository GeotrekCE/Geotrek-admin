from django.conf import settings
from django.conf.urls import patterns, url
from mapentity.registry import MapEntityOptions

from geotrek.altimetry.views import (ElevationProfile, ElevationChart,
                                     ElevationArea, serve_elevation_chart)


urlpatterns = patterns(
    '',
    url(r'^%s/profiles/(?P<model_name>.+)-(?P<pk>\d+).png$' % settings.MEDIA_URL.strip('/'), serve_elevation_chart),
)


class AltimetryEntityOptions(MapEntityOptions):
    elevation_profile_view = ElevationProfile
    elevation_area_view = ElevationArea
    elevation_chart_view = ElevationChart

    def scan_views(self, *args, **kwargs):
        """ Adds the URLs of all views provided by ``AltimetryMixin`` models.
        """
        views = super(AltimetryEntityOptions, self).scan_views(*args, **kwargs)
        altimetry_views = patterns(
            '',
            url(r'^api/(?P<lang>\w+)/{modelname}s/(?P<pk>\d+)/profile.json$'.format(modelname=self.modelname),
                self.elevation_profile_view.as_view(model=self.model),
                name="%s_profile" % self.modelname),
            url(r'^api/(?P<lang>\w+)/{modelname}s/(?P<pk>\d+)/dem.json$'.format(modelname=self.modelname),
                self.elevation_area_view.as_view(model=self.model),
                name="%s_elevation_area" % self.modelname),
            url(r'^api/(?P<lang>\w+)/{modelname}s/(?P<pk>\d+)/profile.svg$'.format(modelname=self.modelname),
                self.elevation_chart_view.as_view(model=self.model),
                name='%s_profile_svg' % self.modelname),
        )
        return views + altimetry_views
