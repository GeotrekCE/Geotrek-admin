from django.utils.translation import ugettext_lazy as _
from django_filters import CharFilter

from .models import Path

from caminae.common.filters import OptionalRangeFilter, StructureRelatedFilterSet


class PathFilter(StructureRelatedFilterSet):
    length = OptionalRangeFilter(label=_('length'))   # TODO: why force ?
    name = CharFilter(label=_('Name'), lookup_type='icontains')
    comments = CharFilter(label=_('Comments'), lookup_type='icontains')

    class Meta(StructureRelatedFilterSet.Meta):
        model = Path
        fields = StructureRelatedFilterSet.Meta.fields + [
                    'length', 'networks', 'trail',
                ]

