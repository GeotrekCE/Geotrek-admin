# -*- coding: utf-8 -*-

from collections import OrderedDict
import fiona
from fiona.crs import from_epsg
from io import BytesIO
import json
import os
import shutil
import uuid
import unicodedata
import zipfile

from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.contrib.gis.db.models.fields import (GeometryField, GeometryCollectionField,
                                                 PointField, LineStringField, PolygonField,
                                                 MultiPointField, MultiLineStringField, MultiPolygonField)
from django.contrib.gis.geos import Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon
from django.contrib.gis.geos.collections import GeometryCollection
from django.core.serializers.base import Serializer
from django.core.exceptions import FieldDoesNotExist
from django.utils.encoding import smart_str
from django.utils.translation import gettext as _

from ..settings import app_settings
from .helpers import smart_plain_text, field_as_string

os.environ["SHAPE_ENCODING"] = "UTF-8"


class ZipShapeSerializer(Serializer):
    def __init__(self, *args, **kwargs):
        super(ZipShapeSerializer, self).__init__(*args, **kwargs)
        self.path_directory = os.path.join(app_settings['TEMP_DIR'], str(uuid.uuid4()))
        os.mkdir(self.path_directory)

    def serialize(self, queryset, **options):
        columns = options.pop('fields')
        stream = options.pop('stream')
        model = options.pop('model', None) or queryset.model
        delete = options.pop('delete', True)
        filename = options.pop('filename', 'shp_download')
        # Zip all shapefiles created temporarily
        self._create_shape(self.path_directory, queryset, model, columns)
        self.zip_shapefiles(self.path_directory, stream, filename)
        if delete:
            shutil.rmtree(self.path_directory)

    def zip_shapefiles(self, shape_directory, stream, filename):
        buffr = BytesIO()
        zipf = zipfile.ZipFile(buffr, "w", compression=zipfile.ZIP_DEFLATED)
        path = os.path.normpath(shape_directory)
        if path != os.curdir and path != shape_directory:
            zipf.write(path, os.path.relpath(path, shape_directory))
        for dirpath, dirnames, filenames in os.walk(shape_directory):
            for name in sorted(dirnames):
                path = os.path.normpath(os.path.join(dirpath, name))
                zipf.write(path, os.path.relpath(path, shape_directory))
            for name in filenames:
                path = os.path.normpath(os.path.join(dirpath, name))
                if os.path.isfile(path):
                    zipf.write(path, os.path.relpath(path, shape_directory))

        zipf.close()
        buffr.flush()  # zip.close() writes stuff.
        stream.write(buffr.getvalue())
        buffr.close()

    def _create_shape(self, shape_directory, queryset, model, columns):
        """Split a shapes into one or more shapes (one for point and one for linestring)
        """
        geo_field = geo_field_from_model(model, app_settings['GEOM_FIELD_NAME'])
        get_geom, geom_type, srid = info_from_geo_field(geo_field)
        if geom_type.upper() in (GeometryField.geom_type, GeometryCollectionField.geom_type):

            by_points, by_linestrings, by_polygons, multipoints, multilinestrings, multipolygons = \
                self.split_bygeom(queryset, geom_getter=get_geom)

            for split_qs, split_geom_field in ((by_points, PointField),
                                               (by_linestrings, LineStringField),
                                               (by_polygons, PolygonField),
                                               (multipoints, MultiPointField),
                                               (multilinestrings, MultiLineStringField),
                                               (multipolygons, MultiPolygonField)):
                if len(split_qs) == 0:
                    continue
                split_geom_type = split_geom_field.geom_class().geom_type
                shape_write(shape_directory, split_qs, model, columns, get_geom, split_geom_type, srid)

        else:
            geom_type = geo_field.geom_class().geom_type
            shape_write(shape_directory, queryset, model, columns, get_geom, geom_type, srid)

    def split_bygeom(self, iterable, geom_getter=lambda x: x.geom):
        """Split an iterable in two list (points, linestring)"""
        points, linestrings, polygons, multipoints, multilinestrings, multipolygons = [], [], [], [], [], []

        for x in iterable:
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
                raise ValueError("Only LineString, Point and Polygon should be here. Got %s for pk %d" % (geom, x.pk))
        return points, linestrings, polygons, multipoints, multilinestrings, multipolygons


def shape_write(shape_directory, iterable, model, columns, get_geom, geom_type, srid, srid_out=None):
    """
    Write tempfile with shape layer.
    """

    headers = []
    columns_headers = {}
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

        reponse = "{}".format(c)
        reponse = unicodedata.normalize('NFD', reponse)
        reponse = smart_str(reponse.encode('ascii', 'ignore')).replace(' ', '_').lower()

        headers.append(reponse)
        columns_headers[field] = reponse
    shape, headers = create_shape_format_layer(shape_directory, headers, geom_type, srid, srid_out)
    if srid != srid_out and srid_out:

        def transform(ogr_geom):
            ogr_geom.transform(srid_out)
            return ogr_geom
    else:
        def transform(ogr_geom):
            return ogr_geom

    for item in iterable:
        geom = get_geom(item)
        if geom:
            geom = transform(geom)
        shape.write({'geometry': json.loads(geom.json),
                     'properties': get_serialized_properties(model, item, columns, columns_headers)})
    shape.close()


def get_serialized_properties(model, item, columns, columns_headers):
    properties = {}
    for fieldname in columns:
        try:
            modelfield = model._meta.get_field(fieldname)
        except FieldDoesNotExist:
            modelfield = None
        if isinstance(modelfield, ForeignKey):
            properties[columns_headers[fieldname][:10]] = smart_plain_text(getattr(item, fieldname))
        elif isinstance(modelfield, ManyToManyField):
            properties[columns_headers[fieldname][:10]] = ','.join([smart_plain_text(o)
                                                                    for o in getattr(item, fieldname).all()] or '')
        else:
            properties[columns_headers[fieldname][:10]] = field_as_string(item, fieldname)
    return properties


def create_shape_format_layer(directory, headers, geom_type, srid, srid_out=None):
    """Creates a Shapefile layer definition, that will later be filled with data.

    :note:

        All attributes fields have type `String`.

    """
    # Create temp file
    if srid_out:
        srid = srid_out
    properties_schema = {k[:10]: 'str' for k in headers}
    schema = {
        'geometry': geom_type,
        'properties': properties_schema,
    }
    shape = fiona.open(directory, layer=geom_type, mode='w', driver='ESRI Shapefile', schema=schema, encoding='UTF-8',
                       crs=from_epsg(srid))
    return shape, headers


def geo_field_from_model(model, default_geo_field_name=None):
    """Look for a geo field - taken from shapes"""
    try:
        # If the class defines a geomfield property, use it !
        return model.geomfield
    except AttributeError:
        pass

    fields = model._meta.fields
    geo_fields = [f for f in fields if isinstance(f, GeometryField)]

    # Used for error case
    def geo_fields_names():
        return ', '.join([f.name for f in geo_fields])

    if len(geo_fields) > 1:
        if not default_geo_field_name:
            raise ValueError("More than one geodjango geometry field found, please specify which to use by name using \
the 'geo_field' keyword. Available fields are: '%s'" % geo_fields_names())
        else:
            geo_field_by_name = [fld for fld in geo_fields if fld.name == default_geo_field_name]
            if not geo_field_by_name:
                raise ValueError("Geodjango geometry field not found with the name '%s', fields available are: '%s'" %
                                 (default_geo_field_name, geo_fields_names()))
            else:
                geo_field = geo_field_by_name[0]
    elif geo_fields:
        geo_field = geo_fields[0]
    else:
        raise ValueError('No geodjango geometry fields found in this model')

    return geo_field


def info_from_geo_field(geo_field):
    """Extract relevant info from geofield"""

    geo_field_name = geo_field.name

    def get_geom(obj):
        return getattr(obj, geo_field_name)

    geom_type = geo_field.geom_type
    srid = geo_field.srid

    return get_geom, geom_type, srid
