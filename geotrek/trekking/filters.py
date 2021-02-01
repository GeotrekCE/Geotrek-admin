from django.utils.translation import gettext_lazy as _
from mapentity.filters import MapEntityFilterSet
from geotrek.core.filters import TopologyFilter
from geotrek.zoning.filters import ZoningFilterSet

from .models import Trek, POI, Service


class TrekFilterSet(ZoningFilterSet, MapEntityFilterSet):

    class Meta:
        model = Trek
        fields = ['published', 'difficulty', 'duration', 'themes', 'networks',
                  'practice', 'accessibilities', 'route', 'labels',
                  'structure', 'source', 'portal', 'reservation_system']


class POITrekFilter(TopologyFilter):
    queryset = Trek.objects.existing()


class POIFilterSet(ZoningFilterSet, MapEntityFilterSet):
    trek = POITrekFilter(label=_("Trek"), required=False)

    class Meta:
        model = POI
        fields = ['published', 'type', 'trek', 'structure']


class ServiceFilterSet(ZoningFilterSet, MapEntityFilterSet):
    class Meta:
        model = Service
        fields = ['type', 'structure']
