from django.utils.translation import ugettext_lazy as _

from .models import Path

from caminae.common.filters import OptionalRangeFilter, StructureRelatedFilterSet


class PathFilter(StructureRelatedFilterSet):
    length = OptionalRangeFilter(label=_('length'))   # TODO: why force ?

    class Meta(StructureRelatedFilterSet.Meta):
        model = Path
        fields = StructureRelatedFilterSet.Meta.fields + [
                    'length', 'name', 'networks', 'comments', 'trail',
                ]


