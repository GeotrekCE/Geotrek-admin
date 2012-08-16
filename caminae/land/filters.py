from django_filters import FilterSet

from .models import PhysicalEdge, LandEdge, CompetenceEdge, WorkManagementEdge, SignageManagementEdge


class PhysicalEdgeFilter(FilterSet):
    class Meta:
        model = PhysicalEdge
        fields = ['physical_type']


class LandEdgeFilter(FilterSet):
    class Meta:
        model = LandEdge
        fields = ['land_type']


class CompetenceEdgeFilter(FilterSet):
    class Meta:
        model = CompetenceEdge
        fields = ['organization']


class WorkManagementEdgeFilter(FilterSet):
    class Meta:
        model = WorkManagementEdge
        fields = ['organization']


class SignageManagementEdgeFilter(FilterSet):
    class Meta:
        model = SignageManagementEdge
        fields = ['organization']
