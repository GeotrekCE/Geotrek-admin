from django.conf import settings
from django.template.loader import render_to_string
from django import forms
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


class SelectMultipleWithPop(forms.SelectMultiple):
    def __init__(self, *args, **kwargs):
        self.add_url = kwargs.pop('add_url')
        super(SelectMultipleWithPop, self).__init__(*args, **kwargs)

    def render(self, name, *args, **kwargs):
        html = super(SelectMultipleWithPop, self).render(name, *args, **kwargs)
        context = {'field': name, 'add_url': self.add_url}
        popupplus = render_to_string("mapentity/popupplus.html", context)
        return html+popupplus
