import os
import json
import logging
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.views import static
from django.views.generic.detail import DetailView
from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.template.exceptions import TemplateDoesNotExist
from django.template.defaultfilters import slugify
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from djappypod.response import OdtTemplateResponse
from django_weasyprint import WeasyTemplateResponseMixin

from ..settings import app_settings
from .. import models as mapentity_models
from ..helpers import convertit_url, download_to_stream, user_has_perm
from ..decorators import save_history, view_permission_required
from ..forms import AttachmentForm
from ..models import LogEntry, ADDITION, CHANGE, DELETION
from .. import serializers as mapentity_serializers
from ..helpers import suffix_for, name_for, smart_get_template
from .base import history_delete, BaseListView
from .mixins import (ModelViewMixin, FormViewMixin)


logger = logging.getLogger(__name__)


def log_action(request, object, action_flag):
    if not app_settings['ACTION_HISTORY_ENABLED']:
        return
    if not request.user.is_authenticated:
        return
    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=object.get_content_type_id(),
        object_id=object.pk,
        object_repr=force_text(object),
        action_flag=action_flag
    )


class MapEntityList(BaseListView, ListView):
    """

    A generic view list web page.

    """

    def get_template_names(self):
        default = super(MapEntityList, self).get_template_names()
        return default + ['mapentity/mapentity_list.html']

    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_LIST

    @view_permission_required(login_url='login')
    def dispatch(self, request, *args, **kwargs):
        # Save last list visited in session
        # (only if viewing a true list, not an inherited ENTITY_JSON_LIST for ex.)
        if self.__class__.get_entity_kind() == mapentity_models.ENTITY_LIST:
            request.session['last_list'] = request.path
        return super(MapEntityList, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MapEntityList, self).get_context_data(**kwargs)
        context['filterform'] = self._filterform  # From FilterListMixin
        context['columns'] = self.columns  # From BaseListView

        context['create_label'] = self.get_model().get_create_label()

        model = self.get_model()
        perm_create = model.get_permission_codename(mapentity_models.ENTITY_CREATE)
        can_add = user_has_perm(self.request.user, perm_create)
        context['can_add'] = can_add

        perm_export = model.get_permission_codename(mapentity_models.ENTITY_FORMAT_LIST)
        can_export = user_has_perm(self.request.user, perm_export)
        context['can_export'] = can_export

        return context


class MapEntityFormat(BaseListView, ListView):
    """

    Export the list to a particular format.

    """
    DEFAULT_FORMAT = 'csv'

    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_FORMAT_LIST

    def render_to_response(self, context, **response_kwargs):
        """Delegate to the fmt view function found at dispatch time"""
        formats = {
            'csv': self.csv_view,
            'shp': self.shape_view,
            'gpx': self.gpx_view,
        }
        extensions = {
            'shp': 'zip'
        }
        fmt_str = self.request.GET.get('format', self.DEFAULT_FORMAT)
        formatter = formats.get(fmt_str)
        if not formatter:
            logger.warning("Unknown serialization format '%s'" % fmt_str)
            return HttpResponseBadRequest()

        filename = '%s-%s-list' % (datetime.now().strftime('%Y%m%d-%H%M'),
                                   str(slugify(u"{}".format(self.get_model()._meta.verbose_name))))
        filename += '.%s' % extensions.get(fmt_str, fmt_str)
        response = formatter(request=self.request, context=context, **response_kwargs)
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response

    def csv_view(self, request, context, **kwargs):
        serializer = mapentity_serializers.CSVSerializer()
        response = HttpResponse(content_type='text/csv')
        serializer.serialize(queryset=self.get_queryset(), stream=response,
                             model=self.get_model(), fields=self.columns, ensure_ascii=True)
        return response

    def shape_view(self, request, context, **kwargs):
        serializer = mapentity_serializers.ZipShapeSerializer()
        response = HttpResponse(content_type='application/zip')
        serializer.serialize(queryset=self.get_queryset(), model=self.get_model(),
                             stream=response, fields=self.columns)
        response['Content-length'] = str(len(response.content))
        return response

    def gpx_view(self, request, context, **kwargs):
        serializer = mapentity_serializers.GPXSerializer()
        response = HttpResponse(content_type='application/gpx+xml')
        serializer.serialize(self.get_queryset(), model=self.get_model(), stream=response,
                             geom_field=app_settings['GEOM_FIELD_NAME'])
        return response


class MapEntityMapImage(ModelViewMixin, DetailView):
    """
    A static file view, that serves the up-to-date map image (detail screenshot)
    On error, returns 404 status.
    """
    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_MAPIMAGE

    def render_to_response(self, context, **response_kwargs):
        obj = self.get_object()
        if not obj.is_public():
            if not self.request.user.is_authenticated:
                raise PermissionDenied
            if not self.request.user.has_perm('%s.read_%s' % (obj._meta.app_label, obj._meta.model_name)):
                raise PermissionDenied
        obj.prepare_map_image(self.request.build_absolute_uri('/'))
        path = obj.get_map_image_path().replace(settings.MEDIA_ROOT, '').lstrip('/')
        if settings.DEBUG or not app_settings['SENDFILE_HTTP_HEADER']:
            response = static.serve(self.request, path, settings.MEDIA_ROOT)
        else:
            response = HttpResponse(content_type='image/png')
            response[app_settings['SENDFILE_HTTP_HEADER']] = os.path.join(settings.MEDIA_URL_SECURE, path)
        return response


class MapEntityDocumentBase(ModelViewMixin, DetailView):

    def __init__(self, *args, **kwargs):
        super(MapEntityDocumentBase, self).__init__(*args, **kwargs)
        self.model = self.get_model()

    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_DOCUMENT

    @view_permission_required()
    def dispatch(self, *args, **kwargs):
        return super(MapEntityDocumentBase, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        rooturl = self.request.build_absolute_uri('/')

        # Screenshot of object map is required, since present in document
        self.get_object().prepare_map_image(rooturl)
        context = super(MapEntityDocumentBase, self).get_context_data(**kwargs)
        context['datetime'] = datetime.now()
        context['objecticon'] = os.path.join(settings.STATIC_ROOT, self.get_entity().icon_big)
        context['logo_path'] = os.path.join(settings.MEDIA_ROOT, 'upload/logo-header.png')
        if not os.path.exists(context['logo_path']):
            context['logo_path'] = os.path.join(settings.STATIC_ROOT, 'images/logo-header.png')
        context['STATIC_URL'] = self.request.build_absolute_uri(settings.STATIC_URL)
        context['STATIC_ROOT'] = settings.STATIC_ROOT
        context['MEDIA_URL'] = self.request.build_absolute_uri(settings.MEDIA_URL)
        context['MEDIA_ROOT'] = settings.MEDIA_ROOT
        return context


class MapEntityWeasyprint(MapEntityDocumentBase):

    def __init__(self, *args, **kwargs):
        super(MapEntityWeasyprint, self).__init__(*args, **kwargs)

        suffix = suffix_for(self.template_name_suffix, "_pdf", "html")
        self.template_name = smart_get_template(self.model, suffix)
        if not self.template_name:
            raise TemplateDoesNotExist(name_for(self.model._meta.app_label,
                                                self.model._meta.object_name.lower(), suffix))
        self.template_attributes = smart_get_template(self.model, suffix_for(self.template_name_suffix,
                                                                             "_attributes", "html"))
        self.template_css = smart_get_template(self.model, suffix_for(self.template_name_suffix, "_pdf", "css"))

    def get_context_data(self, **kwargs):
        context = super(MapEntityWeasyprint, self).get_context_data(**kwargs)
        context['map_path'] = self.get_object().get_map_image_path()
        context['template_attributes'] = self.template_attributes
        context['template_css'] = self.template_css
        return context


class MapEntityDocumentWeasyprint(MapEntityWeasyprint, WeasyTemplateResponseMixin):
    pass


class MapEntityMarkupWeasyprint(MapEntityWeasyprint):

    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_MARKUP


class MapEntityDocumentOdt(MapEntityDocumentBase):
    response_class = OdtTemplateResponse
    with_html_attributes = True

    def __init__(self, *args, **kwargs):
        super(MapEntityDocumentOdt, self).__init__(*args, **kwargs)

        suffix = suffix_for(self.template_name_suffix, "", "odt")
        self.template_name = smart_get_template(self.model, suffix)
        if not self.template_name:
            raise TemplateDoesNotExist(name_for(self.model._meta.app_label,
                                                self.model._meta.object_name.lower(), suffix))

    def get_context_data(self, **kwargs):
        context = super(MapEntityDocumentOdt, self).get_context_data(**kwargs)
        if self.with_html_attributes:
            context['attributeshtml'] = self.get_object().get_attributes_html(self.request)
        context['_'] = _
        return context


if app_settings['MAPENTITY_WEASYPRINT']:
    MapEntityDocument = MapEntityDocumentWeasyprint
else:
    MapEntityDocument = MapEntityDocumentOdt


class Convert(View):
    """
    A proxy view to conversion server.
    """
    format = 'pdf'
    http_method_names = ['get']

    def source_url(self):
        return self.request.GET.get('url')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Convert, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        source = self.source_url()
        if source is None:
            return HttpResponseBadRequest('url parameter missing')

        if not source.startswith('http'):
            source = self.request.build_absolute_uri(source)

        fromtype = request.GET.get('from')
        format = request.GET.get('to', self.format)
        url = convertit_url(source, from_type=fromtype, to_type=format)

        response = HttpResponse()
        received = download_to_stream(url, response,
                                      silent=True,
                                      headers=self.request_headers())
        if received:
            filename = os.path.basename(received.url)
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response

    def request_headers(self):
        """Retrieves the original Accept-Language header of this view request.
        Django converts header names to upper-case with underscores.

        See http://stackoverflow.com/questions/3889769/get-all-request-headers-in-django
        """
        if 'HTTP_ACCEPT_LANGUAGE' not in self.request.META:
            return {}
        return {'Accept-Language': self.request.META['HTTP_ACCEPT_LANGUAGE']}


class DocumentConvert(Convert, DetailView):
    """
    Convert the object's document to PDF
    """
    def source_url(self):
        return self.get_object().get_document_url()


"""

    CRUD

"""


class MapEntityCreate(ModelViewMixin, FormViewMixin, CreateView):

    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_CREATE

    def get_template_names(self):
        default = super(MapEntityCreate, self).get_template_names()
        return default + ['mapentity/mapentity_form.html']

    @classmethod
    def get_title(cls):
        return cls.model.get_create_label()

    @view_permission_required(login_url=mapentity_models.ENTITY_LIST)
    def dispatch(self, *args, **kwargs):
        return super(MapEntityCreate, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(MapEntityCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super(MapEntityCreate, self).form_valid(form)
        messages.success(self.request, _("Created"))
        log_action(self.request, self.object, ADDITION)
        return response

    def form_invalid(self, form):
        messages.error(self.request, _("Your form contains errors"))
        return super(MapEntityCreate, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(MapEntityCreate, self).get_context_data(**kwargs)
        return context


class MapEntityDetail(ModelViewMixin, DetailView):

    def __init__(self, *args, **kwargs):
        super(MapEntityDetail, self).__init__(*args, **kwargs)
        # Try to load template for each lang and object detail
        model = self.get_model()
        suffix = suffix_for(self.template_name_suffix, "_attributes", "html")
        self.template_attributes = smart_get_template(model, suffix)

    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_DETAIL

    def get_template_names(self):
        default = super(MapEntityDetail, self).get_template_names()
        return default + ['mapentity/mapentity_detail.html']

    def get_title(self):
        return u"{}".format(self.get_object())

    @view_permission_required(login_url=mapentity_models.ENTITY_LIST)
    @save_history()
    def dispatch(self, *args, **kwargs):
        return super(MapEntityDetail, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MapEntityDetail, self).get_context_data(**kwargs)
        logentries_max = app_settings['ACTION_HISTORY_LENGTH']
        logentries = LogEntry.objects.filter(
            content_type_id=self.object.get_content_type_id(),
            object_id=self.object.pk
        ).order_by('-id')
        context['activetab'] = self.request.GET.get('tab')
        context['empty_map_message'] = _("No map available for this object.")
        context['logentries'] = logentries[:logentries_max]
        context['logentries_hellip'] = logentries.count() > logentries_max

        perm_update = self.get_model().get_permission_codename(mapentity_models.ENTITY_UPDATE)
        can_edit = user_has_perm(self.request.user, perm_update)
        context['can_edit'] = can_edit
        context['attachment_form_class'] = AttachmentForm
        context['template_attributes'] = self.template_attributes
        context['mapentity_weasyprint'] = app_settings['MAPENTITY_WEASYPRINT']
        if 'context' in self.request.GET:
            mapcontext = json.loads(self.request.GET['context'])
            if 'mapsize' in mapcontext:
                context['mapwidth'] = int(mapcontext['mapsize']['width'])
                context['mapheight'] = int(mapcontext['mapsize']['height'])

        return context


class MapEntityUpdate(ModelViewMixin, FormViewMixin, UpdateView):

    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_UPDATE

    def get_template_names(self):
        default = super(MapEntityUpdate, self).get_template_names()
        return default + ['mapentity/mapentity_form.html']

    def get_title(self):
        return _("Edit %s") % self.get_object()

    @view_permission_required(login_url=mapentity_models.ENTITY_DETAIL)
    def dispatch(self, *args, **kwargs):
        return super(MapEntityUpdate, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(MapEntityUpdate, self).get_form_kwargs()
        kwargs['user'] = self.request.user

        perm_delete = self.get_model().get_permission_codename(mapentity_models.ENTITY_DELETE)
        can_delete = user_has_perm(self.request.user, perm_delete)
        kwargs['can_delete'] = can_delete
        return kwargs

    def form_valid(self, form):
        response = super(MapEntityUpdate, self).form_valid(form)
        messages.success(self.request, _("Saved"))
        log_action(self.request, self.object, CHANGE)
        return response

    def form_invalid(self, form):
        messages.error(self.request, _("Your form contains errors"))
        return super(MapEntityUpdate, self).form_invalid(form)

    def get_success_url(self):
        return self.get_object().get_detail_url()


class MapEntityDelete(ModelViewMixin, DeleteView):

    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_DELETE

    def get_template_names(self):
        default = super(MapEntityDelete, self).get_template_names()
        return default + ['mapentity/mapentity_confirm_delete.html']

    @view_permission_required(login_url=mapentity_models.ENTITY_DETAIL)
    def dispatch(self, *args, **kwargs):
        return super(MapEntityDelete, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        log_action(self.request, self.object, DELETION)
        # Remove entry from history
        history_delete(request, path=self.object.get_detail_url())
        return super(MapEntityDelete, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return self.get_model().get_list_url()
