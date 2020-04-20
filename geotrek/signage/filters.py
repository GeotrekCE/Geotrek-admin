from django_filters import CharFilter
from django.utils.translation import ugettext_lazy as _

from geotrek.core.models import Topology
from geotrek.common.filters import StructureRelatedFilterSet, ValueFilter
from geotrek.maintenance.filters import InterventionYearTargetFilter
from geotrek.signage.models import Signage, Blade
from geotrek.signage.widgets import SignageYearSelect, SignageImplantationYearSelect

from mapentity.filters import PolygonFilter


class PolygonTopologyFilter(PolygonFilter):
    def filter(self, qs, value):
        if not value:
            return qs
        lookup = self.lookup_expr
        inner_qs = Topology.objects.filter(**{'geom__%s' % lookup: value})
        return qs.filter(**{'%s__in' % self.field_name: inner_qs})


class SignageFilterSet(StructureRelatedFilterSet):
    name = CharFilter(label=_('Name'), lookup_expr='icontains')
    description = CharFilter(label=_('Description'), lookup_expr='icontains')
    implantation_year = ValueFilter(field_name='implantation_year',
                                    widget=SignageImplantationYearSelect)
    intervention_year = InterventionYearTargetFilter(widget=SignageYearSelect)

    def __init__(self, *args, **kwargs):
        super(SignageFilterSet, self).__init__(*args, **kwargs)

    class Meta(StructureRelatedFilterSet.Meta):
        model = Signage
        fields = StructureRelatedFilterSet.Meta.fields + ['type', 'condition', 'implantation_year', 'intervention_year',
                                                          'published', 'code', 'printed_elevation', 'manager',
                                                          'sealing']


class BladeFilterSet(StructureRelatedFilterSet):
    bbox = PolygonTopologyFilter(field_name='topology', lookup_expr='intersects')

    def __init__(self, *args, **kwargs):
        super(BladeFilterSet, self).__init__(*args, **kwargs)

    class Meta(StructureRelatedFilterSet.Meta):
        model = Blade
        fields = StructureRelatedFilterSet.Meta.fields + ['number', 'direction', 'type', 'color', 'condition']
