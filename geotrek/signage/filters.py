from django.utils.translation import ugettext_lazy as _
from django_filters import CharFilter

from geotrek.common.filters import StructureRelatedFilterSet, YearFilter, ValueFilter
from geotrek.signage.widgets import SignageYearSelect, SignageImplantationYearSelect
from .models import Signage, Blade
from mapentity.filters import PolygonFilter, PythonPolygonFilter
from geotrek.maintenance.filters import PolygonTopologyFilter


class SignageFilterSet(StructureRelatedFilterSet):
    name = CharFilter(label=_('Name'), lookup_expr='icontains')
    description = CharFilter(label=_('Description'), lookup_expr='icontains')
    implantation_year = ValueFilter(name='implantation_year',
                                    widget=SignageImplantationYearSelect)
    intervention_year = YearFilter(name='interventions_set__date',
                                   widget=SignageYearSelect)

    def __init__(self, *args, **kwargs):
        super(SignageFilterSet, self).__init__(*args, **kwargs)

    class Meta(StructureRelatedFilterSet.Meta):
        model = Signage
        fields = StructureRelatedFilterSet.Meta.fields + ['type', 'condition', 'implantation_year', 'intervention_year',
                                                          'published', 'code', 'printed_elevation', 'manager',
                                                          'sealing']


class BladeFilterSet(StructureRelatedFilterSet):
    bbox = PolygonTopologyFilter(name='topology', lookup_expr='intersects')
    number = CharFilter(label=_('Number'), lookup_expr='icontains')
    direction = CharFilter(label=_('Direction'), lookup_expr='icontains')
    color = CharFilter(label=_('Color'), lookup_expr='icontains')

    def __init__(self, *args, **kwargs):
        super(BladeFilterSet, self).__init__(*args, **kwargs)

    class Meta(StructureRelatedFilterSet.Meta):
        model = Blade
        fields = StructureRelatedFilterSet.Meta.fields + ['number', 'direction', 'type', 'color', 'condition']
