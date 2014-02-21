from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import GEOSGeometry

from django.conf import settings
import os.path

from geotrek.core.helpers import TopologyHelper


class Command(BaseCommand):
    args = '<point_layer>'
    help = 'Load a layer with point geometries in a model\n'
    can_import_settings = True

    def handle(self, *args, **options):

        try:
            from osgeo import gdal, ogr, osr
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
        self.stdout.write('%s objects found' % count)

        for i in range(count):
            feature = layer.GetFeature(i)
            featureGeom = feature.GetGeometryRef()
            geometry = GEOSGeometry(featureGeom.ExportToWkt())
            self.create_poi(geometry)

    def create_poi(self, geometry):
        serialized = '{"lng": %s, "lat": %s}' % (geometry.x, geometry.y)
        TopologyHelper.deserialize(serialized)
