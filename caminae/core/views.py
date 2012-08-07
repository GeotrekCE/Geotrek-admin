import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.timezone import utc
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic.detail import DetailView, BaseDetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.contrib import messages
from django.views.decorators.http import condition
from django.core.cache import get_cache

from djgeojson.views import GeoJSONLayerView

from caminae.authent.decorators import path_manager_required, same_structure_required
from caminae.common.views import JSONResponseMixin, json_django_dumps, HttpJSONResponse
from .models import Path
from .forms import PathForm
from .filters import PathFilter
from . import graph as graph_lib


def latest_updated_path_date(*args, **kwargs):
    try:
        return Path.objects.latest("date_update").date_update
    except Path.DoesNotExist:
        return None


class MapEntityLayer(GeoJSONLayerView):
    srid = settings.MAP_SRID

    @method_decorator(condition(last_modified_func=latest_updated_path_date))
    def dispatch(self, *args, **kwargs):
        return super(MapEntityLayer, self).dispatch(*args, **kwargs)
 
    def render_to_response(self, context, **response_kwargs):
        cache = get_cache('fat')
        key = 'path_layer_json'

        result = cache.get(key)

        latest = latest_updated_path_date()

        if result and latest:
            cache_latest, content = result
            # still valid
            if cache_latest >= latest:
                return self.response_class(content=content, **response_kwargs)

        response = super(MapEntityLayer, self).render_to_response(context, **response_kwargs)
        cache.set(key, (latest, response.content))
        return response


class MapEntityList(ListView):
    """
    
    A generic view list web page.
    
    model = None
    filterform = None
    columns = []
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MapEntityList, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MapEntityList, self).get_context_data(**kwargs)
        context.update(**dict(
            model=self.model,
            datatables_ajax_url=self.model.get_jsonlist_url(),
            filterform=self.filterform(None, queryset=self.get_queryset()),
            columns=self.columns,
            generic_detail_url=self.model.get_generic_detail_url(),
        ))
        return context


class MapEntityJsonList(JSONResponseMixin, MapEntityList):
    """
    Return path related datas (belonging to the current user) as a JSON
    that will populate a dataTable.

    TODO: provide filters, pagination, sorting etc.
          At the moment everything (except the first listing) is done client side
    """
    # aaData is the key looked up by dataTables
    data_table_name = 'aaData'

    def get_context_data(self, **kwargs):
        """
        override the most important part of JSONListView... (paginator)
        """
        queryset = kwargs.pop('object_list')
        # Filter queryset from possible serialized form
        queryset = self.filterform(self.request.GET or None, queryset=queryset)
        # Build list with fields
        map_obj_pk = []
        data_table_rows = []
        for obj in queryset:
            columns = []
            for field in self.columns:
                columns.append(getattr(obj, field + '_display', getattr(obj, field)))
            data_table_rows.append(columns)
            map_obj_pk.append(obj.pk)

        context = {
            self.data_table_name: data_table_rows,
            'map_obj_pk': map_obj_pk,
        }
        return context


class MapEntityDetail(DetailView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MapEntityDetail, self).dispatch(*args, **kwargs)

    def can_edit(self):
        return False

    def get_context_data(self, **kwargs):
        context = super(MapEntityDetail, self).get_context_data(**kwargs)
        context['can_edit'] = self.can_edit()
        return context


class MapEntityCreate(CreateView):
    def form_valid(self, form):
        messages.success(self.request, _("Created"))
        return super(MapEntityCreate, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Your form contains errors"))
        return super(MapEntityCreate, self).form_invalid(form)

    def get_success_url(self):
        return self.get_object().get_detail_url()

    def get_context_data(self, **kwargs):
        context = super(MapEntityCreate, self).get_context_data(**kwargs)
        name = self.model._meta.verbose_name
        if hasattr(name, '_proxy____args'):
            name = name._proxy____args[0]  # untranslated
        context['object_type'] = name.lower()
        # Whole "add" phrase translatable, but not catched  by makemessages
        context['add_msg'] = _("Add a new %s" % context['object_type'])
        return context


class MapEntityUpdate(UpdateView):
    def form_valid(self, form):
        messages.success(self.request, _("Saved"))
        return super(MapEntityUpdate, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Your form contains errors"))
        return super(MapEntityUpdate, self).form_invalid(form)

    def get_success_url(self):
        return self.get_object().get_detail_url()


class MapEntityDelete(DeleteView):
    def get_success_url(self):
        return self.model.get_list_url()


"""

    Concrete MapEntity views

"""

class PathLayer(MapEntityLayer):
    model = Path


class PathList(MapEntityList):
    model = Path
    filterform = PathFilter
    columns = ['name', 'date_update', 'length', 'trail']


class PathJsonList(MapEntityJsonList, PathList):
    pass


class PathDetail(MapEntityDetail):
    model = Path

    def can_edit(self):
        return self.request.user.profile.is_path_manager and \
               self.get_object().same_structure(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(PathDetail, self).get_context_data(**kwargs)
        context['profile'] = self.get_object().get_elevation_profile()
        return context


class PathCreate(MapEntityCreate):
    model = Path
    form_class = PathForm

    @method_decorator(path_manager_required('core:path_list'))
    def dispatch(self, *args, **kwargs):
        return super(PathCreate, self).dispatch(*args, **kwargs)


class PathUpdate(MapEntityUpdate):
    model = Path
    form_class = PathForm

    @method_decorator(path_manager_required('core:path_detail'))
    @same_structure_required('core:path_detail')
    def dispatch(self, *args, **kwargs):
        return super(PathUpdate, self).dispatch(*args, **kwargs)


class PathDelete(MapEntityDelete):
    model = Path

    @method_decorator(path_manager_required('core:path_detail'))
    @same_structure_required('core:path_detail')
    def dispatch(self, *args, **kwargs):
        return super(PathDelete, self).dispatch(*args, **kwargs)


class ElevationProfile(JSONResponseMixin, BaseDetailView):
    """Extract elevation profile from a path and return it as JSON"""

    model = Path

    def get_context_data(self, **kwargs):
        """
        Put elevation profile into response context.
        """
        p = self.get_object()
        return {'profile': p.get_elevation_profile()}


@login_required
def get_graph_json(request):
    def path_modifier(path):
        return { "pk": path.pk, "length": path.length }

    graph = graph_lib.graph_of_qs_optimize(Path.objects.all(), value_modifier=path_modifier)
    json_graph = json_django_dumps(graph)

    return HttpJSONResponse(json_graph)


home = PathList.as_view()
