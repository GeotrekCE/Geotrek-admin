from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_control, cache_page
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from djgeojson.views import GeoJSONLayerView

from caminae.authent.decorators import path_manager_required, same_structure_required
from caminae.common.views import JSONListView
from caminae.maintenance.models import Contractor
from .models import Path



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
    context_object_name = 'aaData'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PathAjaxList, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        override the most important part of JSONListView... (paginator)
        """
        queryset = kwargs.pop('object_list')
        new_queryset = self.update_queryset(queryset)

        context = { self.context_object_name: new_queryset }
        return context

    def update_queryset(self, queryset):
        # do not use given queryset for now
        user_path_queryset = self.model.in_structure.byUser(self.request.user)

        # This must match columns defined in core/path_list.html template
        return [(
            u'<a href="%s" >%s</a>' % (path.get_detail_url(), path),
            path.date_update,
            path.length,
            path.trail.name if path.trail else _("None")
        ) for path in user_path_queryset ]


class PathList(ListView):
    model = Path
    context_object_name = 'path_list'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PathList, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PathList, self).get_context_data(**kwargs)
        # Temporary during Sprint1
        context.update(**dict(
            contractors=Contractor.forUser(self.request.user),
            all_contractors=Contractor.objects.all(),
            datatables_ajax_url=reverse('core:path_ajax_list'),
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

        # NOTE: Quick and dirty. Should be replaced soon by a JSON view with
        # nice graph visualization
        import math
        def distance3D(a, b):
            return math.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2 + (b[2] - a[2])**2)
        p = self.get_object()
        profile = []
        for i in range(1, len(p.geom.coords)):
            profile.append((distance3D(p.geom.coords[i-1], p.geom.coords[i]), p.geom.coords[i][2]))
        context['profile'] = profile

        return context


class PathCreate(CreateView):
    model = Path
    context_object_name = 'path'

    @method_decorator(path_manager_required('core:path_list'))
    def dispatch(self, *args, **kwargs):
        return super(PathCreate, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('core:path_detail', kwargs={'pk': self.object.pk})


class PathUpdate(UpdateView):
    model = Path
    context_object_name = 'path'

    @method_decorator(path_manager_required('core:path_detail'))
    @same_structure_required('core:path_detail')
    def dispatch(self, *args, **kwargs):
        return super(PathUpdate, self).dispatch(*args, **kwargs)

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


home = PathList.as_view()
