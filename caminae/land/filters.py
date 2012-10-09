# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from django_filters import ModelChoiceFilter

from caminae.core.models import TopologyMixin
from caminae.common.models import Organism
from caminae.common.filters import StructureRelatedFilterSet
from caminae.mapentity.filters import MapEntityFilterSet

from .models import (
    CompetenceEdge, LandEdge, LandType, PhysicalEdge, PhysicalType,
    SignageManagementEdge, WorkManagementEdge
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


class TopoFilterPhysicalType(ModelChoiceFilter):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', PhysicalType.objects.all())
        super(TopoFilterPhysicalType, self).__init__(*args, **kwargs)

    def filter(self, qs, value_physical_type):
        if value_physical_type is None:
            return qs

        edges = value_physical_type.physicaledge_set.all()
        return TopologyMixin.overlapping(qs, edges)


class TopoFilterLandType(ModelChoiceFilter):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', LandType.objects.all())
        super(TopoFilterLandType, self).__init__(*args, **kwargs)

    def filter(self, qs, value_land_type):
        if value_land_type is None:
            return qs

        edges = value_land_type.landedge_set.all()
        return TopologyMixin.overlapping(qs, edges)


class TopoFilter(ModelChoiceFilter):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', Organism.objects.all())
        super(TopoFilter, self).__init__(*args, **kwargs)

    def filter(self, qs, value_orga):
        if not value_orga:
            return qs

        edges = self.orga_to_edges(value_orga)
        return TopologyMixin.overlapping(qs, edges)

    def orga_to_edges(self, orga):
        raise NotImplementedError


class TopoFilterCompetenceEdge(TopoFilter):
    def orga_to_edges(self, orga):
        return orga.competenceedge_set.select_related(depth=1).all()


class TopoFilterSignageManagementEdge(TopoFilter):
    def orga_to_edges(self, orga):
        return orga.signagemanagementedge_set.select_related(depth=1).all()


class TopoFilterWorkManagementEdge(TopoFilter):
    def orga_to_edges(self, orga):
        return orga.workmanagementedge_set.select_related(depth=1).all()


class EdgeFilterSet(MapEntityFilterSet):
    physical_type = TopoFilterPhysicalType(label=_('Physical type'), required=False)
    land_type = TopoFilterLandType(label=_('Land type'), required=False)

    competence = TopoFilterCompetenceEdge(label=_('Competence'), required=False)
    signage = TopoFilterSignageManagementEdge(label=_('Signage management'), required=False)
    work = TopoFilterWorkManagementEdge(label=_('Work management'), required=False)

    class Meta(MapEntityFilterSet.Meta):
        fields = MapEntityFilterSet.Meta.fields


class EdgeStructureRelatedFilterSet(StructureRelatedFilterSet):
    physical_type = TopoFilterPhysicalType(label=_('Physical type'), required=False)
    land_type = TopoFilterLandType(label=_('Land type'), required=False)

    competence = TopoFilterCompetenceEdge(label=_('Competence'), required=False)
    signage = TopoFilterSignageManagementEdge(label=_('Signage management'), required=False)
    work = TopoFilterWorkManagementEdge(label=_('Work management'), required=False)

    class Meta(StructureRelatedFilterSet.Meta):
        fields = StructureRelatedFilterSet.Meta.fields
