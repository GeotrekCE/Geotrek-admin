from caminae.core.models import TopologyMixin
from caminae.common.filters import StructureRelatedFilterSet
from caminae.mapentity.filters import PolygonFilter
from caminae.mapentity.widgets import GeomWidget

from .models import Intervention, Project


class PolygonTopologyFilter(PolygonFilter):
    def filter(self, qs, value):
        lookup = self.lookup_type
        inner_qs = TopologyMixin.objects.filter(**{'geom__%s' % lookup: value})
        return qs.filter(**{'%s__in' % self.name: inner_qs})


class InterventionFilter(StructureRelatedFilterSet):
    bbox = PolygonTopologyFilter(name='topology', lookup_type='intersects', widget=GeomWidget)
    class Meta(StructureRelatedFilterSet.Meta):
        model = Intervention
        fields = StructureRelatedFilterSet.Meta.fields + ['status']


class ProjectFilter(StructureRelatedFilterSet):
    class Meta(StructureRelatedFilterSet.Meta):
        model = Project
        fields = StructureRelatedFilterSet.Meta.fields + ['begin_year', 'end_year']
        exclude = ('bbox',)  # Project has no geom db field
