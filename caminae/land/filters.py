# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from django_filters import ModelChoiceFilter

from caminae.core.models import Topology, Path
from caminae.common.models import Organism
from caminae.common.filters import StructureRelatedFilterSet
from caminae.mapentity.filters import MapEntityFilterSet


from .models import (
    CompetenceEdge, LandEdge, LandType, PhysicalEdge, PhysicalType,
    SignageManagementEdge, WorkManagementEdge,
    City, District
)


class PhysicalEdgeFilter(MapEntityFilterSet):
    class Meta(MapEntityFilterSet.Meta):
        model = PhysicalEdge
        fields = MapEntityFilterSet.Meta.fields + ['physical_type']


class LandEdgeFilter(StructureRelatedFilterSet):
    class Meta(MapEntityFilterSet.Meta):
        model = LandEdge
        fields = MapEntityFilterSet.Meta.fields + ['land_type']


class OrganismFilter(MapEntityFilterSet):
    class Meta(MapEntityFilterSet.Meta):
        fields = MapEntityFilterSet.Meta.fields + ['organization']


class CompetenceEdgeFilter(OrganismFilter):
    class Meta(OrganismFilter.Meta):
        model = CompetenceEdge


class WorkManagementEdgeFilter(OrganismFilter):
    class Meta(OrganismFilter.Meta):
        model = WorkManagementEdge


class SignageManagementEdgeFilter(OrganismFilter):
    class Meta(OrganismFilter.Meta):
        model = SignageManagementEdge


"""

    Welcome in the land of complexity.

    (also known as over-engineering)

"""

def filter(qs, edges):
    """
    This piece of code was moved from core, and should be rewritten nicely
    with managers : TODO !
    """
    # TODO: this is wrong, land should not depend on maintenance
    import caminae.maintenance as maintenance

    overlapping = Topology.overlapping(edges)

    # In case, we filter on paths
    if qs.model == Path:
        paths = []
        for o in overlapping:
            paths.extend(o.paths.all())
        return qs.filter(pk__in=[ path.pk for path in set(paths) ])

    # TODO: This is (amazingly) ugly in terms of OOP. Should refactor overlapping()
    elif issubclass(qs.model, maintenance.models.Intervention):
        return qs.filter(topology__in=[ topo.pk for topo in overlapping ])
    elif issubclass(qs.model, maintenance.models.Project):
        # Find all interventions overlapping those edges
        interventions = filter(maintenance.models.Intervention.objects.existing()\
                                                              .select_related(depth=1)\
                                                              .filter(project__in=qs), 
                               edges)
        # Return only the projects concerned by the interventions
        projects = []
        for intervention in interventions:
            projects.append(intervention.project.pk)
        return qs.filter(pk__in=set(projects))

    else:
        assert issubclass(qs.model, Topology), "%s is not a Topology as expected" % qs.model
        return qs.filter(pk__in=[ topo.pk for topo in overlapping ])



class TopoFilter(ModelChoiceFilter):

    model = None
    queryset = None

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', self.get_queryset())
        super(TopoFilter, self).__init__(*args, **kwargs)
        self.field.widget.attrs['class'] = self.field.widget.attrs.get('class', '') + ' topology-filter'

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        return self.model.objects.all()

    def filter(self, qs, value):
        """Overrides parent filter() method completely."""
        if not value:
            return qs
        if issubclass(value.__class__, Topology):
            edges = Topology.objects.filter(pk=value.pk)
        else:
            edges = self.value_to_edges(value)
        return filter(qs, edges)

    def value_to_edges(self, value):
        raise NotImplementedError


class TopoFilterPhysicalType(TopoFilter):
    model = PhysicalType

    def value_to_edges(self, value):
        return value.physicaledge_set.all()


class TopoFilterLandType(TopoFilter):
    model = LandType

    def value_to_edges(self, value):
        return value.landedge_set.all()


class TopoFilterCity(TopoFilter):
    model = City

    def value_to_edges(self, value):
        return value.cityedge_set.all()


class TopoFilterDistrict(TopoFilter):
    model = District

    def value_to_edges(self, value):
        return value.districtedge_set.all()


class TopoFilterCompetenceEdge(TopoFilter):
    model = Organism

    def value_to_edges(self, value):
        return value.competenceedge_set.select_related(depth=1).all()


class TopoFilterSignageManagementEdge(TopoFilter):
    model = Organism

    def value_to_edges(self, value):
        return value.signagemanagementedge_set.select_related(depth=1).all()


class TopoFilterWorkManagementEdge(TopoFilter):
    model = Organism

    def value_to_edges(self, value):
        return value.workmanagementedge_set.select_related(depth=1).all()


class EdgeFilterSet(MapEntityFilterSet):
    city = TopoFilterCity(label=_('City'), required=False)
    district = TopoFilterDistrict(label=('District'), required=False)

    physical_type = TopoFilterPhysicalType(label=_('Physical type'), required=False)
    land_type = TopoFilterLandType(label=_('Land type'), required=False)

    competence = TopoFilterCompetenceEdge(label=_('Competence'), required=False)
    signage = TopoFilterSignageManagementEdge(label=_('Signage management'), required=False)
    work = TopoFilterWorkManagementEdge(label=_('Work management'), required=False)

    class Meta(MapEntityFilterSet.Meta):
        fields = MapEntityFilterSet.Meta.fields


class EdgeStructureRelatedFilterSet(StructureRelatedFilterSet):
    city = TopoFilterCity(label=_('City'), required=False)
    district = TopoFilterDistrict(label=('District'), required=False)

    physical_type = TopoFilterPhysicalType(label=_('Physical type'), required=False)
    land_type = TopoFilterLandType(label=_('Land type'), required=False)

    competence = TopoFilterCompetenceEdge(label=_('Competence'), required=False)
    signage = TopoFilterSignageManagementEdge(label=_('Signage management'), required=False)
    work = TopoFilterWorkManagementEdge(label=_('Work management'), required=False)

    class Meta(StructureRelatedFilterSet.Meta):
        fields = StructureRelatedFilterSet.Meta.fields
