# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from mapentity.filters import MapEntityFilterSet

from geotrek.common.models import Organism
from geotrek.common.filters import StructureRelatedFilterSet

from geotrek.core.filters import TopologyFilter, PathFilterSet
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


"""

    Injected filter fields

"""


class TopologyFilterPhysicalType(TopologyFilter):
    model = PhysicalType

    def value_to_edges(self, value):
        return value.physicaledge_set.all()


class TopologyFilterLandType(TopologyFilter):
    model = LandType

    def value_to_edges(self, value):
        return value.landedge_set.all()


class TopologyFilterCity(TopologyFilter):
    model = City

    def value_to_edges(self, value):
        return value.cityedge_set.all()


class TopologyFilterDistrict(TopologyFilter):
    model = District

    def value_to_edges(self, value):
        return value.districtedge_set.all()


class TopologyFilterCompetenceEdge(TopologyFilter):
    model = Organism

    def value_to_edges(self, value):
        return value.competenceedge_set.select_related('organization').all()


class TopologyFilterSignageManagementEdge(TopologyFilter):
    model = Organism

    def value_to_edges(self, value):
        return value.signagemanagementedge_set.select_related('organization').all()


class TopologyFilterWorkManagementEdge(TopologyFilter):
    model = Organism

    def value_to_edges(self, value):
        return value.workmanagementedge_set.select_related('organization').all()


def add_edge_filters(filter_set):
    filter_set.add_filters({
        'city': TopologyFilterCity(label=_('City'), required=False),
        'district': TopologyFilterDistrict(label=_('District'), required=False),
        'physical_type': TopologyFilterPhysicalType(label=_('Physical type'), required=False),
        'land_type': TopologyFilterLandType(label=_('Land type'), required=False),
        'competence': TopologyFilterCompetenceEdge(label=_('Competence'), required=False),
        'signage': TopologyFilterSignageManagementEdge(label=_('Signage management'), required=False),
        'work': TopologyFilterWorkManagementEdge(label=_('Work management'), required=False),
    })


add_edge_filters(TrekFilterSet)
add_edge_filters(POIFilterSet)
add_edge_filters(InterventionFilterSet)
add_edge_filters(ProjectFilterSet)
add_edge_filters(PathFilterSet)
add_edge_filters(InfrastructureFilterSet)
add_edge_filters(SignageFilterSet)
