import os

from django.views.generic.edit import BaseDetailView
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.views import static

from mapentity.decorators import view_cache_response_content
from mapentity.views import JSONResponseMixin, LastModifiedMixin

from geotrek.common.views import PublicOrReadPermMixin

from .models import AltimetryMixin


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


class ElevationProfile(LastModifiedMixin, JSONResponseMixin,
                       PublicOrReadPermMixin, BaseDetailView):
    """Extract elevation profile from a path and return it as JSON"""

    def get_context_data(self, **kwargs):
        """
        Put elevation profile into response context.
        """
        data = {}
        elevation_profile = self.object.get_elevation_profile()
        # Formatted as distance, elevation, [lng, lat]
        for step in elevation_profile:
            formatted = step[0], step[3], step[1:3]
            data.setdefault('profile', []).append(formatted)
        data['limits'] = dict(zip(['ceil', 'floor'], self.object.get_elevation_limits()))
        return data


class ElevationArea(LastModifiedMixin, JSONResponseMixin, PublicOrReadPermMixin,
                    BaseDetailView):
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

    @view_cache_response_content()
    def dispatch(self, *args, **kwargs):
        return super(ElevationArea, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        return self.object.get_elevation_area()


def serve_elevation_chart(request, model_name, pk, from_command=False):
    try:
        model = ContentType.objects.get(model=model_name).model_class()
    except:
        raise Http404
    if not issubclass(model, AltimetryMixin):
        raise Http404
    obj = get_object_or_404(model, pk=pk)
    if not obj.is_public():
        if not request.user.is_authenticated():
            raise PermissionDenied
        if not request.user.has_perm('%s.read_%s' % (model._meta.app_label, model_name)):
            raise PermissionDenied
    language = request.LANGUAGE_CODE
    obj.prepare_elevation_chart(language, request.build_absolute_uri('/'))
    path = obj.get_elevation_chart_path(language).replace(settings.MEDIA_ROOT, '').lstrip('/')

    if settings.DEBUG or from_command:
        response = static.serve(request, path, settings.MEDIA_ROOT)
    else:
        response = HttpResponse()
        response['X-Accel-Redirect'] = os.path.join(settings.MEDIA_URL_SECURE, path)
    response["Content-Type"] = 'image/png'
    return response
