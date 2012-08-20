from caminae.common.filters import StructureRelatedFilterSet

from .models import Intervention, Project


class InterventionFilter(StructureRelatedFilterSet):
    class Meta(StructureRelatedFilterSet.Meta):
        model = Intervention
        fields = StructureRelatedFilterSet.Meta.fields + ['status']
        exclude = ('bbox',)  # Intervention has no geom db field


class ProjectFilter(StructureRelatedFilterSet):
    class Meta(StructureRelatedFilterSet.Meta):
        model = Project
        fields = StructureRelatedFilterSet.Meta.fields + ['begin_year', 'end_year']
        exclude = ('bbox',)  # Project has no geom db field
