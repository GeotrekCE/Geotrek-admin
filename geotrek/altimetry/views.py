from django.views.generic.edit import BaseDetailView
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from mapentity.decorators import view_cache_response_content
from mapentity.views import JSONResponseMixin, LastModifiedMixin


class HttpSVGResponse(HttpResponse):
    content_type = 'image/svg+xml'

    def __init__(self, content='', **kwargs):
        kwargs['content_type'] = self.content_type
        super(HttpSVGResponse, self).__init__(content, **kwargs)


class ElevationChart(LastModifiedMixin, BaseDetailView):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ElevationChart, self).dispatch(*args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        return HttpSVGResponse(self.get_object().get_elevation_profile_svg(),
                               **response_kwargs)


class ElevationProfile(LastModifiedMixin, JSONResponseMixin, BaseDetailView):
    """Extract elevation profile from a path and return it as JSON"""

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ElevationProfile, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Put elevation profile into response context.
        """
        obj = self.get_object()
        data = {}
        # Formatted as distance, elevation, [lng, lat]
        for step in obj.get_elevation_profile():
            formatted = step[0], step[3], step[1:3]
            data.setdefault('profile', []).append(formatted)
        return data


class ElevationArea(LastModifiedMixin, JSONResponseMixin, BaseDetailView):
    """Extract elevation profile on an area and return it as JSON"""

    def view_cache_key(self):
        """Used by the ``view_cache_response_content`` decorator.
        """
        obj = self.get_object()
        return 'altimetry_dem_area_%s' % obj.pk

    def latest_updated(self):
        """Used by the ``view_cache_response_content`` decorator.
        """
        obj = self.get_object()
        return obj.date_update

    @method_decorator(login_required)
    @view_cache_response_content()
    def dispatch(self, *args, **kwargs):
        return super(ElevationArea, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        obj = self.get_object()
        return obj.get_elevation_area()
