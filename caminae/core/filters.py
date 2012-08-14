import sys
from django_filters import FilterSet, RangeFilter, Filter
from decimal import Decimal

import floppyforms as forms

from .models import Path
from .widgets import GeomWidget


class OptionalRangeFilter(RangeFilter):
    def filter(self, qs, value):
        if value:
            if value.start and not value.stop:
                value = slice(value.start, Decimal(sys.maxint), value.step)
            if not value.start and value.stop:
                value = slice(Decimal(-(sys.maxint +1)), value.stop, value.step)
        return super(OptionalRangeFilter, self).filter(qs, value)


class PolygonFilter(Filter):
    field_class = forms.gis.PolygonField


class PathFilter(FilterSet):
    length = OptionalRangeFilter()
    bbox = PolygonFilter(name='geom', lookup_type='intersects', widget=GeomWidget)

    class Meta:
        model = Path
        fields = ['length', 'bbox']
