from django.conf import settings
from django.template.loader import render_to_string
from django.forms import widgets as django_widgets

import floppyforms as forms

from geotrek.common.utils import transform_wkt, wkt_to_geom


class HiddenGeometryWidget(django_widgets.HiddenInput):
    # hidden by default

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
        if value and not isinstance(value, basestring):
            value.transform(settings.API_SRID)
        return value


"""

Floppyforms widgets

"""


class LeafletMapWidget(forms.gis.BaseGeometryWidget):
    template_name = 'mapentity/fieldgeometry_fragment.html'
    display_wkt = settings.DEBUG

    def get_context(self, name, value, attrs=None, extra_context=None):
        context = super(LeafletMapWidget, self).get_context(name, value, attrs, extra_context or {})
        context['update'] = bool(value)
        context['field'] = value
        return context


class GeometryWidget(LeafletMapWidget):
    dim = 3

    def value_from_datadict(self, data, files, name):
        """
        From WKT to post-processed WKT (TODO: should be done in Field clean())
        """
        wkt = super(GeometryWidget, self).value_from_datadict(data, files, name)
        return None if not wkt else transform_wkt(wkt, settings.API_SRID, settings.SRID, self.dim)

    def get_context(self, name, value, attrs=None, extra_context=None):
        """
        Before serialization, reprojects to API_SRID. But handles the form validation error, where
        value is a string.
        TODO: There should be a simpler way.
        TODO: This fails if WKT is invalid.
        """
        context = super(GeometryWidget, self).get_context(name, value, attrs, extra_context or {})
        # Be careful, on form error, value is not a GEOSGeometry
        if value:
            if isinstance(value, basestring):
                value = transform_wkt(value, settings.SRID, settings.API_SRID, self.dim)
                context['field'] = wkt_to_geom(value)
            else:
                value.transform(settings.API_SRID)
        return context


class PointWidget(GeometryWidget,
                  forms.gis.PointWidget):
    pass


class Point2DWidget(GeometryWidget,
                    forms.gis.PointWidget):
    dim = 2


class LineStringWidget(GeometryWidget,
                       forms.gis.LineStringWidget):
    pass


class SelectMultipleWithPop(forms.SelectMultiple):
    def __init__(self, *args, **kwargs):
        self.add_url = kwargs.pop('add_url')
        super(SelectMultipleWithPop, self).__init__(*args, **kwargs)

    def render(self, name, *args, **kwargs):
        html = super(SelectMultipleWithPop, self).render(name, *args, **kwargs)
        context = {'field': name, 'add_url': self.add_url}
        popupplus = render_to_string("mapentity/popupplus.html", context)
        return html + popupplus
