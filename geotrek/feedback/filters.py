from mapentity.filters import MapEntityFilterSet
from .models import Report


class ReportFilterSet(MapEntityFilterSet):
    class Meta:
        model = Report
        fields = ['name', 'email', 'category', 'status']
