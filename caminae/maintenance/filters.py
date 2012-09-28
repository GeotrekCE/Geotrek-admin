from django.forms.widgets import Select
from django.utils.translation import ugettext_lazy as _

from caminae.core.models import TopologyMixin
from caminae.common.filters import StructureRelatedFilterSet
from caminae.mapentity.filters import PolygonFilter, PythonPolygonFilter, YearFilter, YearBetweenFilter
from caminae.mapentity.widgets import GeomWidget

from caminae.land.filters import (
        TopoFilterPhysicalType, TopoFilterLandType,
        TopoFilterCompetenceEdge, TopoFilterSignageManagementEdge, TopoFilterWorkManagementEdge
)

from .models import Intervention, Project


class PolygonTopologyFilter(PolygonFilter):
    def filter(self, qs, value):
        if not value:
            return qs
        lookup = self.lookup_type
        inner_qs = TopologyMixin.objects.filter(**{'geom__%s' % lookup: value})
        return qs.filter(**{'%s__in' % self.name: inner_qs})


class InterventionFilter(StructureRelatedFilterSet):
    bbox = PolygonTopologyFilter(name='topology', lookup_type='intersects', widget=GeomWidget)
    year = YearFilter(name='date', widget=Select, label=_(u"Year"))

    physical_type = TopoFilterPhysicalType(label=_('Physical type'), required=False)
    land_type = TopoFilterLandType(label=_('Land type'), required=False)

    competence = TopoFilterCompetenceEdge(label=_('Competence'), required=False)
    signage = TopoFilterSignageManagementEdge(label=_('Signage management'), required=False)
    work = TopoFilterWorkManagementEdge(label=_('Work management'), required=False)

    class Meta(StructureRelatedFilterSet.Meta):
        model = Intervention
        fields = StructureRelatedFilterSet.Meta.fields + [
            'status', 'type', 'stake', # user
        ]


class ProjectFilter(StructureRelatedFilterSet):
    bbox = PythonPolygonFilter(name='geom', widget=GeomWidget)
    in_year = YearBetweenFilter(name=('begin_year', 'end_year'), widget=Select,
                    label=_(u"Year of activity"))

    physical_type = TopoFilterPhysicalType(label=_('Physical type'), required=False)
    land_type = TopoFilterLandType(label=_('Land type'), required=False)

    competence = TopoFilterCompetenceEdge(label=_('Competence'), required=False)
    signage = TopoFilterSignageManagementEdge(label=_('Signage management'), required=False)
    work = TopoFilterWorkManagementEdge(label=_('Work management'), required=False)

    class Meta(StructureRelatedFilterSet.Meta):
        model = Project
        fields = StructureRelatedFilterSet.Meta.fields

