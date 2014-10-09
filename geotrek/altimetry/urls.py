from django.conf.urls import patterns, url
from mapentity.registry import MapEntityOptions

from geotrek.altimetry.views import (ElevationProfile, ElevationChart,
                                 ElevationArea)


class AltimetryEntityOptions(MapEntityOptions):
    elevation_profile_view = ElevationProfile
    elevation_area_view = ElevationArea
    elevation_chart_view = ElevationChart

    def scan_views(self, *args, **kwargs):
        """ Adds the URLs of all views provided by ``AltimetryMixin`` models.
        """
        views = super(AltimetryEntityOptions, self).scan_views(*args, **kwargs)
        altimetry_views = patterns('',
            url(r'^api/%s/(?P<pk>\d+)/profile.json$' % self.modelname,
                self.elevation_profile_view.as_view(model=self.model),
                name="%s_profile" % self.modelname),
            url(r'^api/%s/(?P<pk>\d+)/dem.json$' % self.modelname,
                self.elevation_area_view.as_view(model=self.model),
                name="%s_elevation_area" % self.modelname),
            url(r'^api/%s/(?P<pk>\d+)/profile.svg$' % self.modelname,
                self.elevation_chart_view.as_view(model=self.model),
                name='%s_profile_svg' % self.modelname),
        )
        return views + altimetry_views
