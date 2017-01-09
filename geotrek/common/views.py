# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.decorators import method_decorator
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.utils import DatabaseError
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from mapentity.helpers import api_bbox
from mapentity import views as mapentity_views

from geotrek.celery import app as celery_app
from geotrek.common.utils import sql_extent
from geotrek import __version__

from rest_framework import permissions as rest_permissions, viewsets

# async data imports
import ast
import os
import json
import redis
from zipfile import ZipFile
from djcelery.models import TaskMeta
from datetime import datetime, timedelta

from .utils.import_celery import create_tmp_destination, discover_available_parsers

from .tasks import import_datas, import_datas_from_web
from .forms import ImportDatasetForm, ImportDatasetFormWithFile
from .models import Theme
from .serializers import ThemeSerializer


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
                context[self.context_name] = self.formset_class(
                    self.request.POST, instance=self.object)
            except ValidationError:
                pass
        else:
            context[self.context_name] = self.formset_class(
                instance=self.object)
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


class DocumentPublic(PublicOrReadPermMixin, mapentity_views.MapEntityDocumentWeasyprint):
    template_name_suffix = "_public"

    # Override view_permission_required
    def dispatch(self, *args, **kwargs):
        return super(mapentity_views.MapEntityDocumentBase, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DocumentPublic, self).get_context_data(**kwargs)
        modelname = self.get_model()._meta.object_name.lower()
        context['mapimage_ratio'] = settings.EXPORT_MAP_IMAGE_SIZE[modelname]
        return context

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
        dem_extent_native = sql_extent(
            "SELECT ST_Extent(rast::geometry) FROM mnt;")
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


def import_file(uploaded, parser):
    destination_dir, destination_file = create_tmp_destination(uploaded.name)
    with open(destination_file, 'w+') as f:
        f.write(uploaded.file.read())
        zfile = ZipFile(f)
        for name in zfile.namelist():
            try:
                zfile.extract(
                    name, os.path.dirname(os.path.realpath(f.name)))
            except Exception:
                raise

            if name.endswith('shp'):
                import_datas.delay(parser.__name__, '/'.join((destination_dir, name)), parser.__module__)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def import_view(request):
    """
    Gets the existing declared parsers for the current project.
    This view handles only the file based import parsers.
    """
    choices = []
    choices_url = []
    render_dict = {}

    choices, choices_url, classes = discover_available_parsers()

    form = ImportDatasetFormWithFile(choices, prefix="with-file")
    form_without_file = ImportDatasetForm(
        choices_url, prefix="without-file")

    if request.method == 'POST':
        if 'upload-file' in request.POST:
            form = ImportDatasetFormWithFile(
                choices, request.POST, request.FILES, prefix="with-file")

            if form.is_valid():
                uploaded = request.FILES['with-file-zipfile']
                parser = classes[int(form['parser'].value())]
                import_file(uploaded, parser)

        if 'import-web' in request.POST:
            form_without_file = ImportDatasetForm(
                choices_url, request.POST, prefix="without-file")

            if form_without_file.is_valid():
                parser = classes[int(form_without_file['parser'].value())]
                import_datas_from_web.delay(
                    parser.__name__, parser.__module__
                )

    # Hide second form if parser has no web based imports.
    render_dict['form'] = form
    if choices_url:
        render_dict['form_without_file'] = form_without_file

    return render(request, 'common/import_dataset.html', render_dict)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def import_update_json(request):
    results = []
    threshold = datetime.now() - timedelta(seconds=60)
    for task in TaskMeta.objects.filter(date_done__gte=threshold).order_by('date_done'):
        if hasattr(task, 'result') and task.result.get('name', '').startswith('geotrek.common'):
            results.append(
                {
                    'id': task.task_id,
                    'result': task.result or {'current': 0, 'total': 0},
                    'status': task.status
                }
            )
    i = celery_app.control.inspect([u'celery@geotrek'])
    try:
        reserved = i.reserved()
    except redis.exceptions.ConnectionError:
        reserved = None
    tasks = [] if reserved is None else reversed(reserved[u'celery@geotrek'])
    for task in tasks:
        if task['name'].startswith('geotrek.common'):
            args = ast.literal_eval(task['args'])
            if task['name'].endswith('import-file'):
                filename = os.path.basename(args[1])
            else:
                filename = _("Import from web.")
            results.append(
                {
                    'id': task['id'],
                    'result': {
                        'parser': args[0],
                        'filename': filename,
                        'current': 0,
                        'total': 0
                    },
                    'status': 'PENDING',
                }
            )

    return HttpResponse(json.dumps(results), content_type="application/json")


class ThemeViewSet(viewsets.ModelViewSet):
    model = Theme
    queryset = Theme.objects.all()
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]
    serializer_class = ThemeSerializer

    def get_queryset(self):
        qs = super(ThemeViewSet, self).get_queryset()
        return qs.order_by('id')
