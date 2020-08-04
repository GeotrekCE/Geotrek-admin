import mercantile
from math import pi
from rest_framework.exceptions import ParseError

from django.db.models.fields.related import ManyToOneRel
from django.db.models import Func
from django.conf import settings

from django_filters import FilterSet, Filter
from django_filters.filterset import get_model_field
from django.contrib.gis import forms
from django.contrib.gis.geos import Polygon

from .settings import app_settings


class PolygonFilter(Filter):

    field_class = forms.PolygonField

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('field_name', app_settings['GEOM_FIELD_NAME'])
        kwargs.setdefault('widget', forms.HiddenInput)
        kwargs.setdefault('lookup_expr', 'intersects')
        self.tolerance = 0
        super(PolygonFilter, self).__init__(*args, **kwargs)

    def _compute_pixel_size(self, zoom):
        tile_pixel_size = 512
        equatorial_radius_wgs84 = 6378137
        circumference = 2 * pi * equatorial_radius_wgs84
        return circumference / tile_pixel_size / 2 ** int(zoom)

    def get_polygon_from_value(self, value):
        if not value:
            ParseError('Invalid tile string supplied')
        # Parse coordinates from parameter
        try:
            z, x, y = (int(n) for n in value.split('/'))
        except ValueError:
            raise ParseError('Invalid tile string supplied for parameter {0}'.format(self.value))

        # define bounds from x y z and create polygon from bounds
        bounds = mercantile.bounds(int(x), int(y), int(z))
        west, south = mercantile.xy(bounds.west, bounds.south)
        east, north = mercantile.xy(bounds.east, bounds.north)
        bbox = Polygon.from_bbox((west, south, east, north))
        bbox.srid = 3857  # WGS84 SRID
        # compute the tolerance to simplify the geometries
        if not self.tolerance:
            self.tolerance = self._compute_pixel_size(z)
        # transform the polygon to match with db srid
        bbox.transform(settings.SRID)
        return bbox


class TileFilter(PolygonFilter):
    def filter(self, qs, value):
        if not value:
            return qs
        bbox = self.get_polygon_from_value(value)
        qs = qs.filter(geom__intersects=bbox)
        return qs.annotate(simplified_geom=Func('geom', 2 * self.tolerance, function='ST_SimplifyPreserveTopology'))


class PythonTileFilter(PolygonFilter):
    def filter(self, qs, value):
        if not value:
            return qs
        filtered = []
        for o in qs.all():
            geom = getattr(o, self.field_name)
            if geom and geom.valid and not geom.empty:
                if getattr(geom, self.lookup_expr)(self.get_polygon_from_value(value)):
                    filtered.append(o.pk)
            else:
                filtered.append(o.pk)
        qs = qs.filter(pk__in=filtered)
        for index in range(len(qs)):
            qs[index].geom = qs[index].geom.simplify(2 * self.tolerance, preserve_topology=True)
        return qs


class BaseMapEntityFilterSet(FilterSet):
    def __init__(self, *args, **kwargs):
        super(BaseMapEntityFilterSet, self).__init__(*args, **kwargs)
        self.__bypass_labels()

    def __bypass_labels(self):
        """
        These hacks allow to bypass field labels. Using either placeholders,
        empty choices label, etc. This allows to greatly save space in form layout,
        which is required for concise filter forms.
        """
        for fieldname in self.base_filters.keys():
            field = self.form.fields[fieldname]
            if isinstance(field, forms.MultiValueField):
                for i, widget in enumerate(field.widget.widgets):
                    self.__set_placeholder(field.fields[i], widget)
            elif isinstance(field, forms.ChoiceField):
                field.empty_label = field.label
                self.__set_placeholder(field, field.widget)
            elif isinstance(field, forms.NullBooleanField):
                choices = [(u'1', field.label)] + field.widget.choices[1:]
                field.widget.choices = choices
                self.__set_placeholder(field, field.widget)
            else:
                self.__set_placeholder(field, field.widget)

    def __set_placeholder(self, field, widget):
        field.help_text = ''  # Hide help text
        widget.attrs['placeholder'] = field.label
        widget.attrs['data-placeholder'] = field.label
        widget.attrs['title'] = field.label
        widget.attrs['data-label'] = field.label

    @classmethod
    def add_filter(cls, name, filter_=None):
        field = get_model_field(cls._meta.model, name)
        if filter_ is None:
            if isinstance(field, ManyToOneRel):
                filter_ = cls.filter_for_reverse_field(field, name)
            else:
                filter_ = cls.filter_for_field(field, name)
        cls.base_filters[name] = filter_

    @classmethod
    def add_filters(cls, filters):
        for name, filter_ in filters.items():
            filter_.field_name = name
            cls.add_filter(name, filter_)


class MapEntityFilterSet(BaseMapEntityFilterSet):
    tiles = TileFilter()

    class Meta:
        fields = ['tiles']
