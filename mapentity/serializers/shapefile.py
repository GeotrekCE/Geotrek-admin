# -*- coding: utf-8 -*-
import os
import zipfile
import tempfile
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from collections import OrderedDict

from django.core.serializers.base import Serializer
from django.contrib.gis.gdal import check_err, OGRGeomType
from django.contrib.gis.geos.collections import GeometryCollection
from django.contrib.gis.geos import Point, LineString, MultiPoint, MultiLineString
from django.contrib.gis.db.models.fields import (GeometryField, GeometryCollectionField,
                                                 PointField, LineStringField,
                                                 MultiPointField, MultiLineStringField)

from osgeo import ogr, osr

from .. import app_settings


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
        buffr = StringIO()
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

    def _create_shape(self, queryset,  model, columns, filename):
        """Split a shapes into one or more shapes (one for point and one for linestring)
        """
        geo_field = geo_field_from_model(model, 'geom')
        get_geom, geom_type, srid = info_from_geo_field(geo_field)

        if geom_type.upper() in (GeometryField.geom_type, GeometryCollectionField.geom_type):

            by_points, by_linestrings, multipoints, multilinestrings = self.split_bygeom(queryset, geom_getter=get_geom)

            for split_qs, split_geom_field in ((by_points, PointField),
                                               (by_linestrings, LineStringField),
                                               (multipoints, MultiPointField),
                                               (multilinestrings, MultiLineStringField)):
                if len(split_qs) == 0:
                    continue
                split_geom_type = split_geom_field.geom_type
                shp_filepath = shape_write(split_qs, model, columns, get_geom, split_geom_type, srid)
                filename = '%s_%s' % (filename, split_geom_type.lower())
                self.layers[filename] = shp_filepath

        else:
            shp_filepath = shape_write(queryset, model, columns, get_geom, geom_type, srid)
            self.layers[filename] = shp_filepath

    def split_bygeom(self, iterable, geom_getter=lambda x: x.geom):
        """Split an iterable in two list (points, linestring)"""
        points, linestrings, multipoints, multilinestrings = [], [], [], []

        for x in iterable:
            geom = geom_getter(x)
            if geom is None:
                pass
            elif isinstance(geom, GeometryCollection):
                # Duplicate object, shapefile do not support geometry collections !
                subpoints, sublines, pp, ll = self.split_bygeom(geom, geom_getter=lambda geom: geom)
                if subpoints:
                    clone = x.__class__.objects.get(pk=x.pk)
                    clone.geom = MultiPoint(subpoints, srid=geom.srid)
                    multipoints.append(clone)
                if sublines:
                    clone = x.__class__.objects.get(pk=x.pk)
                    clone.geom = MultiLineString(sublines, srid=geom.srid)
                    multilinestrings.append(clone)
            elif isinstance(geom, Point):
                points.append(x)
            elif isinstance(geom, LineString):
                linestrings.append(x)
            else:
                raise ValueError("Only LineString and Point geom should be here. Got %s for pk %d" % (geom, x.pk))
        return points, linestrings, multipoints, multilinestrings


def shapefile_files(shapefile_path):
    basename = shapefile_path.replace('.shp', '')
    return ['%s.%s' % (basename, item) for item in ['shp', 'shx', 'prj', 'dbf']]


def shape_write(iterable, model, columns, get_geom, geom_type, srid, srid_out=None):
    """
    Write tempfile with shape layer.
    """
    from . import field_as_string

    tmp_file, layer, ds, native_srs, output_srs = create_shape_format_layer(columns, geom_type, srid, srid_out)

    feature_def = layer.GetLayerDefn()

    transform = lambda ogr_geom: ogr_geom

    # omg.. will not work for 3D coords
    if native_srs != output_srs:
        ct = osr.CoordinateTransformation(native_srs, output_srs)

        def transform(ogr_geom):
            ogr_geom.Transform(ct)
            return ogr_geom

    for item in iterable:
        feat = ogr.Feature(feature_def)

        for fieldname in columns:
            # They are all String (see create_shape_format_layer)
            value = field_as_string(item, fieldname, ascii=True)
            feat.SetField(fieldname[:10], value[:255])

        geom = get_geom(item)
        if geom:
            ogr_geom = transform(ogr.CreateGeometryFromWkt(geom.wkt))
            check_err(feat.SetGeometry(ogr_geom))

        check_err(layer.CreateFeature(feat))

    ds.Destroy()

    return tmp_file.name


def create_shape_format_layer(fieldnames, geom_type, srid, srid_out=None):
    # Create temp file
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

    # Create other fields
    for fieldname in fieldnames:
        field_defn = ogr.FieldDefn(str(fieldname[:10]), ogr.OFTString)
        field_defn.SetWidth(255)
        if layer.CreateField(field_defn) != 0:
            raise Exception('Faild to create field')

    return tmp, layer, ds, native_srs, output_srs


def geo_field_from_model(model, default_geo_field_name=None):
    """Look for a geo field - taken from shapes"""
    try:
        # If the class defines a geomfield property, use it !
        return model.geomfield
    except AttributeError:
        pass

    fields = model._meta.fields
    geo_fields = [f for f in fields if isinstance(f, GeometryField)]

    # Used for error case
    geo_fields_names = lambda: ', '.join([f.name for f in geo_fields])

    if len(geo_fields) > 1:
        if not default_geo_field_name:
            raise ValueError("More than one geodjango geometry field found, please specify which to use by name using the 'geo_field' keyword. Available fields are: '%s'" % geo_fields_names())
        else:
            geo_field_by_name = [fld for fld in geo_fields if fld.name == default_geo_field_name]
            if not geo_field_by_name:
                raise ValueError("Geodjango geometry field not found with the name '%s', fields available are: '%s'" % (default_geo_field_name, geo_fields_names()))
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

    get_geom = lambda obj: getattr(obj, geo_field_name)

    if hasattr(geo_field, 'geom_type'):
        geom_type = geo_field.geom_type
    else:
        geom_type = geo_field._geom

    if hasattr(geo_field, 'srid'):
        srid = geo_field.srid
    else:
        srid = geo_field._srid

    return get_geom, geom_type, srid
