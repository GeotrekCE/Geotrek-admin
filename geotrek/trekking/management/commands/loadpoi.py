import os.path

from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import GEOSGeometry

from geotrek.core.helpers import TopologyHelper
from geotrek.trekking.models import POI, POIType


class Command(BaseCommand):
    args = '<point_layer>'
    help = 'Load a layer with point geometries in a model\n'
    can_import_settings = True
    field_name = 'name'
    field_poitype = 'type'

    def handle(self, *args, **options):

        try:
            from osgeo import gdal, ogr, osr  # NOQA
        except ImportError:
            msg = 'GDAL Python bindings are not available. Can not proceed.'
            raise CommandError(msg)

        # Validate arguments
        if len(args) != 1:
            raise CommandError('Filename missing. See help')

        filename = args[0]

        if not os.path.exists(filename):
            raise CommandError('File does not exists at: %s' % filename)

        ogrdriver = ogr.GetDriverByName("ESRI Shapefile")
        datasource = ogrdriver.Open(filename, 1)
        layer = datasource.GetLayer()
        count = layer.GetFeatureCount()
        if options['verbosity'] >= 1:
            self.stdout.write('%s objects found' % count)

        for i in range(count):
            feature = layer.GetFeature(i)
            featureGeom = feature.GetGeometryRef()
            geometry = GEOSGeometry(featureGeom.ExportToWkt())
            name = feature.GetFieldAsString(self.field_name)
            if name:
                name = name.decode('utf-8')
            poitype = feature.GetFieldAsString(self.field_poitype)
            if poitype:
                poitype = poitype.decode('utf-8')
            self.create_poi(geometry, name, poitype)

    def create_poi(self, geometry, name, poitype):
        poitype, created = POIType.objects.get_or_create(label=poitype)
        poi = POI.objects.create(name=name, type=poitype)
        # Use existing topology helpers to transform a Point(x, y)
        # to a path aggregation (topology)
        serialized = '{"lng": %s, "lat": %s}' % (geometry.x, geometry.y)
        topology = TopologyHelper.deserialize(serialized)
        # Move deserialization aggregations to the POI
        poi.mutate(topology)
        return poi
