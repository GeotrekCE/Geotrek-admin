# -*- coding: utf-8 -*-

import os
import zipfile
import tempfile
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.conf import settings
from django.utils.encoding import smart_str
from django.contrib.gis.db.models.fields import GeometryField
from django.contrib.gis.gdal import check_err, OGRGeomType

from osgeo import ogr, osr


def zip_shapes(shapes, delete=True):
    buffr = StringIO()
    zipf = zipfile.ZipFile(buffr, 'w', zipfile.ZIP_DEFLATED)

    for shp_name, shp_path in shapes:
        zip_shapefile_path(zipf, shp_path, shp_name, delete)

    zipf.close()
    buffr.flush()

    zip_stream = buffr.getvalue()
    buffr.close()

    return zip_stream


def zip_shapefile_path(zipf, shapefile_path, file_name, delete=True):
    files = ['shp', 'shx', 'prj', 'dbf']
    for item in files:
        filename = '%s.%s' % (shapefile_path.replace('.shp',''), item)
        zipf.write(filename, arcname='%s.%s' % (file_name.replace('.shp',''), item))
        if delete:
            os.remove(filename)


class ShapeCreator(object):

    def __init__(self):
        self.shapes = [] # list of pair (shp name, shp path)

    def add_shape(self, shp_name, shp_filepath):
        self.shapes.append((shp_name, shp_filepath))

    def add_shape_from_qs(self, qs, srid_out=None, shp_name='shp_download'):
        self.add_shape_from_model(qs, qs.model, srid_out, shp_name)

    def add_shape_from_model(self, iterable, model, srid_out=None, shp_name='shp_download'):
        fieldmap = fieldmap_from_model(model)
        get_geom, geom_type, srid = info_from_geo_field(geo_field_from_model(model))

        shp_filepath = shape_write(iterable, fieldmap, get_geom, geom_type, srid, srid_out)
        self.add_shape(shp_name, shp_filepath)

    def as_zip(self):
        return zip_shapes(self.shapes)


def shape_write(iterable, fieldmap, get_geom, geom_type, srid, srid_out=None):

    # normalize ?!
    fieldmap = dict((k[:10], v) for k, v in fieldmap.iteritems())

    # refactor
    tmp_file, layer, ds, native_srs, output_srs = create_shape_format_layer(fieldmap.keys(), geom_type, srid, srid_out)

    feature_def = layer.GetLayerDefn()

    transform = lambda ogr_geom: ogr_geom

    # omg.. will not work for 3D coords
    if native_srs != output_srs:
        ct = osr.CoordinateTransformation(native_srs, output_srs)
        def transform(ogr_geom):
            ogr_geom.Transform(ct)
            return ogr_geom

    for item in iterable:
        feat = ogr.Feature( feature_def )

        for fieldname, getter in fieldmap.iteritems():
            feat.SetField(fieldname, getter(item))

        geom = get_geom(item)
        if geom:
            ogr_geom = transform(ogr.CreateGeometryFromWkt(geom.wkt))
            check_err(feat.SetGeometry(ogr_geom))

        check_err(layer.CreateFeature(feat))

    ds.Destroy()

    return tmp_file.name

def create_shape_format_layer(fieldnames, geom_type, srid, srid_out=None):
    # Create temp file
    tmp = tempfile.NamedTemporaryFile(suffix='.shp', mode = 'w+b', dir=settings.TEMP_DIR)
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
        field_defn = ogr.FieldDefn(fieldname, ogr.OFTString)
        field_defn.SetWidth( 255 )
        if layer.CreateField(field_defn) != 0:
            raise Exception('Faild to create field')

    return tmp, layer, ds, native_srs, output_srs


def fieldmap_from_fields(model, fieldnames):
    from .serializers import plain_text
    return dict(
        (fname, lambda x, fname=fname: smart_str(plain_text(getattr(x, fname + '_csv_display',
                                                            getattr(x, fname + '_display', getattr(x, fname))))))
        for fname in fieldnames
    )

def fieldmap_from_model(model):
    """Extract all non geometry fields from model"""
    fields = model._meta.fields
    non_geometry_field_names = [f.name for f in fields if not isinstance(f, GeometryField)]

    return fieldmap_from_fields(model, non_geometry_field_names)


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

