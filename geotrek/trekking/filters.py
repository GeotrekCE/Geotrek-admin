from django.utils.translation import ugettext_lazy as _
from mapentity.filters import MapEntityFilterSet
from geotrek.core.filters import TopologyFilter

from .models import Trek, POI, Service


class TrekFilterSet(MapEntityFilterSet):
    class Meta:
        model = Trek
        fields = ['published', 'difficulty', 'duration', 'themes', 'networks',
                  'practice', 'accessibilities', 'route', 'is_park_centered',
                  'structure', 'source', 'portal']


class POITrekFilter(TopologyFilter):
    queryset = Trek.objects.existing()


class POIFilterSet(MapEntityFilterSet):
    trek = POITrekFilter(label=_("Trek"), required=False)

    class Meta:
        model = POI
        fields = ['published', 'type', 'trek', 'structure']


class ServiceFilterSet(MapEntityFilterSet):
    class Meta:
        model = Service
        fields = ['type', 'structure']
