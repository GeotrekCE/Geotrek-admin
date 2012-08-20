from caminae.common.filters import StructureRelatedFilterSet

from .models import Intervention, Project


class InterventionFilter(StructureRelatedFilterSet):
    class Meta(StructureRelatedFilterSet.Meta):
        model = Intervention
        fields = StructureRelatedFilterSet.Meta.fields + ['status']


class ProjectFilter(StructureRelatedFilterSet):
    class Meta(StructureRelatedFilterSet.Meta):
        model = Project
        fields = StructureRelatedFilterSet.Meta.fields + ['begin_year', 'end_year']
