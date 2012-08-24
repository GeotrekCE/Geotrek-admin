from caminae.mapentity.filters import MapEntityFilterSet

from .models import Trek, POI


class TrekFilter(MapEntityFilterSet):
    class Meta(MapEntityFilterSet.Meta):
        model = Trek
        fields = MapEntityFilterSet.Meta.fields + ['difficulty']


class POIFilter(MapEntityFilterSet):
    class Meta(MapEntityFilterSet.Meta):
        model = POI
        fields = MapEntityFilterSet.Meta.fields + ['type']
