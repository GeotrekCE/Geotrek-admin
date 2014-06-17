from django.utils.translation import ugettext_lazy as _
from mapentity.filters import MapEntityFilterSet
from geotrek.core.filters import TopologyFilter

from .models import Trek, POI


class TrekFilterSet(MapEntityFilterSet):
    class Meta:
        model = Trek
        fields = ['published', 'difficulty', 'duration', 'themes', 'networks',
                  'usages', 'route', 'is_park_centered']


class POITrekFilter(TopologyFilter):
    queryset = Trek.objects.existing()


class POIFilterSet(MapEntityFilterSet):
    trek = POITrekFilter(label=_("Trek"), required=False)

    class Meta:
        model = POI
        fields = ['type', 'trek']
