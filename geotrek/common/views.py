# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.decorators import method_decorator
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.utils import DatabaseError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

from mapentity.helpers import api_bbox
from mapentity import views as mapentity_views
from mapentity.settings import app_settings

from geotrek.common.utils import sql_extent
from geotrek import __version__

#async data imports
import os
import json
from zipfile import ZipFile
from geotrek.common.parsers import AttachmentParserMixin
from geotrek.celery import app
from djcelery.models import TaskMeta
from datetime import datetime, timedelta

from .tasks import import_datas
from .forms import ImportDatasetForm

class FormsetMixin(object):
    context_name = None
    formset_class = None

    def form_valid(self, form):
        context = self.get_context_data()
        formset_form = context[self.context_name]

        if formset_form.is_valid():
            response = super(FormsetMixin, self).form_valid(form)
            formset_form.instance = self.object
            formset_form.save()
        else:
            response = self.form_invalid(form)
        return response

    def get_context_data(self, **kwargs):
        context = super(FormsetMixin, self).get_context_data(**kwargs)
        if self.request.POST:
            try:
                context[self.context_name] = self.formset_class(self.request.POST, instance=self.object)
            except ValidationError:
                pass
        else:
            context[self.context_name] = self.formset_class(instance=self.object)
        return context


class PublicOrReadPermMixin(object):
    def get_object(self, queryset=None):
        obj = super(PublicOrReadPermMixin, self).get_object(queryset)
        if not obj.is_public():
            if not self.request.user.is_authenticated():
                raise PermissionDenied
            if not self.request.user.has_perm('%s.read_%s' % (obj._meta.app_label, obj._meta.model_name)):
                raise PermissionDenied
        return obj


class DocumentPublicPDF(PublicOrReadPermMixin, mapentity_views.DocumentConvert):
    # Override login_required
    def dispatch(self, *args, **kwargs):
        return super(mapentity_views.Convert, self).dispatch(*args, **kwargs)

    def source_url(self):
        return self.get_object().get_document_public_url()


class DocumentPublicBase(PublicOrReadPermMixin, mapentity_views.MapEntityDocument):
    template_name_suffix = "_public"

    # Override view_permission_required
    def dispatch(self, *args, **kwargs):
        return super(mapentity_views.MapEntityDocumentBase, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DocumentPublicBase, self).get_context_data(**kwargs)
        modelname = self.get_model()._meta.object_name.lower()
        context['mapimage_ratio'] = settings.EXPORT_MAP_IMAGE_SIZE[modelname]
        return context


class DocumentPublicOdt(DocumentPublicBase):
    with_html_attributes = False

    def render_to_response(self, context, **response_kwargs):
        # Use attachment that overrides document print, if any.
        # And return it as response
        try:
            overriden = self.object.get_attachment_print()
            response = HttpResponse(mimetype='application/vnd.oasis.opendocument.text')
            with open(overriden, 'rb') as f:
                response.write(f.read())
            return response
        except ObjectDoesNotExist:
            pass
        return super(DocumentPublicOdt, self).render_to_response(context, **response_kwargs)


if app_settings['MAPENTITY_WEASYPRINT']:
    DocumentPublic = DocumentPublicBase
else:
    DocumentPublic = DocumentPublicOdt

#
# Concrete views
# ..............................


class JSSettings(mapentity_views.JSSettings):
    """ Override mapentity base settings in order to provide
    Geotrek necessary stuff.
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(JSSettings, self).dispatch(*args, **kwargs)

    def get_context_data(self):
        dictsettings = super(JSSettings, self).get_context_data()
        # Add geotrek map styles
        base_styles = dictsettings['map']['styles']
        for name, override in settings.MAP_STYLES.items():
            merged = base_styles.get(name, {})
            merged.update(override)
            base_styles[name] = merged
        # Add extra stuff (edition, labelling)
        dictsettings['map'].update(
            snap_distance=settings.SNAP_DISTANCE,
            paths_line_marker=settings.PATHS_LINE_MARKER,
            colorspool=settings.COLORS_POOL,
        )
        dictsettings['version'] = __version__
        return dictsettings


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_check_extents(request):
    """
    This view allows administrators to visualize data and configured extents.

    Since it's the first, we implemented this in a very rough way. If there is
    to be more admin tools like this one. Move this to a separate Django app and
    style HTML properly.
    """
    path_extent_native = sql_extent("SELECT ST_Extent(geom) FROM l_t_troncon;")
    path_extent = api_bbox(path_extent_native)
    try:
        dem_extent_native = sql_extent("SELECT ST_Extent(rast::geometry) FROM mnt;")
        dem_extent = api_bbox(dem_extent_native)
    except DatabaseError:  # mnt table missing
        dem_extent_native = None
        dem_extent = None
    tiles_extent_native = settings.SPATIAL_EXTENT
    tiles_extent = api_bbox(tiles_extent_native)
    viewport_native = settings.LEAFLET_CONFIG['SPATIAL_EXTENT']
    viewport = api_bbox(viewport_native, srid=settings.API_SRID)

    def leafletbounds(bbox):
        return [[bbox[1], bbox[0]], [bbox[3], bbox[2]]]

    context = dict(
        path_extent=leafletbounds(path_extent),
        path_extent_native=path_extent_native,
        dem_extent=leafletbounds(dem_extent) if dem_extent else None,
        dem_extent_native=dem_extent_native,
        tiles_extent=leafletbounds(tiles_extent),
        tiles_extent_native=tiles_extent_native,
        viewport=leafletbounds(viewport),
        viewport_native=viewport_native,
        SRID=settings.SRID,
        API_SRID=settings.API_SRID,
    )
    return render(request, 'common/check_extents.html', context)


class UserArgMixin(object):
    def get_form_kwargs(self):
        kwargs = super(UserArgMixin, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


def get_all_subclasses(cls):
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses


@login_required
@user_passes_test(lambda u: u.is_superuser)
def import_view(request):
    """
    Gets the existing declared parsers for the current project.
    This view handles only the file based import parsers.
    """
    choices = []
    try:
        from bulkimport.parsers import *
    except ImportError:
        pass
    
    classes = get_all_subclasses(AttachmentParserMixin)
    for index, cls in enumerate(classes):
        choices.append((index, cls.__name__))
    
    choices = sorted(choices, key=lambda x: x[1])
    
    if request.method == 'POST':
        form = ImportDatasetForm(choices, request.POST, request.FILES)

        if form.is_valid():
            uploaded = request.FILES['file']
            if uploaded.content_type == u'application/zip':
                
                save_dir = '/tmp/geotrek/{}'.format(uploaded.name)
                if not os.path.exists('/tmp/geotrek'):
                    os.mkdir('/tmp/geotrek')
                if not os.path.exists(save_dir):
                    os.mkdir(save_dir)
                with open(save_dir+'/{}'.format(uploaded.name), 'w+') as f:
                    f.write(uploaded.file.read())
                    
                    zfile = ZipFile(f)
                    for name in zfile.namelist():
                        zfile.extract(name, save_dir)
                        if name.endswith('shp'):
                            try:
                                parser = classes[int(form['parser'].value())]
                                async_job = import_datas.delay('/'.join((save_dir, name)), parser.__name__, parser.__module__)
                            except Exception as e:
                                raise e
    else:
        form = ImportDatasetForm(choices)

    return render(request, 'common/import_dataset.html', {
        'form': form
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def import_update_json(request):
    results = []
    threshold = datetime.now() - timedelta(seconds=60)
    for task in TaskMeta.objects.filter(date_done__gte=threshold):
        results.append(
           {
            'id': task.task_id,
            'result': task.result or {'current': 0, 'total': 0},
            'status': task.status
           }
        )

    return HttpResponse(json.dumps(results), content_type="application/json")

