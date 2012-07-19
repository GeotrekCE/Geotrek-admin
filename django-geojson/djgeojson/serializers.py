"""
Created on 2011-05-12
Updated on 2011-11-09 -- added desrializer support

@author: Daniel Sokolowski

Extends django's built in JSON serializer to support GEOJSON encoding
"""
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.core.serializers.json import (DjangoJSONEncoder, 
                                          Serializer as JsonSerializer)
from django.utils import simplejson
from django.contrib.gis.db.models.fields import GeometryField
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.core.serializers.python import Deserializer as PythonDeserializer

import geojson
from shapely.geometry import asShape


class Serializer(JsonSerializer):

    def __init__(self, collection=False):
        self.collection = collection

     def serialize(self, object, **options):
         options['collection'] = self.collection
        simplejson.dump(self.objects, self.stream, cls=DjangoGeoJsonEncoder, **options)

    def handle_field(self, obj, field):
        """
        If field is of GeometryField than encode otherwise call parent's method
        """
        value = field._get_val_from_obj(obj)
        if isinstance(field, GeometryField):
            self._current[field.name] = value
        else:
            super(Serializer, self).handle_field(obj, field)



class DjangoGeoJsonEncoder(DjangoJSONEncoder):
    """
    DjangoGeoJsonEncoder subclass that knows how to encode GEOSGeometry value
    """
    def __init__(self, **options):
        print options
        super(DjangoGeoJsonEncoder, self).__init__(self, **options)

    def default(self, o):
        """ Overload the default method to process any GEOSGeometry objects 
        otherwise call original method """ 
        if isinstance(o, GEOSGeometry):
            dictval = o.loads(o.geojson)
            return dictval
        return super(DjangoGeoJsonEncoder, self).default(o)


def Deserializer(stream_or_string, **options):
    """
    Deserialize a stream or string of JSON data.
    """
    def GeoJsonToEWKT(dictobj):
        """ 
        Convert to a string that GEOSGeometry class constructor can accept. 
        """
        geojsondict = geojson.loads(dictobj, object_hook=geojson.GeoJSON.to_instance)
        shape = asShape(geojsondict)
        return shape.wkt

    if isinstance(stream_or_string, basestring):
        stream = StringIO(stream_or_string)
    else:
        stream = stream_or_string
    for obj in PythonDeserializer(simplejson.load(stream, object_hook=GeoJsonToEWKT), **options):
        yield obj
