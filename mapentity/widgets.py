from django.conf import settings
from django.forms import widgets as django_widgets

from caminae.common.utils import wkt_to_geom


class GeomWidget(django_widgets.HiddenInput):
    # hidden by default

    def value_from_datadict(self, data, files, name):
        wkt = super(GeomWidget, self).value_from_datadict(data, files, name)
        return None if not wkt else wkt_to_geom(wkt)

    def _format_value(self, value):
        if value and not isinstance(value, basestring):
            value.transform(settings.API_SRID)
        return value
