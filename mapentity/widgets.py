from django.template.loader import render_to_string
from django.forms import widgets as django_widgets
from django.utils import six
from leaflet.forms.widgets import LeafletWidget
from django import forms

from .settings import API_SRID
from .helpers import wkt_to_geom


class MapWidget(LeafletWidget):
    geometry_field_class = 'MapEntity.GeometryField'

    def render(self, name, value, attrs=None):
        attrs = attrs or {}
        attrs.update(geometry_field_class=self.geometry_field_class)
        return super(MapWidget, self).render(name, value, attrs)


class HiddenGeometryWidget(django_widgets.HiddenInput):

    def value_from_datadict(self, data, files, name):
        """
        From WKT to Geometry (TODO: should be done in Field clean())
        """
        wkt = super(HiddenGeometryWidget, self).value_from_datadict(data, files, name)
        return None if not wkt else wkt_to_geom(wkt, silent=True)

    def _format_value(self, value):
        """
        Before serialization, reprojects to API_SRID
        """
        if value and not isinstance(value, six.string_types):
            value.transform(API_SRID)
        return value


class SelectMultipleWithPop(forms.SelectMultiple):
    def __init__(self, *args, **kwargs):
        self.add_url = kwargs.pop('add_url')
        super(SelectMultipleWithPop, self).__init__(*args, **kwargs)

    def render(self, name, *args, **kwargs):
        html = super(SelectMultipleWithPop, self).render(name, *args, **kwargs)
        context = {'field': name, 'add_url': self.add_url}
        popupplus = render_to_string("mapentity/popupplus.html", context)
        return html + popupplus
