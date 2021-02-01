from django.db.models import Q
from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from rest_framework import permissions as rest_permissions
from geotrek.authent.decorators import same_structure_required
from geotrek.common.views import DocumentPublic, MarkupPublic
from geotrek.outdoor.filters import SiteFilterSet
from geotrek.outdoor.forms import SiteForm
from geotrek.outdoor.models import Site
from geotrek.outdoor.serializers import SiteSerializer, SiteGeojsonSerializer
from mapentity.views import (MapEntityLayer, MapEntityList, MapEntityJsonList,
                             MapEntityDetail, MapEntityCreate, MapEntityUpdate,
                             MapEntityDelete, MapEntityViewSet)


class SiteLayer(MapEntityLayer):
    properties = ['name']
    queryset = Site.objects.all()


class SiteList(MapEntityList):
    columns = ['id', 'name', 'super_practices', 'lastmod']
    filterform = SiteFilterSet
    queryset = Site.objects.all()


class SiteJsonList(MapEntityJsonList, SiteList):
    pass


class SiteDetail(MapEntityDetail):
    queryset = Site.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super(SiteDetail, self).get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class SiteCreate(MapEntityCreate):
    model = Site
    form_class = SiteForm


class SiteUpdate(MapEntityUpdate):
    queryset = Site.objects.all()
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
        qs = Site.objects.filter(published=True)
        if 'source' in self.request.GET:
            qs = qs.filter(source__name__in=self.request.GET['source'].split(','))
        if 'portal' in self.request.GET:
            qs = qs.filter(Q(portal__name=self.request.GET['portal']) | Q(portal=None))
        return qs.annotate(api_geom=Transform("geom", settings.API_SRID))


class SiteDocumentPublicMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content = self.get_object()

        context['headerimage_ratio'] = settings.EXPORT_HEADER_IMAGE_SIZE['touristiccontent']
        context['object'] = context['content'] = content

        return context


class SiteDocumentPublic(SiteDocumentPublicMixin, DocumentPublic):
    pass


class SiteMarkupPublic(SiteDocumentPublicMixin, MarkupPublic):
    pass
