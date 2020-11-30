from geotrek.authent.decorators import same_structure_required
from geotrek.core.views import CreateFromTopologyMixin
from geotrek.outdoor.filters import SiteFilterSet
from geotrek.outdoor.forms import SiteForm
from geotrek.outdoor.models import Site
from mapentity.views import (MapEntityLayer, MapEntityList, MapEntityJsonList,
                             MapEntityDetail, MapEntityCreate, MapEntityUpdate,
                             MapEntityDelete)


class SiteLayer(MapEntityLayer):
    properties = ['name']
    queryset = Site.objects.existing()


class SiteList(MapEntityList):
    columns = ['id', 'name']
    filterform = SiteFilterSet
    queryset = Site.objects.existing()


class SiteJsonList(MapEntityJsonList, SiteList):
    pass


class SiteDetail(MapEntityDetail):
    queryset = Site.objects.existing()

    def get_context_data(self, *args, **kwargs):
        context = super(SiteDetail, self).get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class SiteCreate(CreateFromTopologyMixin, MapEntityCreate):
    model = Site
    form_class = SiteForm


class SiteUpdate(MapEntityUpdate):
    queryset = Site.objects.existing()
    form_class = SiteForm

    @same_structure_required('outdoor:site_detail')
    def dispatch(self, *args, **kwargs):
        return super(SiteUpdate, self).dispatch(*args, **kwargs)


class SiteDelete(MapEntityDelete):
    model = Site

    @same_structure_required('outdoor:site_detail')
    def dispatch(self, *args, **kwargs):
        return super(SiteDelete, self).dispatch(*args, **kwargs)
