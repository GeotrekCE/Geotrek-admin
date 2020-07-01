from mapentity.filters import MapEntityFilterSet
from .models import Report


class ReportFilterSet(MapEntityFilterSet):
    class Meta:
        model = Report
        fields = ['activity', 'email', 'category', 'status', 'problem_magnitude']
