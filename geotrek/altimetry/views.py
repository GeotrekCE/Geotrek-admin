import os

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import caches
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views import static
from django.views.generic.edit import BaseDetailView
from mapentity.views import JSONResponseMixin, LastModifiedMixin

from geotrek.common.permissions import PublicOrReadPermMixin
from geotrek.decorators import cbv_cache_response_content
from .models import AltimetryMixin


class HttpSVGResponse(HttpResponse):
    content_type = 'image/svg+xml'

    def __init__(self, content='', **kwargs):
        kwargs['content_type'] = self.content_type
        super().__init__(content, **kwargs)


class ElevationChart(LastModifiedMixin, PublicOrReadPermMixin, BaseDetailView):

    def render_to_response(self, context, **response_kwargs):
        svg_cache = caches['fat']
        lang = self.kwargs['lang']
        obj = self.get_object()
        date_update = obj.get_date_update().strftime('%y%m%d%H%M%S%f'),
        cache_lookup = f"altimetry_profile_{obj.pk}_{date_update}_svg_{lang}"
        content = svg_cache.get(cache_lookup)
        if content:
            return HttpSVGResponse(content=content, **response_kwargs)
        profile_svg = obj.get_elevation_profile_svg(lang)
        svg_cache.set(cache_lookup, profile_svg)
        return HttpSVGResponse(profile_svg, **response_kwargs)


class ElevationProfile(LastModifiedMixin, JSONResponseMixin,
                       PublicOrReadPermMixin, BaseDetailView):
    """Extract elevation profile from a path and return it as JSON"""

    def view_cache_key(self):
        """Used by the ``view_cache_response_content`` decorator.
        """
        obj = self.get_object()
        date_update = obj.get_date_update().strftime('%y%m%d%H%M%S%f'),
        return f"altimetry_profile_{obj.pk}_{date_update}"

    @cbv_cache_response_content()
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Put elevation profile into response context.
        """
        return self.object.get_formatted_elevation_profile_and_limits()


class ElevationArea(LastModifiedMixin, JSONResponseMixin, PublicOrReadPermMixin,
                    BaseDetailView):
    """Extract elevation profile on an area and return it as JSON"""

    def view_cache_key(self):
        """Used by the ``view_cache_response_content`` decorator.
        """
        obj = self.get_object()
        date_update = obj.get_date_update().strftime('%y%m%d%H%M%S%f'),
        return f"altimetry_dem_area_{obj.pk}_{date_update}"

    @cbv_cache_response_content()
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        return self.object.get_elevation_area()


def serve_elevation_chart(request, model_name, pk, from_command=False):
    model = get_object_or_404(ContentType, model=model_name).model_class()
    if not issubclass(model, AltimetryMixin):
        raise Http404
    obj = get_object_or_404(model, pk=pk)
    if not obj.is_public():
        if not request.user.is_authenticated:
            raise PermissionDenied
        if not request.user.has_perm('%s.read_%s' % (model._meta.app_label, model_name)):
            raise PermissionDenied
    language = request.LANGUAGE_CODE
    obj.prepare_elevation_chart(language)
    path = obj.get_elevation_chart_path(language).replace(settings.MEDIA_ROOT, '').lstrip('/')

    if settings.DEBUG or from_command:
        response = static.serve(request, path, settings.MEDIA_ROOT)
    else:
        response = HttpResponse()
        response['X-Accel-Redirect'] = os.path.join(settings.MEDIA_URL_SECURE, path)
    response["Content-Type"] = 'image/png'
    return response
