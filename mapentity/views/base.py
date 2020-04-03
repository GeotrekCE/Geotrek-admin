from __future__ import unicode_literals

import json
import logging
import mimetypes
import os
from datetime import datetime
import re

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.gis.db.models import GeometryField
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.http import (HttpResponse, HttpResponseBadRequest, Http404)
from django.shortcuts import get_object_or_404
from django.utils.six.moves.urllib.parse import quote
from django.views import static
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic.base import TemplateView
from paperclip.settings import get_attachment_permission, get_attachment_model

from mapentity import models as mapentity_models
from .mixins import JSONResponseMixin, FilterListMixin, ModelViewMixin
from ..decorators import view_permission_required
from ..helpers import capture_image
from ..settings import app_settings, _MAP_STYLES

logger = logging.getLogger(__name__)


def serve_attachment(request, path):
    """
    Serve media/ for authorized users only, since it can contain sensitive
    information (uploaded documents)
    """
    original_path = re.sub(r'\.\d+x\d+_q\d+(_crop)?\.(jpg|png|jpeg)$', '', path, count=1, flags=re.IGNORECASE)
    attachment = get_object_or_404(get_attachment_model(), attachment_file=original_path)
    obj = attachment.content_object
    if not issubclass(obj._meta.model, mapentity_models.MapEntityMixin):
        raise Http404
    if not obj.is_public():
        if not request.user.is_authenticated:
            raise PermissionDenied
        if not request.user.has_perm(get_attachment_permission('read_attachment')):
            raise PermissionDenied
        if not request.user.has_perm('{}.read_{}'.format(obj._meta.app_label, obj._meta.model_name)):
            raise PermissionDenied

    content_type, encoding = mimetypes.guess_type(path)

    if settings.DEBUG:
        response = static.serve(request, path, settings.MEDIA_ROOT)
    else:
        response = HttpResponse()
        response[app_settings['SENDFILE_HTTP_HEADER']] = os.path.join(settings.MEDIA_URL_SECURE, path)
    response["Content-Type"] = content_type or 'application/octet-stream'
    if encoding:
        response["Content-Encoding"] = encoding
    if app_settings['SERVE_MEDIA_AS_ATTACHMENT']:
        response['Content-Disposition'] = "attachment; filename={0}".format(
            os.path.basename(path))
    return response


class JSSettings(JSONResponseMixin, TemplateView):
    """
    Javascript settings, in JSON format.
    Likely to be overriden. Contains only necessary stuff
    for mapentity.
    """

    def get_context_data(self):
        dictsettings = {}
        dictsettings['debug'] = settings.DEBUG
        dictsettings['map'] = dict(
            extent=getattr(settings, 'LEAFLET_CONFIG', {}).get('SPATIAL_EXTENT'),
            styles=_MAP_STYLES,
        )

        # URLs
        root_url = app_settings['ROOT_URL']
        root_url = root_url if root_url.endswith('/') else '{}/'.format(root_url)
        dictsettings['urls'] = {}
        dictsettings['urls']['root'] = root_url

        from django.db import models
        from mapentity.registry import MapEntityOptions

        class ModelName(mapentity_models.MapEntityMixin, models.Model):
            pass

        options = MapEntityOptions(ModelName)

        dictsettings['urls']['static'] = settings.STATIC_URL
        dictsettings['urls']['layer'] = '{}{}'.format(root_url, options._url_path(mapentity_models.ENTITY_LAYER)[1:-1])
        dictsettings['urls']['detail'] = '{}modelname/0/'.format(root_url)
        dictsettings['urls']['format_list'] = '{}{}'.format(
            root_url, options._url_path(mapentity_models.ENTITY_FORMAT_LIST)[1:-1]
        )
        dictsettings['urls']['screenshot'] = reverse("mapentity:map_screenshot")

        # Useful for JS calendars
        date_format = settings.DATE_INPUT_FORMATS[0].replace('%Y', 'yyyy').replace('%m', 'mm').replace('%d', 'dd')
        dictsettings['date_format'] = date_format
        # Languages
        dictsettings['languages'] = dict(available=dict(app_settings['TRANSLATED_LANGUAGES']),
                                         default=app_settings['LANGUAGE_CODE'])
        return dictsettings


class BaseListView(FilterListMixin, ModelViewMixin):
    columns = None

    def __init__(self, *args, **kwargs):
        super(BaseListView, self).__init__(*args, **kwargs)

        if self.columns is None:
            # All model fields except geometries
            self.columns = [field.name for field in self.get_model()._meta.fields
                            if not isinstance(field, GeometryField)]
            # Id column should be the first one
            self.columns.remove('id')
            self.columns.insert(0, 'id')

    @view_permission_required()
    def dispatch(self, *args, **kwargs):
        return super(BaseListView, self).dispatch(*args, **kwargs)


@csrf_exempt
@login_required
def map_screenshot(request):
    """
    This view allows to take screenshots, via a django-screamshot service, of
    the map **currently viewed by the user**.

    - A context full of information is built on client-side and posted here.
    - We reproduce this context, via headless browser, and take a capture
    - We return the resulting image as attachment.

    This seems overkill ? Please look around and find a better way.
    """
    try:
        printcontext = request.POST['printcontext']
        assert len(printcontext) < 2048, "Print context is way too big."

        # Prepare context, extract and add infos
        context = json.loads(printcontext)
        selector = context.pop('selector')
        map_url = context.pop('url')
        map_url = request.build_absolute_uri(map_url)
        context['print'] = True
        printcontext = json.dumps(context)
        contextencoded = quote(printcontext)
        map_url += '?context=%s' % contextencoded
        logger.debug("Capture %s" % map_url)

        # Capture image and return it
        width = context.get('viewport', {}).get('width')
        height = context.get('viewport', {}).get('height')

        response = HttpResponse()
        capture_image(map_url, response, width=width, height=height, selector=selector)
        response['Content-Disposition'] = 'attachment; filename=%s.png' % datetime.now().strftime('%Y%m%d-%H%M%S')
        return response

    except Exception as exc:
        logger.exception(exc)
        return HttpResponseBadRequest(exc)


@require_http_methods(["POST"])
@csrf_exempt
@login_required
def history_delete(request, path=None):
    path = request.POST.get('path', path)
    if path:
        history = request.session.get('history')
        if history:
            history = [h for h in history if h['path'] != path]
            request.session['history'] = history
    return HttpResponse()
