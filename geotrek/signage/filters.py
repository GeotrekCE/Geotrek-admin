from django_filters import CharFilter
from django.utils.translation import ugettext_lazy as _

from geotrek.core.models import Topology
from geotrek.common.filters import StructureRelatedFilterSet, ValueFilter
from geotrek.maintenance.filters import InterventionYearTargetFilter
from geotrek.signage.models import Signage, Blade
from geotrek.signage.widgets import SignageYearSelect, SignageImplantationYearSelect, SignageStructureSelect

from mapentity.filters import MapEntityFilterSet, PolygonFilter


class PolygonTopologyFilter(PolygonFilter):
    def filter(self, qs, value):
        if not value:
            return qs
        lookup = self.lookup_expr
        inner_qs = Topology.objects.filter(**{'geom__%s' % lookup: value})
        return qs.filter(**{'%s__in' % self.field_name: inner_qs})


class SignageStructureFilter(ValueFilter):
    def filter(self, qs, value):
        if not value or value == -1:
            return qs
        return qs.filter(**{'signage__structure__name': value})


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


class BladeFilterSet(MapEntityFilterSet):
    bbox = PolygonTopologyFilter(field_name='topology', lookup_expr='intersects')
    structure = SignageStructureFilter(widget=SignageStructureSelect)

    def __init__(self, *args, **kwargs):
        super(BladeFilterSet, self).__init__(*args, **kwargs)

    class Meta(MapEntityFilterSet.Meta):
        model = Blade
        fields = MapEntityFilterSet.Meta.fields + ['structure', 'number', 'direction', 'type', 'color', 'condition']
