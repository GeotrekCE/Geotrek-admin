from caminae.mapentity.filters import MapEntityFilterSet

from .models import Intervention, Project


class InterventionFilter(MapEntityFilterSet):
    class Meta(MapEntityFilterSet.Meta):
        model = Intervention
        fields = MapEntityFilterSet.Meta.fields + ['status']


class ProjectFilter(MapEntityFilterSet):
    class Meta(MapEntityFilterSet.Meta):
        model = Project
        fields = MapEntityFilterSet.Meta.fields + ['begin_year', 'end_year']
