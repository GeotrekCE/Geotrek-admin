from caminae.land.filters import EdgeFilterSet

from .models import Trek, POI


class TrekFilter(EdgeFilterSet):
    class Meta(EdgeFilterSet.Meta):
        model = Trek
        fields = EdgeFilterSet.Meta.fields + ['difficulty', 'duration', 'themes', 'networks', 'usages', 'route', 'is_park_centered']


class POIFilter(EdgeFilterSet):
    class Meta(EdgeFilterSet.Meta):
        model = POI
        fields = EdgeFilterSet.Meta.fields + ['type']
