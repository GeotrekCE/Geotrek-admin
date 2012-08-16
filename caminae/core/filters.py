from .models import Path

from caminae.mapentity.filters import MapEntityFilterSet
from caminae.common.filters import OptionalRangeFilter


class PathFilter(MapEntityFilterSet):
    length = OptionalRangeFilter()

    class Meta(MapEntityFilterSet.Meta):
        model = Path
        fields = MapEntityFilterSet.Meta.fields + ['length',]
