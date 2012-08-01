
from django_filters import FilterSet, RangeFilter
from .models import Path

class PathFilter(FilterSet):
    length = RangeFilter()

    class Meta:
        model = Path
        fields = ['length']

