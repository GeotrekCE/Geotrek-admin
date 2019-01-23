import csv
from functools import partial

from django.core.exceptions import FieldDoesNotExist
from django.core.serializers.base import Serializer
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.contrib.gis.geos import Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon
from django.contrib.gis.geos.collections import GeometryCollection
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _

from geotrek.authent.serializers import StructureSerializer
from geotrek.common.serializers import PictogramSerializerMixin, BasePublishableSerializerMixin
from geotrek.signage import models as signage_models

from mapentity.serializers.helpers import smart_plain_text, field_as_string
from mapentity.serializers.shapefile import ZipShapeSerializer

from rest_framework import serializers as rest_serializers


class SignageTypeSerializer(PictogramSerializerMixin):
    class Meta:
        model = signage_models.SignageType
        fields = ('id', 'pictogram', 'label')


class SignageSerializer(BasePublishableSerializerMixin):
    type = SignageTypeSerializer()
    structure = StructureSerializer()

    class Meta:
        model = signage_models.Signage
        id_field = 'id'  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        geo_field = 'geom'
        fields = ('id', 'structure', 'name', 'type', 'code', 'printed_elevation', 'condition',
                  'manager', 'sealing') + \
            BasePublishableSerializerMixin.Meta.fields


class BladeTypeSerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = signage_models.BladeType
        fields = ('label', )


class BladeSerializer(rest_serializers.ModelSerializer):
    type = BladeTypeSerializer()
    structure = StructureSerializer()

    class Meta:
        model = signage_models.Blade
        id_field = 'id'  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        geo_field = 'geom'
        fields = ('id', 'structure', 'number', 'order_lines', 'type', 'color', 'condition', 'direction')


class CSVBladeSerializer(Serializer):
    def serialize(self, queryset, **options):
        """
        Uses self.columns, containing fieldnames to produce the CSV.
        The header of the csv is made of the verbose name of each field.
        """
        model = signage_models.Line
        columns = options.pop('fields')
        stream = options.pop('stream')
        ascii = options.get('ensure_ascii', True)

        headers = []
        for field in columns:
            c = getattr(model, '%s_verbose_name' % field, None)
            if c is None:
                try:
                    f = model._meta.get_field(field)
                    if f.one_to_many:
                        c = f.field.model._meta.verbose_name_plural
                    else:
                        c = f.verbose_name
                except FieldDoesNotExist:
                    c = _(field.title())
            headers.append(smart_str(unicode(c)))
        getters = {}
        for field in columns:
            try:
                modelfield = model._meta.get_field(field)
            except FieldDoesNotExist:
                modelfield = None
            if isinstance(modelfield, ForeignKey):
                getters[field] = lambda obj, field: smart_plain_text(getattr(obj, field), ascii)
            elif isinstance(modelfield, ManyToManyField):
                getters[field] = lambda obj, field: ','.join([smart_plain_text(o, ascii)
                                                              for o in getattr(obj, field).all()] or '')
            else:
                getters[field] = partial(field_as_string, ascii=ascii)

        def get_lines():
            yield headers
            for blade in queryset.order_by('number'):
                for obj in blade.lines.order_by('number'):
                    yield [getters[field](obj, field) for field in columns]

        writer = csv.writer(stream)
        writer.writerows(get_lines())


class ZipBladeShapeSerializer(ZipShapeSerializer):
    def split_bygeom(self, iterable, geom_getter=lambda x: x.geom):
        """Split an iterable in two list (points, linestring)"""
        points, linestrings, polygons, multipoints, multilinestrings, multipolygons = [], [], [], [], [], []
        for blade in iterable:
            for x in blade.lines.all():
                geom = geom_getter(x)
                if geom is None:
                    pass
                elif isinstance(geom, GeometryCollection):
                    # Duplicate object, shapefile do not support geometry collections !
                    subpoints, sublines, subpolygons, pp, ll, yy = self.split_bygeom(geom, geom_getter=lambda geom: geom)
                    if subpoints:
                        clone = x.__class__.objects.get(pk=x.pk)
                        clone.geom = MultiPoint(subpoints, srid=geom.srid)
                        multipoints.append(clone)
                    if sublines:
                        clone = x.__class__.objects.get(pk=x.pk)
                        clone.geom = MultiLineString(sublines, srid=geom.srid)
                        multilinestrings.append(clone)
                    if subpolygons:
                        clone = x.__class__.objects.get(pk=x.pk)
                        clone.geom = MultiPolygon(subpolygons, srid=geom.srid)
                        multipolygons.append(clone)
                elif isinstance(geom, Point):
                    points.append(x)
                elif isinstance(geom, LineString):
                    linestrings.append(x)
                elif isinstance(geom, Polygon):
                    polygons.append(x)
                else:
                    raise ValueError("Only LineString, Point and Polygon should be here. Got %s for pk %d" %
                                     (geom, x.pk))
        return points, linestrings, polygons, multipoints, multilinestrings, multipolygons
