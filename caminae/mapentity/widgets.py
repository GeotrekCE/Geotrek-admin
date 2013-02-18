from django.conf import settings
from django.template.loader import render_to_string
from django.forms import widgets as django_widgets

import floppyforms as forms

from caminae.common.utils import transform_wkt, wkt_to_geom


class LeafletMapWidget(forms.gis.BaseGeometryWidget):
    template_name = 'mapentity/fieldgeometry_fragment.html'
    display_wkt = settings.DEBUG

    def get_context(self, name, value, attrs=None, extra_context={}):
        context = super(LeafletMapWidget, self).get_context(name, value, attrs, extra_context)
        context['update'] = bool(value)
        context['field'] = value
        return context


class GeometryWidget(LeafletMapWidget):

    def value_from_datadict(self, data, files, name):
        wkt = super(GeometryWidget, self).value_from_datadict(data, files, name)
        return None if not wkt else transform_wkt(wkt, settings.API_SRID, settings.SRID)

    def get_context(self, name, value, attrs=None, extra_context={}):
        context = super(GeometryWidget, self).get_context(name, value, attrs, extra_context)
        # Be careful, on form error, value is not a GEOSGeometry
        if value:
            if isinstance(value, basestring):
                value = transform_wkt(value, settings.SRID, settings.API_SRID)
                context['field'] = wkt_to_geom(value)
            else:
                value.transform(settings.API_SRID)
        return context


class PointWidget(GeometryWidget,
                  forms.gis.PointWidget):
    pass


class LineStringWidget(GeometryWidget,
                       forms.gis.LineStringWidget):
    pass


class GeomWidget(django_widgets.HiddenInput):
    # hidden by default

    def value_from_datadict(self, data, files, name):
        wkt = super(GeomWidget, self).value_from_datadict(data, files, name)
        return None if not wkt else wkt_to_geom(wkt, silent=True)

    def _format_value(self, value):
        if value and not isinstance(value, basestring):
            value.transform(settings.API_SRID)
        return value


class SelectMultipleWithPop(forms.SelectMultiple):
    def __init__(self, *args, **kwargs):
        self.add_url = kwargs.pop('add_url')
        super(SelectMultipleWithPop, self).__init__(*args, **kwargs)

    def render(self, name, *args, **kwargs):
        html = super(SelectMultipleWithPop, self).render(name, *args, **kwargs)
        context = {'field': name, 'add_url': self.add_url}
        popupplus = render_to_string("mapentity/popupplus.html", context)
        return html+popupplus
