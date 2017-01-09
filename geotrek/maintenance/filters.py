from django.utils.translation import ugettext_lazy as _

from mapentity.filters import PolygonFilter, PythonPolygonFilter

from geotrek.core.models import Topology
from geotrek.common.filters import (
    StructureRelatedFilterSet, YearFilter, YearBetweenFilter)
from geotrek.common.widgets import YearSelect

from .models import Intervention, Project


class PolygonTopologyFilter(PolygonFilter):
    def filter(self, qs, value):
        if not value:
            return qs
        lookup = self.lookup_expr
        inner_qs = Topology.objects.filter(**{'geom__%s' % lookup: value})
        return qs.filter(**{'%s__in' % self.name: inner_qs})


class InterventionYearSelect(YearSelect):
    label = _(u"Year")

    def get_years(self):
        return Intervention.objects.all_years()


class InterventionFilterSet(StructureRelatedFilterSet):
    bbox = PolygonTopologyFilter(name='topology', lookup_expr='intersects')
    year = YearFilter(name='date',
                      widget=InterventionYearSelect,
                      label=_(u"Year"))

    class Meta(StructureRelatedFilterSet.Meta):
        model = Intervention
        fields = StructureRelatedFilterSet.Meta.fields + [
            'status', 'type', 'stake', 'subcontracting', 'project'
        ]


class ProjectYearSelect(YearSelect):
    label = _(u"Year of activity")

    def get_years(self):
        return Project.objects.all_years()


class ProjectFilterSet(StructureRelatedFilterSet):
    bbox = PythonPolygonFilter(name='geom')
    in_year = YearBetweenFilter(name=('begin_year', 'end_year'),
                                widget=ProjectYearSelect,
                                label=_(u"Year of activity"))

    class Meta(StructureRelatedFilterSet.Meta):
        model = Project
        fields = StructureRelatedFilterSet.Meta.fields + [
            'in_year', 'type', 'domain', 'contractors', 'project_owner',
            'project_manager', 'founders'
        ]
