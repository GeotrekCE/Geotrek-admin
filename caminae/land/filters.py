from caminae.mapentity.filters import MapEntityFilterSet

from .models import PhysicalEdge, LandEdge, CompetenceEdge, WorkManagementEdge, SignageManagementEdge


class PhysicalEdgeFilter(MapEntityFilterSet):
    class Meta(MapEntityFilterSet.Meta):
        model = PhysicalEdge
        fields = MapEntityFilterSet.Meta.fields + ['physical_type']


class LandEdgeFilter(MapEntityFilterSet):
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
