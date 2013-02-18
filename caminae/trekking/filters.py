from django.utils.translation import ugettext_lazy as _
from caminae.land.filters import TopoFilter, EdgeFilterSet

from .models import Trek, POI


class TrekFilter(EdgeFilterSet):
    class Meta(EdgeFilterSet.Meta):
        model = Trek
        fields = EdgeFilterSet.Meta.fields + ['difficulty', 'duration', 'themes', 'networks', 'usages', 'route', 'is_park_centered']


class POITrekFilter(TopoFilter):
    queryset = Trek.objects.existing()


class POIFilter(EdgeFilterSet):
    trek = POITrekFilter(label=_("Trek"), required=False)

    class Meta(EdgeFilterSet.Meta):
        model = POI
        fields = EdgeFilterSet.Meta.fields + ['type', 'trek']
