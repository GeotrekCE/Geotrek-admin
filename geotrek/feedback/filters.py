from geotrek.zoning.filters import ZoningFilterSet
from mapentity.filters import MapEntityFilterSet
from .models import Report


class ReportFilterSet(ZoningFilterSet, MapEntityFilterSet):
    class Meta(MapEntityFilterSet.Meta):
        model = Report
        fields = ['activity', 'email', 'category', 'status', 'problem_magnitude']
