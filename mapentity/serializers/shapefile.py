# -*- coding: utf-8 -*-

from collections import OrderedDict
import os
import tempfile
import unicodedata
import zipfile

from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.contrib.gis.db.models.fields import (GeometryField, GeometryCollectionField,
                                                 PointField, LineStringField, PolygonField,
                                                 MultiPointField, MultiLineStringField, MultiPolygonField)
from django.contrib.gis.gdal import check_err, OGRGeomType
from django.contrib.gis.geos import Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon
from django.contrib.gis.geos.collections import GeometryCollection
from django.core.serializers.base import Serializer
from django.core.exceptions import FieldDoesNotExist
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _

from osgeo import ogr, osr

from ..settings import app_settings
from .helpers import smart_plain_text, field_as_string
from io import BytesIO

os.environ["SHAPE_ENCODING"] = "UTF-8"


class ZipShapeSerializer(Serializer):
    def __init__(self, *args, **kwargs):
        super(ZipShapeSerializer, self).__init__(*args, **kwargs)
        self.layers = OrderedDict()

    def start_object(self, *args, **kwargs):
        pass

    def serialize(self, queryset, **options):
        columns = options.pop('fields')
        stream = options.pop('stream')
        model = options.pop('model', None) or queryset.model
        delete = options.pop('delete', True)
        filename = options.pop('filename', 'shp_download')
        # Zip all shapefiles created temporarily
        self._create_shape(queryset, model, columns, filename)
        self.zip_shapefiles(stream, delete=delete)

    def zip_shapefiles(self, stream, delete=True):
        # Can't use stream, because HttpResponse is not seekable
        buffr = BytesIO()
        zipf = zipfile.ZipFile(buffr, 'w', zipfile.ZIP_DEFLATED)

        for filename, shp_filepath in self.layers.items():
            shapefiles = shapefile_files(shp_filepath)
            archivefiles = shapefile_files(filename)
            for source, dest in zip(shapefiles, archivefiles):
                zipf.write(source, arcname=dest)
                if delete:
                    os.remove(source)

        zipf.close()
        buffr.flush()  # zip.close() writes stuff.
        stream.write(buffr.getvalue())
        buffr.close()

    def _create_shape(self, queryset, model, columns, filename):
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
                split_geom_type = split_geom_field.geom_type
                shp_filepath = shape_write(split_qs, model, columns, get_geom, split_geom_type, srid)
                subfilename = '%s_%s' % (filename, split_geom_type.lower())
                self.layers[subfilename] = shp_filepath

        else:
            shp_filepath = shape_write(queryset, model, columns, get_geom, geom_type, srid)
            self.layers[filename] = shp_filepath

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


def shapefile_files(shapefile_path):
    basename = shapefile_path.replace('.shp', '')
    return ['%s.%s' % (basename, item) for item in ['shp', 'shx', 'prj', 'dbf']]


def shape_write(iterable, model, columns, get_geom, geom_type, srid, srid_out=None):
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

    tmp_file, layer, ds, native_srs, output_srs, column_map = create_shape_format_layer(headers, geom_type,
                                                                                        srid, srid_out)

    feature_def = layer.GetLayerDefn()

    if native_srs != output_srs:
        ct = osr.CoordinateTransformation(native_srs, output_srs)

        def transform(ogr_geom):
            ogr_geom.Transform(ct)
            return ogr_geom
    else:
        def transform(ogr_geom):
            return ogr_geom

    for item in iterable:
        feat = ogr.Feature(feature_def)

        for fieldname in columns:
            try:
                modelfield = model._meta.get_field(fieldname)
            except FieldDoesNotExist:
                modelfield = None
            if isinstance(modelfield, ForeignKey):
                value = smart_plain_text(getattr(item, fieldname))
            elif isinstance(modelfield, ManyToManyField):
                value = ','.join([smart_plain_text(o)
                                  for o in getattr(item, fieldname).all()] or '')
            else:
                value = field_as_string(item, fieldname)

            feat.SetField(column_map.get(columns_headers.get(fieldname)),
                          value[:254])

        geom = get_geom(item)
        if geom:
            ogr_geom = transform(ogr.CreateGeometryFromWkt(geom.wkt))
            check_err(feat.SetGeometry(ogr_geom))

        check_err(layer.CreateFeature(feat))

    ds.Destroy()

    return tmp_file.name


def create_shape_format_layer(headers, geom_type, srid, srid_out=None):
    """Creates a Shapefile layer definition, that will later be filled with data.

    :note:

        All attributes fields have type `String`.

    """
    column_map = {}

    # Create temp file
    tmp = tempfile.NamedTemporaryFile(suffix='.shp', mode='w+b', dir=app_settings['TEMP_DIR'])
    # we must close the file for GDAL to be able to open and write to it
    tmp.close()
    # create shape format

    dr = ogr.GetDriverByName('ESRI Shapefile')
    ds = dr.CreateDataSource(tmp.name)
    if ds is None:
        raise Exception('Could not create file!')

    ogr_type = OGRGeomType(geom_type).num

    native_srs = osr.SpatialReference()
    native_srs.ImportFromEPSG(srid)

    if srid_out:
        output_srs = osr.SpatialReference()
        output_srs.ImportFromEPSG(srid_out)
    else:
        output_srs = native_srs

    layer = ds.CreateLayer('lyr', srs=output_srs, geom_type=ogr_type)
    if layer is None:
        raise ValueError('Could not create layer (type=%s, srs=%s)' % (geom_type, output_srs))

    # Create other fields
    for fieldname in headers:
        field_defn = ogr.FieldDefn(fieldname[:10], ogr.OFTString)
        field_defn.SetWidth(254)

        if layer.CreateField(field_defn) != 0:
            raise Exception('Failed to create field')

        else:
            # get name created for each field
            layerDefinition = layer.GetLayerDefn()
            column_map[fieldname] = layerDefinition.GetFieldDefn(layerDefinition.GetFieldCount() - 1).GetName()

    return tmp, layer, ds, native_srs, output_srs, column_map


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

    if hasattr(geo_field, 'geom_type'):
        geom_type = geo_field.geom_type
    else:
        geom_type = geo_field._geom

    if hasattr(geo_field, 'srid'):
        srid = geo_field.srid
    else:
        srid = geo_field._srid

    return get_geom, geom_type, srid
