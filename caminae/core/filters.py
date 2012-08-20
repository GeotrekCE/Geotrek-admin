from .models import Path

from caminae.common.filters import OptionalRangeFilter, StructureRelatedFilterSet


class PathFilter(StructureRelatedFilterSet):
    length = OptionalRangeFilter()

    class Meta(StructureRelatedFilterSet.Meta):
        model = Path
        fields = StructureRelatedFilterSet.Meta.fields + ['length',]
