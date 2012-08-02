from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_control, cache_page
from django.views.generic.detail import DetailView, BaseDetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.contrib import messages

from djgeojson.views import GeoJSONLayerView

from caminae.authent.decorators import path_manager_required, same_structure_required
from caminae.common.views import JSONListView, JSONResponseMixin, json_django_dumps, HttpJSONResponse
from caminae.maintenance.models import Contractor
from .models import Path
from .forms import PathForm
from .filters import PathFilter
from . import graph as graph_lib



class ElevationProfile(JSONResponseMixin, BaseDetailView):
    """Extract elevation profile from a path and return it as JSON"""

    model = Path

    def get_context_data(self, **kwargs):
        """
        Put elevation profile into response context.
        """
        p = self.get_object()
        return {'profile': p.get_elevation_profile()}


class PathLayer(GeoJSONLayerView):
    model = Path
    fields = ('name', 'valid',)
    precision = 4
    srid = 4326  #TODO: remove and serve in L93
    # simplify = 0.5

    @method_decorator(cache_page(60, cache="fat"))  #TODO: use settings
    @method_decorator(cache_control(max_age=3600*24))   #TODO: use settings
    def dispatch(self, *args, **kwargs):
        return super(PathLayer, self).dispatch(*args, **kwargs)


class PathAjaxList(JSONListView):
    """
    Return path related datas (belonging to the current user) as a JSON
    that will populate a dataTable.

    TODO: provide filters, pagination, sorting etc.
          At the moment everything (except the first listing) is done client side
    """
    model = Path
    # aaData is the key looked up by dataTables
    data_table_name = 'aaData'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PathAjaxList, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        override the most important part of JSONListView... (paginator)
        """
        queryset = kwargs.pop('object_list')
        context = self.update_queryset(queryset)

        return context

    def update_queryset(self, _qs):
        # do not use given queryset for now

        qs = self.model.in_structure.byUser(self.request.user)
        qs = PathFilter(self.request.GET or None, queryset=qs)

        # This must match columns defined in core/path_list.html template

        map_path_pk = []
        data_table_rows = []
        for path in qs:
            data_table_rows.append((
                u'<a href="%s" >%s</a>' % (path.get_detail_url(), path),
                path.date_update,
                path.length,
                path.trail.name if path.trail else _("None")
            ))
            map_path_pk.append(path.pk)

        context = {
            self.data_table_name: data_table_rows,
            'map_path_pk': map_path_pk,
        }

        return context


class PathList(ListView):
    model = Path
    context_object_name = 'path_list'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PathList, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PathList, self).get_context_data(**kwargs)
        context.update(**dict(
            datatables_ajax_url=reverse('core:path_ajax_list'),
            filterform = PathFilter(None, queryset=Path.objects.all())
        ))
        return context


class PathDetail(DetailView):
    model = Path
    context_object_name = 'path'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PathDetail, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PathDetail, self).get_context_data(**kwargs)
        p = self.get_object()
        context['profile'] = p.get_elevation_profile()
        context['can_edit'] = self.request.user.profile.is_path_manager and \
                              p.same_structure(self.request.user)
        return context


class PathCreate(CreateView):
    model = Path
    form_class = PathForm
    context_object_name = 'path'

    @method_decorator(path_manager_required('core:path_list'))
    def dispatch(self, *args, **kwargs):
        return super(PathCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, _("Created"))
        return super(PathCreate, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("You form contains errors"))
        return super(PathCreate, self).form_invalid(form)

    def get_success_url(self):
        return reverse('core:path_detail', kwargs={'pk': self.object.pk})


class PathUpdate(UpdateView):
    model = Path
    form_class = PathForm
    context_object_name = 'path'

    @method_decorator(path_manager_required('core:path_detail'))
    @same_structure_required('core:path_detail')
    def dispatch(self, *args, **kwargs):
        return super(PathUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, _("Saved"))
        return super(PathUpdate, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("You form contains errors"))
        return super(PathUpdate, self).form_invalid(form)

    def get_success_url(self):
        return reverse('core:path_detail', kwargs={'pk': self.object.pk})


class PathDelete(DeleteView):
    model = Path
    context_object_name = 'path'
    success_url = reverse_lazy('core:path_list')

    @method_decorator(path_manager_required('core:path_detail'))
    @same_structure_required('core:path_detail')
    def dispatch(self, *args, **kwargs):
        return super(PathDelete, self).dispatch(*args, **kwargs)


@login_required
def get_graph_json(request):
    def path_modifier(path):
        return { "pk": path.pk, "length": path.length }

    graph = graph_lib.graph_of_qs_optimize(Path.objects.all(), value_modifier=path_modifier)
    json_graph = json_django_dumps(graph)

    return HttpJSONResponse(json_graph)

home = PathList.as_view()
