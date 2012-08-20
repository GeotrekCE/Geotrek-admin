from django_filters import FilterSet, Filter

import floppyforms as forms
from .widgets import GeomWidget


class PolygonFilter(Filter):
    field_class = forms.gis.PolygonField


class PythonPolygonFilter(PolygonFilter):
    widget = GeomWidget
    
    def filter(self, qs, value):
        if not value:
            return qs
        filtered = []
        for o in qs.all():
            geom = getattr(o, self.name)
            if geom and geom.intersects(value):
                filtered.append(o.pk)
        return qs.filter(pk__in=filtered)


class MapEntityFilterSet(FilterSet):
    bbox = PolygonFilter(name='geom', lookup_type='intersects', widget=GeomWidget)

    class Meta:
        fields = ['bbox',]
