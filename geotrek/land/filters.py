# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from mapentity.filters import MapEntityFilterSet

from geotrek.common.models import Organism
from geotrek.common.filters import StructureRelatedFilterSet

from geotrek.core.filters import TopoFilter, PathFilterSet
from geotrek.infrastructure.filters import InfrastructureFilterSet, SignageFilterSet
from geotrek.maintenance.filters import InterventionFilterSet, ProjectFilterSet
from geotrek.trekking.filters import TrekFilterSet, POIFilterSet

from geotrek.zoning.models import City, District
from .models import (
    CompetenceEdge, LandEdge, LandType, PhysicalEdge, PhysicalType,
    SignageManagementEdge, WorkManagementEdge,
)



class PhysicalEdgeFilterSet(MapEntityFilterSet):
    class Meta:
        model = PhysicalEdge
        fields = ['physical_type']


class LandEdgeFilterSet(StructureRelatedFilterSet):
    class Meta:
        model = LandEdge
        fields = ['land_type']


class OrganismFilterSet(MapEntityFilterSet):
    class Meta:
        fields = ['organization']


class CompetenceEdgeFilterSet(OrganismFilterSet):
    class Meta(OrganismFilterSet.Meta):
        model = CompetenceEdge


class WorkManagementEdgeFilterSet(OrganismFilterSet):
    class Meta(OrganismFilterSet.Meta):
        model = WorkManagementEdge


class SignageManagementEdgeFilterSet(OrganismFilterSet):
    class Meta(OrganismFilterSet.Meta):
        model = SignageManagementEdge


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
        return value.competenceedge_set.select_related('organization').all()


class TopoFilterSignageManagementEdge(TopoFilter):
    model = Organism

    def value_to_edges(self, value):
        return value.signagemanagementedge_set.select_related('organization').all()


class TopoFilterWorkManagementEdge(TopoFilter):
    model = Organism

    def value_to_edges(self, value):
        return value.workmanagementedge_set.select_related('organization').all()


def add_edge_filters(filter_set):
    filter_set.add_filters({
        'city': TopoFilterCity(label=_('City'), required=False),
        'district': TopoFilterDistrict(label=_('District'), required=False),
        'physical_type': TopoFilterPhysicalType(label=_('Physical type'), required=False),
        'land_type': TopoFilterLandType(label=_('Land type'), required=False),
        'competence': TopoFilterCompetenceEdge(label=_('Competence'), required=False),
        'signage': TopoFilterSignageManagementEdge(label=_('Signage management'), required=False),
        'work': TopoFilterWorkManagementEdge(label=_('Work management'), required=False),
    })


add_edge_filters(TrekFilterSet)
add_edge_filters(POIFilterSet)
add_edge_filters(InterventionFilterSet)
add_edge_filters(ProjectFilterSet)
add_edge_filters(PathFilterSet)
add_edge_filters(InfrastructureFilterSet)
add_edge_filters(SignageFilterSet)
