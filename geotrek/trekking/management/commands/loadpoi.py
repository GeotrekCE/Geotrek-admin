from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import Point

from geotrek.core.helpers import TopologyHelper
from geotrek.trekking.models import POI, POIType


class Command(BaseCommand):
    help = 'Load a layer with point geometries in a model\n'
    can_import_settings = True
    field_name = 'name'
    field_poitype = 'type'

    def add_arguments(self, parser):
        parser.add_argument('point_layer')
        parser.add_argument('--encoding', '-e', action='store', dest='encoding', default='utf-8',
                            help='File encoding, default utf-8')

    def handle(self, *args, **options):
        verbosity = options.get('verbosity')

        filename = options['point_layer']

        data_source = DataSource(filename, encoding=options.get('encoding'))

        for i, layer in enumerate(data_source):
            if verbosity >= 1:
                self.stdout.write("- Layer '{}' with {} objects found".format(layer.name, layer.num_feat))
            available_fields = layer.fields
            for feature in layer:
                feature_geom = feature.geom
                name = feature.get(self.field_name) if self.field_name in available_fields else 'POI {}'.format(i + 1)
                poitype = feature.get(self.field_poitype)
                self.create_poi(feature_geom, name, poitype)

    def create_poi(self, geometry, name, poitype):
        poitype, created = POIType.objects.get_or_create(label=poitype)
        poi = POI.objects.create(name=name, type=poitype)
        if settings.TREKKING_TOPOLOGY_ENABLED:
            # Use existing topology helpers to transform a Point(x, y)
            # to a path aggregation (topology)
            geometry = geometry.transform(settings.API_SRID, clone=True)
            geometry.coord_dim = 2
            serialized = '{"lng": %s, "lat": %s}' % (geometry.x, geometry.y)
            topology = TopologyHelper.deserialize(serialized)
            # Move deserialization aggregations to the POI
            poi.mutate(topology)
        else:
            if geometry.geom_type != 'Point':
                raise TypeError
            poi.geom = Point(geometry.x, geometry.y, srid=settings.SRID)
            poi.save()
        return poi
