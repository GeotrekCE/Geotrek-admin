from django import forms as django_forms

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

    def __init__(self, *args, **kwargs):
        super(MapEntityFilterSet, self).__init__(*args, **kwargs)
        self.__bypass_labels()
    
    def __bypass_labels(self):
        """
        These hacks allow to bypass field labels. Using either placeholders,
        empty choices label, etc. This allows to greatly save space in form layout,
        which is required for concise filter forms.
        """
        for fieldname in self._meta.fields:
            field = self.form.fields[fieldname]
            if isinstance(field, django_forms.MultiValueField):
                for i, widget in enumerate(field.widget.widgets):
                    self.__set_placeholder(field.fields[i], widget)
            elif isinstance(field, django_forms.ChoiceField):
                field.empty_label = field.label
            else:
                self.__set_placeholder(field, field.widget)

    def __set_placeholder(self, field, widget):
        widget.attrs['placeholder'] = field.label
