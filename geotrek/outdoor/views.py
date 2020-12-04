from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from rest_framework import permissions as rest_permissions
from geotrek.authent.decorators import same_structure_required
from geotrek.outdoor.filters import SiteFilterSet
from geotrek.outdoor.forms import SiteForm
from geotrek.outdoor.models import Site
from geotrek.outdoor.serializers import SiteSerializer, SiteGeojsonSerializer
from mapentity.views import (MapEntityLayer, MapEntityList, MapEntityJsonList,
                             MapEntityDetail, MapEntityCreate, MapEntityUpdate,
                             MapEntityDelete, MapEntityViewSet)


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


class SiteCreate(MapEntityCreate):
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


class SiteViewSet(MapEntityViewSet):
    model = Site
    serializer_class = SiteSerializer
    geojson_serializer_class = SiteGeojsonSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        qs = Site.objects.existing()
        qs = qs.annotate(api_geom=Transform("geom", settings.API_SRID))
        return qs
