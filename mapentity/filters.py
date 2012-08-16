from django_filters import FilterSet, Filter

import floppyforms as forms
from .widgets import GeomWidget


class PolygonFilter(Filter):
    field_class = forms.gis.PolygonField


class MapEntityFilterSet(FilterSet):
    bbox = PolygonFilter(name='geom', lookup_type='intersects', widget=GeomWidget)

    class Meta:
        fields = ['bbox',]
