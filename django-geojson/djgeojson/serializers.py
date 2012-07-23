"""

    This code is a modified version of Daniel's GeoJSON serializer.

    http://djangosnippets.org/snippets/2596/

    Created on 2011-05-12
    Updated on 2011-11-09 -- added desrializer support

    @author: Daniel Sokolowski

    Extends django's built in JSON serializer to support GEOJSON encoding
"""
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.core.serializers.base import DeserializationError
from django.core.serializers.json import (DjangoJSONEncoder, 
                                          Serializer as JsonSerializer)
from django.utils import simplejson
from django.contrib.gis.db.models.fields import GeometryField
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.core.serializers.python import Deserializer as PythonDeserializer
from django.utils.encoding import smart_unicode

import geojson
from shapely.geometry import asShape


class Serializer(JsonSerializer):
    def __init__(self, *args, **kwargs):
        super(Serializer, self).__init__(*args, **kwargs)
        self.collection = None

    def end_serialization(self):
        self.collection = geojson.FeatureCollection(features=self.objects)
        return geojson.dump(self.collection, self.stream)

    def end_object(self, obj):
        pk = smart_unicode(obj._get_pk_val(), strings_only=True)
        geomattrs = [field for field in obj._meta.fields if isinstance(field, GeometryField)]
        # TODO will raise if not any !
        # TODO warn if more than one ?
        geomattr = geomattrs[0]
        geomfield = getattr(obj, geomattr.name)
        
        simplify = self.options.get('simplify')
        srid = self.options.get('srid')
        
        if simplify is not None:
            geomfield = geomfield.simplify(tolerance=simplify, preserve_topology=True)
        
        if srid is not None:
            geomfield.transform(srid)
        
        gjson = geomfield.geojson
        geometry = simplejson.loads(gjson)
        
        properties = dict(self._current.iteritems())
        if self.selected_fields is not None:
            properties = {k:v for k,v in properties.items() if k in self.selected_fields}
        properties['model'] = smart_unicode(obj._meta)
        properties['pk'] = pk
        self.objects.append(geojson.Feature(id=pk,
                                            properties=properties,
                                            geometry=geometry))
        self._current = None

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
    def FeatureToPython(dictobj):
        properties = dictobj['properties']
        obj = {
            "model"  : properties.pop("model"),
            "pk"     : dictobj['id'],
            "fields" : properties
        }
        shape = asShape(dictobj['geometry'])
        obj['geom'] = shape.wkt
        return obj
    
    if isinstance(stream_or_string, basestring):
        stream = StringIO(stream_or_string)
    else:
        stream = stream_or_string
    try:
        collection = simplejson.load(stream)
        objects = map(FeatureToPython, collection['features'])
        for obj in PythonDeserializer(objects, **options):
            yield obj
    except GeneratorExit:
        raise
    except Exception, e:
        # Map to deserializer error
        raise DeserializationError(e)
